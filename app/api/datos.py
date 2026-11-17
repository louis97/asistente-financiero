"""Lectura de datos (producción o instantánea), descarga a demanda fuera de la piloto, caché y serie de precios.

La API NO reimplementa volatilidades, etiquetas ni percentiles: todo viene de `notebooks/comunes.py`.
"""
import json
import threading
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from app.api import config
import comunes as cm   # noqa: E402

ARCHIVOS_REQUERIDOS = ["precios_diarios", "precios_semanales", "ratios_ttm"]
PILOTO = cm.tickers()
INICIO_LUNES = (pd.Timestamp(cm.INICIO) + pd.offsets.Week(weekday=0)).strftime("%Y-%m-%d")   # como nb01: barras semanales de lunes, alineadas con SPY y XLP
REFERENCIAS = [cm.BENCHMARK, cm.ETF_SECTOR["consumo_defensivo"]]       # SPY y XLP: no son piloto aunque estén en los parquet


class ErrorDescarga(Exception):
    """No hay ni precio para el ticker (502)."""


@dataclass
class DatosTicker:
    ticker: str
    precio: float
    fecha_dato: pd.Timestamp
    panel: pd.DataFrame                  # diario: fecha, ticker, close, r, abs_r, sigma20, sigma252, sigma20_sigma252
    semanal: pd.Series                   # cierre semanal ajustado por dividendos (índice fecha)
    ratios: pd.DataFrame | None          # ratios TTM del ticker, ya ajustados por splits (None si no hay)
    en_piloto: bool
    advertencias: list[str] = field(default_factory=list)
    fuente_datos: str = "snapshot"
    multiplos: pd.DataFrame | None = None        # semanal: close sin dividendos, pe, pe_norm, pb (None si no hay EPS)
    sector: pd.Series | None = None              # cierre semanal del XLP (piloto) o del SPY (fuera de la piloto)
    spy: pd.Series | None = None
    descargado_en: float = 0.0


# ------------------------------------------------------------------ fuente de datos (parquet)
def _fuente() -> tuple:
    """(carpeta, 'produccion' | 'snapshot'): producción solo si existe y tiene los tres parquet requeridos."""
    d = config.DATA_DIR
    if d.is_dir() and all((d / f"{a}.parquet").exists() for a in ARCHIVOS_REQUERIDOS):
        return d, "produccion"
    return config.DIR_SNAPSHOTS, "snapshot"


def _firma(carpeta) -> tuple:
    """Cambia cuando cambia la fecha de modificación de estado.json (o del parquet diario si no hay estado.json)."""
    ref = carpeta / "estado.json"
    if not ref.exists():
        ref = carpeta / "precios_diarios.parquet"
    return (str(carpeta), ref.stat().st_mtime_ns)


def _leer(nombre: str, carpeta) -> pd.DataFrame:
    """Un parquet de la carpeta; si no está (precios sin dividendos y splits no están en producción) el de la instantánea."""
    ruta = carpeta / f"{nombre}.parquet"
    return pd.read_parquet(ruta if ruta.exists() else config.DIR_SNAPSHOTS / f"{nombre}.parquet")


