"""Dashboard del asistente (Streamlit). Se ejecuta desde la raíz: `streamlit run app/dashboard/app.py`."""
import sys, pathlib  # noqa: E401
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import os

import streamlit as st

from app.dashboard.cliente import Cliente, ErrorAcceso, ErrorServicio, ErrorValidacion
from app.dashboard.secciones import (avisos, banner, edicion_niveles, encabezado, franja_glosario, grafico_niveles,
                                     notas_fundamental, panel_riesgo, pie, recuadro_desempeno, registro_decisiones,
                                     tabla_niveles)

PCT_EJEMPLO = [-0.20, -0.12, -0.04, 0.08, 0.16, 0.28]     # niveles iniciales: ejemplo, no es una sugerencia
ss = st.session_state


def leer_api_url() -> str:
    if os.environ.get("API_URL"):
        return os.environ["API_URL"]
    try:
        return st.secrets["API_URL"]
    except Exception:                                      # sin secrets.toml
        return "http://localhost:8000"


def cliente() -> Cliente:
    return Cliente(leer_api_url(), ss.get("alias", ""), ss.get("codigo", ""))


def _pedir_calculo():
    otro = (ss.get("ticker_otro") or "").strip().upper()
    ss["pedido"] = otro or ss.get("ticker")


def _reintentar():
    ss.pop("estado", None)
    ss["pedido"] = ss.get("ultimo_pedido")


def _cerrar_sesion():
    ss["alias"], ss["codigo"] = "", ""
    if "res" in ss:
        ss["res"]["acceso"] = "sin_sesion"


def mostrar_fallo(e: ErrorServicio):
    if e.sin_contacto:
        st.error("No se pudo contactar con el servicio. Intenta de nuevo en un minuto.")
        st.caption("La API (Render) y el dashboard (Streamlit Cloud) gratuitos se duermen si no se usan y pueden tardar "
                   "cerca de 1 minuto en responder la primera vez.")
    else:
        st.error(e.mensaje)
    st.button("Reintentar", on_click=_reintentar)


def calcular(ticker: str):
    """Pide serie, niveles guardados (si hay sesión), lecturas, riesgo y modelo; deja el resultado en session_state."""
    ss["ultimo_pedido"] = ticker
    ss.pop("fallo", None)
    ss.pop("err_niveles", None)
    ss.pop("ok_niveles", None)
    c = cliente()
    alias = (ss.get("alias") or "").strip()
    try:
        with st.spinner("Calculando…"):
            serie = c.serie(ticker)
            precio = serie["cierres"][-1]
            acceso, guardados, avisos_ = ("ok" if alias else "sin_sesion"), None, []
            if alias:
                try:
                    guardados = c.niveles(ticker)
                except ErrorAcceso:
                    acceso = "invalido"
                except ErrorServicio as e:
                    if e.sin_contacto:
                        raise
                    avisos_.append("No se pudieron leer tus niveles guardados: " + e.mensaje)
            ejemplo = [{"valor": round(precio * (1 + p), 2), "unidad": "precio"} for p in PCT_EJEMPLO]
            ent, sal, origen = ejemplo[:3], ejemplo[3:], "ejemplo"
            if guardados:
                ent, sal, origen = guardados["entradas"], guardados["salidas"], "guardados"
            try:
                lec = c.lecturas(ticker, ent, sal)
            except ErrorValidacion:
                if origen != "guardados":
                    raise
                avisos_.append("Tus niveles guardados ya no son coherentes con el precio actual; se muestran los de ejemplo.")
                ent, sal, origen = ejemplo[:3], ejemplo[3:], "ejemplo"
                lec = c.lecturas(ticker, ent, sal)
            res = {"ticker": ticker, "lecturas": lec, "serie": serie, "riesgo": c.riesgo(ticker), "modelo": c.modelo(),
                   "entradas": ent, "salidas": sal, "origen": origen, "acceso": acceso, "avisos": avisos_}
    except ErrorValidacion as e:
        ss.pop("res", None)
        ss["fallo"] = ErrorServicio(e.detalle)
        return
    except ErrorServicio as e:
        ss.pop("res", None)
        ss["fallo"] = e
        return
    for i, n in enumerate(ent + sal):                       # valores iniciales del formulario de edición
        ss[f"nv_valor_{i}"], ss[f"nv_unidad_{i}"] = float(n["valor"]), n["unidad"]
    ss["res"] = res


st.set_page_config(page_title="Asistente bursátil", layout="wide")
banner()

# ---- estado del servicio (primera llamada: puede despertar la API)
if "estado" not in ss:
    try:
        with st.spinner("Despertando el servicio…"):
            ss["estado"] = cliente().estado(primera_vez=True)
    except ErrorServicio as e:
        mostrar_fallo(e)
        st.stop()
estado = ss["estado"]

# ---- barra lateral
with st.sidebar:
    st.header("Tu sesión")
    st.text_input("Alias", key="alias")
    st.text_input("Código", key="codigo", type="password")
    st.button("Cerrar sesión", on_click=_cerrar_sesion)
    st.header("Ticker")
    piloto = estado["tickers_piloto"]
    st.selectbox("Ticker de la industria piloto", piloto, index=piloto.index("KO") if "KO" in piloto else 0, key="ticker",
                 help="Las 21 empresas de consumo defensivo validadas. Para otro ticker, escríbelo abajo.")
    st.text_input("O escribe otro ticker (industria no validada)", key="ticker_otro", max_chars=6)
    st.button("Calcular", type="primary", on_click=_pedir_calculo)
    st.caption("Sin alias puedes ver lecturas, riesgo y gráfico; con alias también guardas niveles y decisiones.")

if ss.get("pedido"):
    calcular(ss.pop("pedido"))

# ---- cuerpo
franja_glosario()
if ss.get("fallo"):
    mostrar_fallo(ss["fallo"])
res = ss.get("res")
if res:
    encabezado(res)
    avisos(res)
    tabla_niveles(res)
    izq, der = st.columns([1.6, 1])
    with izq:
        grafico_niveles(res)
    with der:
        panel_riesgo(res["riesgo"])
    izq, der = st.columns([1, 1])
    with izq:
        notas_fundamental(res)
    with der:
        recuadro_desempeno(res["modelo"])
    edicion_niveles(res, cliente)
    registro_decisiones(res, cliente)
elif not ss.get("fallo"):
    st.info("Elige un ticker en la barra lateral y pulsa Calcular.")
pie(res, estado)
