"""API del asistente: lecturas por nivel, riesgo, serie, modelo, decisiones y niveles del usuario."""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as TiempoAgotado
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import config, datos, niveles
from app.api import modelo as md
from app.api.acceso import usuario_actual
from app.api.db import ErrorBaseDatos, obtener_repositorio
from app.api.esquemas import (Decision, DecisionGuardada, Estado, NivelesUsuario, PedidoLecturas, Riesgo,
                              RespuestaLecturas, Serie, validar_ticker_ruta)

log = logging.getLogger("api")
_pool_ping = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ping")


@asynccontextmanager
async def ciclo(app: FastAPI):
    md.cargar_modelo()                                              # si el modelo no coincide con comunes.py o con scikit-learn, el arranque se detiene
    threading.Thread(target=_calentar, daemon=True).start()         # los parquet se cargan en segundo plano: /estado no los necesita
    yield


def _calentar():
    try:
        datos.precalentar()
    except Exception:
        log.exception("No se pudo precalentar los datos")


app = FastAPI(title="Asistente bursátil: API", version="1.0", lifespan=ciclo)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])


# ------------------------------------------------------------------ errores
def _mensaje(e: dict) -> str:
    loc = [str(x) for x in e["loc"] if x not in ("body", "path", "query")]
    campo = ".".join(loc)
    tipo = e["type"]
    if tipo == "greater_than":
        return f"El valor de «{campo}» debe ser mayor que 0"
    if tipo in ("too_short", "too_long"):
        return f"Se requieren exactamente 3 niveles en «{campo}»"
    if tipo == "literal_error":
        return f"La unidad de «{campo}» debe ser «precio» o «pe»"
    if tipo == "string_pattern_mismatch":
        return "El ticker debe tener de 1 a 6 caracteres: letras mayúsculas, punto o guion"
    if tipo == "missing":
        return f"Falta el campo «{campo}»"
    return f"«{campo}»: {e['msg']}"


@app.exception_handler(RequestValidationError)
async def _validacion(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "; ".join(_mensaje(e) for e in exc.errors())})


@app.exception_handler(ValueError)
async def _valor(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(ErrorBaseDatos)
async def _bd(_: Request, exc: ErrorBaseDatos):
    return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible"})


@app.exception_handler(datos.ErrorDescarga)
async def _descarga(_: Request, exc: datos.ErrorDescarga):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def _inesperado(_: Request, exc: Exception):
    log.exception("Error no previsto", exc_info=exc)                # la traza queda en el log, no en la respuesta
    return JSONResponse(status_code=500, content={"detail": "Error interno"})


# ------------------------------------------------------------------ rutas abiertas
def _ping_con_limite() -> bool:
    try:
        return bool(_pool_ping.submit(obtener_repositorio().ping).result(timeout=config.LIMITE_PING_S))
    except (TiempoAgotado, Exception):
        return False


@app.get("/estado", response_model=Estado)
def get_estado():
    return {**datos.estado(), "supabase_ok": _ping_con_limite()}


@app.get("/serie/{ticker}", response_model=Serie)
def get_serie(ticker: str):
    return datos.serie(validar_ticker_ruta(ticker))


@app.post("/lecturas", response_model=RespuestaLecturas)
def post_lecturas(pedido: PedidoLecturas):
    return niveles.calcular_lecturas(datos.cargar_ticker(pedido.ticker), pedido)


@app.get("/riesgo/{ticker}", response_model=Riesgo)
def get_riesgo(ticker: str):
    return niveles.calcular_riesgo(datos.cargar_ticker(validar_ticker_ruta(ticker)))


@app.get("/modelo")
def get_modelo():
    return md.cargar_modelo()[1]


# ------------------------------------------------------------------ rutas protegidas
@app.get("/decisiones", response_model=list[DecisionGuardada])
def get_decisiones(alias: str = Depends(usuario_actual)):
    return obtener_repositorio().listar_decisiones(alias)


@app.post("/decisiones", response_model=DecisionGuardada)
def post_decisiones(d: Decision, alias: str = Depends(usuario_actual)):
    return obtener_repositorio().crear_decision(alias, d.ticker, d.nivel, d.lectura, d.nota)


@app.get("/niveles/{ticker}")
def get_niveles(ticker: str, alias: str = Depends(usuario_actual)):
    return obtener_repositorio().leer_niveles(alias, validar_ticker_ruta(ticker))      # sin filas: 200 con null


@app.put("/niveles/{ticker}")
def put_niveles(ticker: str, n: NivelesUsuario, alias: str = Depends(usuario_actual)):
    t = validar_ticker_ruta(ticker)
    d = datos.cargar_ticker(t)
    eps = niveles._valor_a_fecha(d, "eps_ttm", d.fecha_dato)
    niveles.validar_coherencia([niveles.a_precio(x, eps, d.precio) for x in n.entradas],
                               [niveles.a_precio(x, eps, d.precio) for x in n.salidas], d.precio)
    return obtener_repositorio().guardar_niveles(alias, t, [x.model_dump() for x in n.entradas], [x.model_dump() for x in n.salidas])