def _leer_estado(carpeta) -> dict:
    try:
        return json.loads((carpeta / "estado.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


class _Almacen:
    """Datos de la piloto en memoria: una carga, y recarga si cambia la firma."""

    def __init__(self):
        self.lock = threading.RLock()
        self.firma = None
        self.fuente = "snapshot"
        self.estado: dict = {}
        self.panel: dict[str, pd.DataFrame] = {}
        self.semanal = pd.DataFrame()
        self.ratios: dict[str, pd.DataFrame] = {}
        self.multiplos: dict[str, pd.DataFrame] = {}
        self.ultimo_dato = None

    def asegurar(self):
        carpeta, fuente = _fuente()
        firma = _firma(carpeta)
        with self.lock:
            if firma == self.firma:
                return
            diarios = _leer("precios_diarios", carpeta)
            panel = cm.construir_panel_diario(diarios)
            self.panel = {t: g.reset_index(drop=True) for t, g in panel.groupby("ticker")}
            self.semanal = cm.a_ancho(_leer("precios_semanales", carpeta))
            ttm, splits = _leer("ratios_ttm", carpeta), _leer("splits", carpeta)
            sd = _leer("precios_semanales_sd", carpeta)
            self.ratios, self.multiplos = {}, {}
            for t in PILOTO:
                rt = ttm[ttm.ticker == t]
                if rt.empty:
                    continue
                self.ratios[t] = cm.ajustar_por_splits(rt, splits[splits.ticker == t])
                self.multiplos[t] = cm.multiplos_semanales(sd[sd.ticker == t], self.ratios[t])
            self.estado, self.fuente = _leer_estado(carpeta), fuente
            self.ultimo_dato = diarios["fecha"].max()
            self.firma = firma


_almacen = _Almacen()
_cache_demanda: dict[str, DatosTicker] = {}
_candados: dict[str, threading.Lock] = {}
_candados_lock = threading.Lock()


def precalentar():
    _almacen.asegurar()


# ------------------------------------------------------------------ construcción de DatosTicker
def _advertencias_fuente(adv: list[str]):
    ok = _almacen.estado.get("fuentes_ok")
    malo = (ok is False) or (isinstance(ok, dict) and not all(ok.values()))
    if malo:
        adv.append(f"datos del {_almacen.ultimo_dato.date()}: la actualización falló")


def _ns(serie: pd.Series) -> pd.Series:
    """Índice en datetime64[ns] (los parquet vienen en ms y yfinance en ns) para alinear fechas sin sorpresas."""
    out = serie.copy()
    out.index = pd.DatetimeIndex(out.index).astype("datetime64[ns]")
    return out


def _ref_semanal(nombre: str) -> pd.Series:
    return _ns(_almacen.semanal[nombre].dropna())


def _armar(t: str, diario: pd.DataFrame, semanal: pd.Series, ratios, multiplos, adv: list[str],
           fuente: str, en_piloto: bool) -> DatosTicker:
    panel = diario.reset_index(drop=True)
    if len(panel) < cm.SIGMA_VENTANA_D + 1:
        adv.append("historia insuficiente: sin lectura técnica ni simulación")
    sector = _ref_semanal("XLP") if en_piloto else _ref_semanal("SPY")
    return DatosTicker(ticker=t, precio=float(panel["close"].iloc[-1]), fecha_dato=pd.Timestamp(panel["fecha"].iloc[-1]),
                       panel=panel, semanal=_ns(semanal), ratios=ratios, en_piloto=en_piloto, advertencias=adv,
                       fuente_datos=fuente, multiplos=multiplos, sector=sector, spy=_ref_semanal("SPY"),
                       descargado_en=time.time())


def _desde_parquet(t: str) -> DatosTicker:
    a = _almacen
    adv: list[str] = []
    _advertencias_fuente(adv)
    ratios, mult = a.ratios.get(t), a.multiplos.get(t)
    if t in REFERENCIAS:                      # SPY y XLP: solo precios, sin EPS ni validación de industria
        adv += ["industria no validada: las probabilidades no fueron validadas en esta industria",
                "referencia sectorial: SPY", "P/E no calculable: utilidad por acción no positiva o no publicada"]
    elif ratios is None:
        adv.append("P/E no calculable: utilidad por acción no positiva o no publicada")
    return _armar(t, a.panel[t], a.semanal[t].dropna(), ratios, mult, adv, a.fuente, en_piloto=t in PILOTO)


def _descargar_largo(simbolo: str, intervalo: str, ajuste: bool) -> pd.DataFrame | None:
    """Una descarga de yfinance con `comunes.descargar_precios`; None si no trae precios o falla."""
    try:
        largo, faltantes = cm.descargar_precios([simbolo], INICIO_LUNES if intervalo == "1wk" else cm.INICIO, intervalo,
                                                ajuste_dividendos=ajuste)
        return None if faltantes or largo.empty else largo
    except Exception:
        return None


def _splits_yf(t: str) -> pd.DataFrame:
    import yfinance as yf
    s = yf.Ticker(t).splits
    return pd.DataFrame({"ticker": t, "fecha": pd.to_datetime(s.index).tz_localize(None), "ratio": s.to_numpy(dtype=float)})


def _descargar_ticker(t: str) -> DatosTicker:
    """Descarga a demanda (fuera de la piloto): precios, y EPS/BVPS de EDGAR si hay SEC_USER_AGENT."""
    _almacen.asegurar()
    adv = ["industria no validada: las probabilidades no fueron validadas en esta industria",
           "referencia sectorial: SPY"]
    dia = _descargar_largo(t, "1d", True)
    if dia is None:
        raise ErrorDescarga(f"No se pudo descargar {t}")
    dia = dia.assign(fecha=dia["fecha"].astype("datetime64[ns]"))
    panel = cm.construir_panel_diario(dia)
    sem = _descargar_largo(t, "1wk", True)
    if sem is None:                                      # semanal derivado del diario (cierre de cada semana, fechada el lunes)
        d = dia.set_index("fecha")["close"]
        semanal = d.groupby(d.index.to_period("W-SUN").start_time).last()
        adv.append("serie semanal derivada de la diaria: la descarga semanal falló")
    else:
        semanal = sem.set_index(sem["fecha"].astype("datetime64[ns]"))["close"]
    ratios = mult = None
    if t in REFERENCIAS:
        adv.append("P/E no calculable: utilidad por acción no positiva o no publicada")
    elif not config.SEC_USER_AGENT:
        adv.append("sin utilidad por acción: falta configuración")
    else:
        try:
            hechos = cm.descargar_hechos_edgar([t])
            r = cm.construir_ratios_ttm(hechos)
            try:
                sp = _splits_yf(t)
            except Exception:
                sp = pd.DataFrame(columns=["ticker", "fecha", "ratio"])
                adv.append("P/E sin ajuste por splits: no se pudieron consultar")
            ratios = cm.ajustar_por_splits(r, sp)
            sd = _descargar_largo(t, "1wk", False)
            if sd is not None:
                mult = cm.multiplos_semanales(sd.assign(fecha=sd["fecha"].astype("datetime64[ns]")), ratios)
            else:
                adv.append("sin historia de múltiplos: falló la descarga de precios semanales sin dividendos")
        except Exception:
            ratios = mult = None
            adv.append("sin utilidad por acción: no se pudo consultar EDGAR")
    return _armar(t, panel, semanal, ratios, mult, adv, "snapshot" if _almacen.fuente == "snapshot" else "produccion", False)


def cargar_ticker(ticker: str) -> DatosTicker:
    """Datos de un ticker. Piloto: de los parquet; fuera de ella: descarga a demanda con caché de 24 h."""
    ticker = ticker.upper()
    if ticker in PILOTO or ticker in REFERENCIAS:
        _almacen.asegurar()
        return _desde_parquet(ticker)
    with _candados_lock:
        candado = _candados.setdefault(ticker, threading.Lock())
    with candado:
        previo = _cache_demanda.get(ticker)
        if previo and time.time() - previo.descargado_en < config.CACHE_HORAS * 3600:
            return previo
        try:
            nuevo = _descargar_ticker(ticker)
        except ErrorDescarga:
            if previo:                                    # descarga fallida: se sirve lo último, avisando
                copia = DatosTicker(**{**previo.__dict__, "advertencias": list(previo.advertencias)})
                copia.advertencias.append(f"datos del {previo.fecha_dato.date()}: la actualización falló")
                return copia
            raise
        _cache_demanda[ticker] = nuevo
        return nuevo


def serie(ticker: str) -> dict:
    """{fechas, cierres}: cierres diarios de las últimas ≈ 1260 sesiones (5 años) del panel."""
    d = cargar_ticker(ticker)
    p = d.panel.tail(config.SESIONES_SERIE)
    return {"fechas": [f.date().isoformat() for f in p["fecha"]], "cierres": [float(c) for c in p["close"]],
            "fuente_datos": d.fuente_datos}


# ------------------------------------------------------------------ /estado (sin modelo ni parquet pesados)
_cache_estado: dict = {"firma": None, "valor": None}


def estado() -> dict:
    """Fecha del último dato y del último recálculo, y de dónde se lee. Nunca lanza."""
    try:
        carpeta, fuente = _fuente()
        firma = _firma(carpeta)
    except Exception:
        return {"ultimo_dato": None, "ultimo_recalculo": None, "fuente_datos": "snapshot", "tickers_piloto": PILOTO}
    if _cache_estado["firma"] != firma:
        est = _leer_estado(carpeta)
        ultimo_dato, recalculo = est.get("ultimo_dato"), est.get("ultimo_recalculo")
        try:
            if not ultimo_dato:
                ultimo_dato = str(pd.read_parquet(carpeta / "precios_diarios.parquet", columns=["fecha"])["fecha"].max().date())
            if not recalculo:                              # instantánea: la fecha de descarga de su meta.json
                meta = json.loads((carpeta / "precios_diarios.meta.json").read_text(encoding="utf-8"))
                recalculo = meta.get("fecha_descarga")
        except Exception:
            pass
        _cache_estado.update(firma=firma, valor={"ultimo_dato": ultimo_dato, "ultimo_recalculo": recalculo, "fuente_datos": fuente})
    return {**_cache_estado["valor"], "tickers_piloto": PILOTO}


# ------------------------------------------------------------------ fuente de dato para pruebas de percentiles
def multiplos_piloto() -> dict[str, pd.DataFrame]:
    _almacen.asegurar()
    return _almacen.multiplos
