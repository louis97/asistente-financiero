"""Lo que comparten dos o más notebooks, la API y la tarea diaria: universo, conceptos y ratios de EDGAR, rutas,
carga de instantáneas, los dos bootstrap y (sección "Entrega 2") las constantes y funciones del modelo técnico.

Todo lo demás vive dentro de cada notebook, junto a su explicación.
"""
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf

# Universo (R5, E5): 21 empresas de la industria piloto, consumo defensivo (en el XLP y con historia desde 2009;
# KHC queda fuera porque cotiza desde 2015). El producto sirve para cualquier industria; agregar otra es
# agregar una clave aquí y su ETF.
UNIVERSO = {
    "consumo_defensivo": ["KO", "PEP", "PG", "WMT", "COST", "CL", "MDLZ", "KMB", "GIS",
                          "MO", "PM", "HSY", "KR", "SYY", "ADM", "CLX", "CHD", "MKC", "STZ", "CAG", "TSN"],
}
ETF_SECTOR = {"consumo_defensivo": "XLP"}  # benchmark del sector
BENCHMARK = "SPY"          # mercado
INICIO = "2009-01-01"      # inicio de la historia descargada

# Conceptos de EDGAR (10-K y 10-Q): nombre → (nombres XBRL alternativos en orden de preferencia, unidad).
# Una empresa puede reportar el mismo concepto con otro nombre; un concepto ausente es NaN, nunca 0 (T2).
# Los usan nb01 (tabla anual) y nb02 (completitud concepto × ticker y A1).
CONCEPTOS = {
    "ingresos": (["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                  "SalesRevenueGoodsNet"], "USD"),   # SalesRevenueGoodsNet: CAG, CHD, GIS, KO, KR, STZ y SYY hasta 2018
    "utilidad_operativa": (["OperatingIncomeLoss"], "USD"),
    "utilidad_neta": (["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"], "USD"),
    "patrimonio": (["StockholdersEquity",
                    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "USD"),
    "deuda_lp": (["LongTermDebt", "LongTermDebtNoncurrent",
                  "LongTermDebtAndCapitalLeaseObligations"], "USD"),   # deuda de LP no corriente con arrendamientos: TSN, SYY, PM, KMB, MDLZ, PEP
    "acciones": (["WeightedAverageNumberOfDilutedSharesOutstanding",
                  "WeightedAverageNumberOfSharesOutstandingBasic",
                  "WeightedAverageNumberOfShareOutstandingBasicAndDiluted"], "shares"),   # MO 2011–2020 y PM 2012–2016
    # D1: EPS reportado, solo para las acciones implícitas (utilidad neta ÷ EPS) cuando faltan las acciones (STZ, HSY)
    "eps_reportado": (["EarningsPerShareDiluted", "EarningsPerShareBasic",
                       "EarningsPerShareBasicAndDiluted"], "USD/shares"),   # MO 2011–2020
}

# Los 5 ratios: nombre → (numerador, denominador). A1: cada ratio se fecha con la publicación
# más tardía de SUS dos conceptos. Los usan nb01 (cálculo) y nb02 (temporalidad A1 y triangulación).
RATIOS = {
    "eps": ("utilidad_neta", "acciones"),               # utilidad por acción (base del P/E)
    "bvps": ("patrimonio", "acciones"),                 # valor en libros por acción (base del P/B)
    "roe": ("utilidad_neta", "patrimonio"),             # rentabilidad del patrimonio
    "margen_operativo": ("utilidad_operativa", "ingresos"),
    "deuda_patrimonio": ("deuda_lp", "patrimonio"),     # deuda de largo plazo frente al patrimonio
}

RAIZ = Path(__file__).resolve().parents[1]
DIR_SNAPSHOTS = RAIZ / "data" / "snapshots"
DIR_ASSETS = RAIZ / "entregables" / "entrega_1" / "assets"


def tickers() -> list[str]:
    """Las 21 empresas de la industria piloto, en el orden de UNIVERSO."""
    return [t for lista in UNIVERSO.values() for t in lista]


def cargar_snapshot(nombre: str) -> pd.DataFrame:
    """Lee una instantánea fechada de data/snapshots (los notebooks después del 01 no descargan nada)."""
    return pd.read_parquet(DIR_SNAPSHOTS / f"{nombre}.parquet")


def a_ancho(df_largo: pd.DataFrame, campo: str = "close") -> pd.DataFrame:
    """Formato largo (fecha, ticker, campo) → ancho (filas = fechas, columnas = tickers)."""
    return df_largo.pivot(index="fecha", columns="ticker", values=campo).sort_index()


def ic_bootstrap_fechas(df, estadistico, bloque, reps=1000, semilla=42, col_fecha="fecha", nivel=0.95,
                        devolver_reps=False):
    """IC por bootstrap por BLOQUES de fechas consecutivas (Künsch 1989; Politis y Romano 1994).

    Toma tramos de `bloque` fechas seguidas, en su orden original, con todas las acciones de esas
    fechas juntas: conserva la dependencia en el tiempo y entre acciones (las crisis las mueven a todas).
    Devuelve (estimación con todos los datos, límite inferior, límite superior).

    Con `devolver_reps=True` devuelve también el arreglo de las `reps` réplicas del estadístico
    (compatible hacia atrás: por defecto el resultado no cambia). Se usa, por ejemplo, para el
    p-value bootstrap unilateral de percentil p = (1 + #réplicas del lado del nulo) / (1 + reps),
    coherente con el IC de percentil al 1 − 2α (p < α ⇔ el nulo queda fuera del IC).
    """
    fechas = np.sort(df[col_fecha].unique())
    nf = len(fechas)
    if bloque > nf:
        raise ValueError(f"El bloque ({bloque}) es mayor que el número de fechas ({nf}).")
    filas = df.groupby(col_fecha).indices                    # fecha → posiciones de sus filas
    rng = np.random.default_rng(semilla)
    nbl = int(np.ceil(nf / bloque))                          # bloques necesarios para cubrir la serie
    vals = np.empty(reps)
    for r in range(reps):
        inicios = rng.integers(0, nf - bloque + 1, nbl)      # dónde empieza cada tramo
        fs = np.concatenate([fechas[i:i + bloque] for i in inicios])[:nf]
        vals[r] = estadistico(df.iloc[np.concatenate([filas[f] for f in fs])])
    q = (1 - nivel) / 2 * 100
    lo, hi = np.nanpercentile(vals, [q, 100 - q])
    if devolver_reps:
        return float(estadistico(df)), float(lo), float(hi), vals
    return float(estadistico(df)), float(lo), float(hi)


def ic_bootstrap_grupos(df, estadistico, col_grupo="ticker", reps=1000, semilla=42, nivel=0.95,
                        devolver_reps=False):
    """IC por bootstrap por GRUPOS (cluster bootstrap; Cameron, Gelbach y Miller 2008).

    Remuestrea grupos completos (p. ej., cada acción con toda su historia, en orden) con reemplazo.
    Se usa cuando el estimando es "la empresa típica" (un valor por empresa).

    Con `devolver_reps=True` devuelve también el arreglo de las `reps` réplicas del estadístico
    (compatible hacia atrás: por defecto el resultado no cambia). Permite calcular el p-value
    bootstrap unilateral de percentil p = (1 + #réplicas del lado del nulo) / (1 + reps),
    coherente con el IC de percentil al 1 − 2α (p < α ⇔ el nulo queda fuera del IC).
    """
    grupos = df[col_grupo].unique()
    if len(grupos) < 2:
        raise ValueError("Se necesitan al menos 2 grupos para el bootstrap por grupos.")
    filas = df.groupby(col_grupo).indices
    rng = np.random.default_rng(semilla)
    vals = np.empty(reps)
    for r in range(reps):
        g = rng.choice(grupos, size=len(grupos), replace=True)
        vals[r] = estadistico(df.iloc[np.concatenate([filas[x] for x in g])])
    q = (1 - nivel) / 2 * 100
    lo, hi = np.nanpercentile(vals, [q, 100 - q])
    if devolver_reps:
        return float(estadistico(df)), float(lo), float(hi), vals
    return float(estadistico(df)), float(lo), float(hi)


# =====================================================================================================
# Entrega 2: constantes, rutas y funciones compartidas por los notebooks 01–08, la API y la tarea diaria
# (firmas y valores: una sola fuente; lo que se movió de los notebooks 01–04 no cambió su cuerpo).
# =====================================================================================================

# --- Rutas de la entrega 2 ---
DIR_RESULTADOS = RAIZ / "data" / "resultados"          # JSON con las cifras de cada notebook
DIR_PRODUCCION = RAIZ / "data" / "produccion"          # datos que actualiza la tarea diaria
DIR_MODELO = RAIZ / "app" / "modelo"                   # modelo entrenado y su metadata
DIR_ASSETS_E2 = RAIZ / "entregables" / "entrega_2" / "assets"   # figuras de la entrega 2

# --- Modelo técnico (contratos §1) ---
N_DIAS = 60                          # horizonte de la etiqueta de entrada: 60 sesiones (3 meses bursátiles; nb04 §4)
K_GRID = (0.5, 1.0, 1.5, 2.0)        # distancias a la barrera inferior, en σ·√N, con las que se entrena el modelo
K_SUP = 1.0                          # barrera superior fija (la misma de la entrega 1)
PASO_SUBMUESTRA = 5                  # una fila cada 5 sesiones por ticker para entrenar: SVM entrenable y menos solapamiento
SIGMA_VENTANA_D = 252                # días hábiles para σ252 (un año bursátil; convención)
SIGMA_CORTA_D = 20                   # días hábiles para σ20 (un mes bursátil)
BRECHA = 60                          # sesiones hábiles descartadas antes de cada frontera (spec §6: igual a N_DIAS, la etiqueta no cruza el corte)
FIN_ENTRENAMIENTO = "2014-12-31"     # spec §6: entrenamiento 2009–2014
INICIO_VALIDACION = "2015-01-01"     # spec §6: validación 2015–2018
FIN_VALIDACION = "2018-12-31"        # spec §6
INICIO_PRUEBA = "2019-01-01"         # spec §6: prueba 2019 en adelante, intocable hasta el final
ANIOS_VALIDACION = (2015, 2016, 2017, 2018)   # un BSS por año de validación (spec §6)
EMPATE_BSS = 0.005                   # diferencia de BSS por debajo de la cual dos candidatos se consideran empatados
DECILES_SIGMA = 10                   # grupos de σ252 para la línea base y la conservación de la partición
SEMILLA = 42                         # semilla reproducible para todo el proyecto
REPS_BOOT = 1000                     # réplicas del bootstrap (percentiles al 95 % ya estables)
BLOQUE_FECHAS = 60                   # bloque del bootstrap por fechas diarias: un trimestre bursátil
VARIABLES = ["abs_r", "sigma20_sigma252", "sigma252", "k"]   # las tres de magnitud de la entrega 1 más k
CRITERIOS_CONSERVACION = {"tasa_pp": 0.03, "mediana_sigma_rel": 0.20, "decil_pp": 0.05}   # tolerancias de la partición (spec §6)
SIM_BLOQUE_SEMANAS = 12              # bloque de la simulación: un trimestre, como el bloque de la entrega 1
SIM_REPS = 2000                      # réplicas de la simulación de salidas
SIM_REPS_RF11 = 500                  # réplicas de la simulación en el flujo de baja latencia (RF11)
SIM_HORIZONTE_SEMANAS = 52           # horizonte fijo de la simulación: un año

# --- Constantes que antes vivían en los notebooks y que usan las funciones movidas (mismos valores) ---
HIST_MIN_PERCENTIL = 52              # semanas mínimas para el percentil expansivo (un año bursátil)
ANTIGUEDAD_MAX = 548                 # días desde el cierre del último trimestre a partir de los cuales el dato es rancio
VENT_VOL_SEM = 52                    # semanas: ventana de la volatilidad móvil anualizada (un año bursátil)
UMBRAL_Z_P1 = 2.0                    # z < -2: convención de caída fuerte (una normal daría ~1 de cada 40 semanas)
DUR_TRIMESTRE = (80, 120)            # días de un trimestre fiscal: acepta trimestres de 12 o 16 semanas
DUR_ANUAL = (330, 400)               # días de un año fiscal: acepta años de 52 y 53 semanas
VENTANA_NORM = 12                    # trimestres (3 años) del EPS promedio anual, denominador del P/E normalizado
PAUSA_SEC = 0.15                     # segundos entre solicitudes: la SEC permite como máximo 10 por segundo
VENTANA_VECINOS = 400                # días alrededor de un cierre para comparar escala (~4 trimestres a cada lado)
MIN_VECINOS_ESCALA = 2               # vecinos publicados antes, mínimos para juzgar la escala; con menos no se corrige
TOLERANCIA_FECHA = 7                 # días: dos cierres (o inicios) a menos de una semana son el mismo período con otra fecha
TOL_LOG_ESCALA = 0.5                 # un monto se reescala solo si es 10^(6±0,5) veces menor que sus vecinos (escrito en millones)
ACCIONES_MIN = 1e7                   # acciones mínimas plausibles (la menor del universo ronda 1,2·10⁸): menos = miles o millones
ACCIONES_MAX = 1e11                  # acciones máximas plausibles (la mayor ronda 8·10⁹): más = unidad equivocada


# --- Múltiplos semanales y percentiles sin look-ahead (de nb04 §0.2) ---
def ajustar_por_splits(r, splits):
    """Lleva eps_ttm/bvps/eps_prom_3a a las acciones de hoy: divide por los splits posteriores a SU fecha de publicación.

    nb01 ya neutraliza los splits DENTRO de la ventana del eps_prom_3a (todos los trimestres se dividen por las
    acciones del último trimestre de la ventana), así que no hay doble división: aquí se corrigen solo los splits
    POSTERIORES a esa fecha, para alinear con el precio actual (sin dividendos, pero ajustado por splits).
    """
    out = r.copy()
    if splits is None or splits.empty:
        return out
    fechas = pd.to_datetime(splits["fecha"]).to_numpy()
    razones = splits["ratio"].to_numpy(dtype=float)
    for col in ("eps_ttm", "bvps", "eps_prom_3a"):
        factor = out[f"filed_{col}"].map(
            lambda f: 1.0 if pd.isna(f) else float(np.prod(razones[fechas > np.datetime64(f)])))
        out[col] = out[col] / factor
    return out


def ultimo_publicado(fechas_precio, r, col):
    """Para cada semana, el último valor de `col` ya publicado (filed_<col> ≤ fecha); empate → trimestre más reciente.

    #9 de los 10-Q (temporalidad): un dato de más de 548 días desde el cierre de su último trimestre es rancio → vacío.
    """
    f = (r[["end", col, f"filed_{col}"]].dropna(subset=[f"filed_{col}"])
           .sort_values([f"filed_{col}", "end"], kind="stable")
           .drop_duplicates(f"filed_{col}", keep="last"))
    m = pd.merge_asof(pd.DataFrame({"fecha": fechas_precio.astype("datetime64[ns]")}),
                      f.rename(columns={f"filed_{col}": "filed"})
                       .assign(filed=lambda d: d.filed.astype("datetime64[ns]"))
                       .assign(end=lambda d: d["end"].astype("datetime64[ns]")),
                      left_on="fecha", right_on="filed", direction="backward")
    rancio = (m["fecha"] - m["end"]).dt.days > ANTIGUEDAD_MAX
    return m[col].where(~rancio).to_numpy()


def multiplos_semanales(precios_sd, r, cols=("eps_ttm", "bvps", "eps_prom_3a", "roe_ttm",
                                             "margen_operativo_ttm", "deuda_patrimonio")):
    """Panel semanal por ticker: precio sin dividendos, P/E (EPS TTM), P/E normalizado (EPS promedio 3 años, R7),
    P/B, y ROE/margen/deuda como contexto. Cada columna llega con SU propio filed_<col> (sin look-ahead).
    EPS ≤ 0 → P/E sin sentido (ya vacío desde nb01)."""
    m = precios_sd[["fecha", "close"]].dropna().sort_values("fecha").reset_index(drop=True)
    for col in cols:
        m[col] = ultimo_publicado(m["fecha"].to_numpy("datetime64[ns]"), r, col)
    m["pe"]      = m["close"] / m["eps_ttm"].where(m["eps_ttm"] > 0)
    m["pe_norm"] = m["close"] / m["eps_prom_3a"].where(m["eps_prom_3a"] > 0)   # R7: "barata frente a su historia"
    m["pb"]      = m["close"] / m["bvps"].where(m["bvps"] > 0)
    return m


def percentil_expansivo(serie, min_obs=HIST_MIN_PERCENTIL):
    """Percentil del valor de hoy dentro de TODA su historia hasta hoy (no mira al futuro)."""
    def _pct(w):
        if np.isnan(w[-1]):
            return np.nan
        v = w[~np.isnan(w)]
        return float((v <= w[-1]).mean()) if len(v) else np.nan
    return serie.expanding(min_periods=min_obs).apply(_pct, raw=True)

# --- Etiqueta de entrada (de nb04 §4.1): la única que mira al futuro ---
def etiqueta_entrada(close, sigma, k_inf, k_sup, n):
    # Etiqueta de entrada (solo largo): en t miramos las n sesiones siguientes.
    # Si el precio toca primero el nivel inferior (precio_t · exp(-k_inf · σ · √n)) → etiqueta 1.
    # Si toca primero el nivel superior o se agotan las n sesiones → 0.
    # Un hueco de precio dentro de las n sesiones deja la etiqueta vacía (censura T3).
    import numpy as _np
    precios = close.to_numpy(dtype=float)
    sig = sigma.reindex(close.index).to_numpy(dtype=float)
    total = len(precios)
    etiqueta = _np.full(total, _np.nan)
    resultado = _np.full(total, None, dtype=object)
    sesiones = _np.full(total, _np.nan)
    for t in range(total):
        if t + n >= total or _np.isnan(sig[t]) or _np.isnan(precios[t]):
            continue
        ancho = sig[t] * _np.sqrt(n)
        inferior = precios[t] * _np.exp(-k_inf * ancho)
        superior = precios[t] * _np.exp( k_sup * ancho)
        etiqueta[t], resultado[t] = 0.0, "tiempo"
        for h in range(1, n + 1):
            p = precios[t + h]
            if _np.isnan(p):
                etiqueta[t], resultado[t], sesiones[t] = _np.nan, None, _np.nan
                break
            if p <= inferior:
                etiqueta[t], resultado[t], sesiones[t] = 1.0, "entrada", h
                break
            if p >= superior:
                etiqueta[t], resultado[t], sesiones[t] = 0.0, "escape", h
                break
    return pd.DataFrame({"etiqueta": etiqueta, "resultado": resultado, "sesiones": sesiones},
                        index=close.index)

# --- Riesgo (de nb03 §0): volatilidad, caída máxima, percentil y caídas fuertes ---
def vol_movil(r, ventana=VENT_VOL_SEM, periodos=VENT_VOL_SEM):
    """Volatilidad móvil anualizada: desviación de las `ventana` observaciones hasta t (no mira al futuro)."""
    return r.rolling(ventana, min_periods=ventana).std(ddof=1) * np.sqrt(periodos)

def max_drawdown(close):
    """Caída máxima desde el máximo previo; devuelve (peor caída en proporción, serie de caídas)."""
    serie = close / close.cummax() - 1
    return float(serie.min()), serie

def percentil_retorno(r, q=0.05):
    """Percentil del retorno; con q=0,05 es la semana 'mala' de 1 en 20."""
    return float(np.nanquantile(r, q))

def tasa_caidas_fuertes(r, k=UMBRAL_Z_P1, ventana=VENT_VOL_SEM):
    """Fracción de observaciones con caída mayor que k veces la volatilidad de las `ventana` ANTERIORES.

    La volatilidad se calcula con `shift(1)` para no usar la observación de hoy en el umbral de hoy.
    """
    z = (r / r.rolling(ventana, min_periods=ventana).std(ddof=1).shift(1)).dropna()
    return float((z < -k).mean()) if len(z) else float("nan")

# --- Descarga de precios (de nb01 §1) ---
COLUMNAS_PX = ["fecha", "ticker", "close", "volume"]


def a_formato_largo(raw, simbolos):
    """Salida de yf.download (columnas por símbolo) → formato largo; un símbolo sin precios se reporta como faltante."""
    partes = []
    for t in simbolos:
        if ("Close", t) not in raw.columns:
            continue
        partes.append(pd.DataFrame({"fecha": raw.index, "ticker": t, "close": raw[("Close", t)].to_numpy(),
                                    "volume": raw[("Volume", t)].to_numpy()}))
    largo = pd.concat(partes, ignore_index=True).dropna(subset=["close"]).reset_index(drop=True)
    return largo[COLUMNAS_PX], [t for t in simbolos if t not in set(largo.ticker)]


def descargar_precios(simbolos, inicio, intervalo, ajuste_dividendos=True):
    """Descarga precios; con ajuste_dividendos=False el cierre solo está ajustado por splits (precio pagado, para los múltiplos)."""
    import yfinance as yf
    raw = yf.download(simbolos, start=inicio, interval=intervalo, auto_adjust=ajuste_dividendos,
                      progress=False, group_by="column")
    return a_formato_largo(raw, simbolos)

# --- Descarga de hechos de EDGAR (de nb01 §3) ---
URL_TICKERS = "https://www.sec.gov/files/company_tickers.json"
URL_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

def descargar_json(url):
    """GET a la SEC con el User-Agent del entorno (requisito de la SEC) y una pausa para no pasar de 10 solicitudes/s."""
    agente = os.environ.get("SEC_USER_AGENT")
    if not agente:
        raise RuntimeError("Defina SEC_USER_AGENT en el entorno (requisito de la SEC)")
    time.sleep(PAUSA_SEC)
    r = requests.get(url, headers={"User-Agent": agente}, timeout=30); r.raise_for_status()
    return r.json()


def hechos_a_df(companyfacts):
    """JSON de companyfacts → tabla larga: una fila por hecho (concepto, unidad, período, valor, formulario, publicación)."""
    filas = [{"concepto": concepto, "unidad": unidad, "start": h.get("start"), "end": h.get("end"),
              "val": h.get("val"), "form": h.get("form"), "fp": h.get("fp"), "filed": h.get("filed")}
             for concepto, cont in companyfacts.get("facts", {}).get("us-gaap", {}).items()
             for unidad, hechos in cont.get("units", {}).items() for h in hechos]
    df = pd.DataFrame(filas, columns=["concepto", "unidad", "start", "end", "val", "form", "fp", "filed"])
    for c in ("start", "end", "filed"):
        df[c] = pd.to_datetime(df[c])
    return df

def descargar_hechos_edgar(tickers: list[str]) -> pd.DataFrame:
    """Hechos contables de EDGAR (companyfacts) de `tickers`, en tabla larga con la columna `ticker`.

    Exige SEC_USER_AGENT en el entorno (RuntimeError si falta). Una descarga parcial no se devuelve:
    si falla algún ticker se lanza RuntimeError, para no sobrescribir una instantánea completa.
    """
    ciks = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in descargar_json(URL_TICKERS).values()}
    nombres = [n for alt, _ in CONCEPTOS.values() for n in alt]
    partes, errores = [], {}
    for t in tickers:
        try:
            h = hechos_a_df(descargar_json(URL_FACTS.format(cik=ciks[t])))
            h = h[h.concepto.isin(nombres) | h.concepto.str.contains("LongTermDebt|OperatingIncome|EarningsPerShare|Revenue|SalesRevenue|WeightedAverageNumberOf")]
            partes.append(h.assign(ticker=t))
        except Exception as e:
            errores[t] = f"{type(e).__name__}: {str(e)[:80]}"
    print("errores:", errores or "ninguno")
    if errores:
        raise RuntimeError(f"Descarga de EDGAR incompleta para {sorted(errores)}; no se guarda nada")
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(
        columns=["concepto", "unidad", "start", "end", "val", "form", "fp", "filed", "ticker"])


# --- Tabla trimestral y ratios TTM (de nb01 §3.2 y §4) ---
def escala_acciones(v):
    """#11 para ACCIONES (regla absoluta, sin vecinos ni futuro): ninguna empresa del universo tiene menos de
    ACCIONES_MIN ni más de ACCIONES_MAX acciones. Un valor menor está en miles (×10³) o en millones (×10⁶);
    uno mayor, en una unidad 10³ veces más chica (÷10³). Devuelve (valor corregido, ¿se corrigió?)."""
    v = np.asarray(v, dtype=float).copy(); c = np.zeros(len(v), bool)
    for f in (1e6, 1e3):                                         # millones (KO, MDLZ) y miles (CLX, HSY)
        m = (v > 0) & (v < ACCIONES_MIN) & (v * f >= ACCIONES_MIN) & (v * f <= ACCIONES_MAX)
        v[m] *= f; c |= m
    m = v > ACCIONES_MAX; v[m] /= 1e3; c |= m
    return v, c

# Parte 1: serie trimestral de los FLUJOS (utilidad neta, ingresos, utilidad operativa, acciones y EPS reportado).
FLUJOS = ["utilidad_neta", "ingresos", "utilidad_operativa", "acciones", "eps_reportado"]
SALDOS = ["patrimonio", "deuda_lp"]

def primera_publicacion(d, claves):
    """#4: un período aparece de nuevo en reportes posteriores (comparativos o reexpresados).
    Se conserva la PRIMERA publicación (filed mínimo): lo que el inversor vio en su momento (sin look-ahead).
    Entre nombres XBRL publicados el mismo día gana el de mayor prioridad (orden de CONCEPTOS)."""
    d = d[d["filed"] >= d["end"]]                                  # publicado antes del cierre: imposible
    return d.sort_values(["filed", "prioridad"]).drop_duplicates(claves, keep="first")

def hechos_de(h, nombre):
    """Hechos de un concepto (con sus alternativas XBRL) en 10-Q y 10-K, nunca 8-K ni formularios corregidos (/A)."""
    alternativas, unidad = CONCEPTOS[nombre]
    d = h[h.concepto.isin(alternativas) & (h.unidad == unidad) & h.form.isin(["10-Q", "10-K"])].copy()
    d["prioridad"] = d["concepto"].map({c: i for i, c in enumerate(alternativas)})
    return corregir_escala(unificar_fechas(d))

def unificar_fechas(d):
    """#3: un mismo período a veces aparece con el cierre corrido 1 a 3 días (se usa una tolerancia de ±7 días como margen) (CHD 2010-04-02 en su 10-Q y 2010-03-31
    en los comparativos de un 10-K posterior). Las fechas a ±TOLERANCIA_FECHA días se tratan como el mismo
    cierre (o inicio) y toman la del dato publicado primero; así no se crean trimestres duplicados."""
    d = d.copy()
    for c in ("end", "start"):
        x = d[d[c].notna()].sort_values([c, "filed"])
        grupo = (x[c].diff().dt.days > TOLERANCIA_FECHA).cumsum()          # cierres a ≤ 7 días = mismo grupo
        canon = x.sort_values("filed").groupby(grupo)[c].transform("first")   # la fecha del primero publicado
        d.loc[x.index, c] = canon
    return d

def corregir_escala(d):
    """#11: errores de escala XBRL (KO y MDLZ reportaron acciones en millones; CLX y HSY, en miles; KMB, la
    utilidad en unidades). Se reescalan y se marcan con `escala_corregida`."""
    d = d.copy(); d["escala_corregida"] = False; d["escala_sin_vecinos"] = False
    val = d["val"].to_numpy(dtype=float).copy(); corr = np.zeros(len(d), bool); sinv = np.zeros(len(d), bool)
    if (d["unidad"] == "shares").all():                          # acciones: regla absoluta (ver escala_acciones)
        val, corr = escala_acciones(val)
        d["val"] = val; d["escala_corregida"] = corr
        return d
    # Montos en USD: se comparan con la mediana de sus VECINOS = mismo nombre XBRL, cierre a ±VENTANA_VECINOS días
    # y publicados ANTES que el valor (filed < su filed), ya corregidos y en orden de publicación: solo se usa lo
    # que se sabía entonces (sin look-ahead) y un error repetido no arrastra la mediana.
    # Solo se reescala por 10⁶ (monto escrito en millones sin su escala, KMB 2009–10) y si el cociente
    # mediana ÷ |valor| está cerca de 10⁶ (|log10(cociente) − 6| < TOL_LOG_ESCALA). No se reescala por 10³: un
    # trimestre real cercano al punto de equilibrio puede ser 100 a 1000 veces menor que lo típico (ADM 2009-03:
    # 3 M, cociente 10^2,4; SYY 2020-03: −3 M, 10^2,2; STZ 2021-08: 1,5 M, 10^2,8) y no se distingue de un error
    # de miles. Las acciones en miles se corrigen con la regla absoluta. Con menos de MIN_VECINOS_ESCALA vecinos no se corrige y se marca.
    fin = d["end"].to_numpy(); fil = d["filed"].to_numpy(); nom = d["concepto"].to_numpy()
    for i in np.argsort(fil, kind="stable"):
        v = (nom == nom[i]) & (np.abs((fin - fin[i]).astype("timedelta64[D]").astype(int)) <= VENTANA_VECINOS) & (fil < fil[i])
        if v.sum() < MIN_VECINOS_ESCALA:
            sinv[i] = True; continue
        med = np.median(np.abs(val[v]))
        if val[i] == 0 or med == 0:
            continue
        if abs(np.log10(med / abs(val[i])) - 6) < TOL_LOG_ESCALA:
            val[i] *= 1e6; corr[i] = True
    d["val"] = val; d["escala_corregida"] = corr; d["escala_sin_vecinos"] = sinv
    return d

def unir(partes, cols):
    """pandas 3: concatenar solo piezas no vacías y fijar los tipos (fechas y float)."""
    partes = [x for x in partes if len(x)]
    t = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=cols)
    for c in ("start", "end", "filed"):
        if c in t: t[c] = pd.to_datetime(t[c])
    if "val" in t: t["val"] = t["val"].astype(float)
    for c in ("escala_corregida", "escala_sin_vecinos"):
        if c in t: t[c] = t[c].fillna(False).astype(bool)
    return t


PRIORIDAD_ORIGEN = {"reportado": 0, "resta_ytd": 1, "q4_derivado": 2}   # desempate con el mismo `filed`

def primero_conocido(q):
    """#4: por cada `end` gana el dato publicado primero; si dos tienen el mismo `filed`, gana el reportado
    (luego la resta de acumulados y al final el Q4 derivado). Orden estable: el resultado no depende del azar."""
    q = q.assign(_p=q["origen"].map(PRIORIDAD_ORIGEN))
    q = q.sort_values(["filed", "_p"], kind="stable").drop_duplicates("end", keep="first")
    return q.drop(columns="_p")

def trimestres_flujo(h, nombre):
    """Un valor por trimestre fiscal (alineado por `end`, nunca por año calendario ni por "Q1–Q4", #3)."""
    d = hechos_de(h, nombre).dropna(subset=["start"])
    d["dur"] = (d["end"] - d["start"]).dt.days
    cols = ["start", "end", "val", "filed", "form", "escala_corregida", "escala_sin_vecinos"]
    # #1 y #8: dato de duración trimestral (80–120 días: acepta trimestres de 12 o 16 semanas y años de 53)
    q = primera_publicacion(d[d.dur.between(*DUR_TRIMESTRE)], ["end"])[cols].assign(origen="reportado")
    if nombre == "acciones":
        # Las acciones son un PROMEDIO, no se pueden restar. Para el cierre del año fiscal (sin 10-Q) se usa
        # el promedio anual del 10-K, el dato publicado más cercano (#6; se declara como precisión en nb02).
        a = primera_publicacion(d[d.dur.between(*DUR_ANUAL) & (d.form == "10-K")], ["end"])
        a = a[~a["end"].isin(q["end"])][cols].assign(origen="promedio_anual")
        return unir([q, a], cols + ["origen"]).sort_values("end")
    # #1: si solo hay acumulado del año (YTD de ~180 o ~270 días), trimestre = acumulado − acumulado anterior
    #     del MISMO año fiscal (misma `start`); Q1 es el acumulado de 3 meses de ese año.
    acum = primera_publicacion(d[d.dur.between(DUR_TRIMESTRE[0], DUR_ANUAL[0] - 1)], ["start", "end"])
    nuevos = []
    for s, g in acum.sort_values("end").groupby("start"):
        g = g.reset_index(drop=True)
        for i in range(1, len(g)):
            act, ant = g.iloc[i], g.iloc[i - 1]
            salto = (act["end"] - ant["end"]).days
            if not DUR_TRIMESTRE[0] <= salto <= DUR_TRIMESTRE[1]:
                continue                                   # los acumulados no son consecutivos
            nuevos.append({"start": ant["end"] + pd.Timedelta(days=1), "end": act["end"],
                           "val": act["val"] - ant["val"], "filed": max(act["filed"], ant["filed"]),  # el más tardío
                           "form": act["form"], "origen": "resta_ytd"})
    # #4: entre reportado y derivado del mismo `end`, gana el que se conoció primero (menor `filed`)
    q = unir([q, pd.DataFrame(nuevos, columns=cols + ["origen"])], cols + ["origen"])
    q = primero_conocido(q)
    # #2: no hay 10-Q del cuarto trimestre. Q4 = anual (10-K, 330–400 días) − suma de los 3 trimestres
    #     de ESE año fiscal (los que terminan dentro del año, por `end`); su `filed` es el del 10-K.
    anual = primera_publicacion(d[d.dur.between(*DUR_ANUAL) & (d.form == "10-K")], ["end"])
    q4 = []
    for _, a in anual.iterrows():
        dentro = q[(q["end"] > a["start"]) & (q["end"] < a["end"] - pd.Timedelta(days=DUR_TRIMESTRE[0] - 1))]
        if len(dentro) != 3:
            continue                                       # sin los 3 trimestres no se deriva Q4: queda vacío (#7)
        q4.append({"start": dentro["end"].max() + pd.Timedelta(days=1), "end": a["end"],
                   "val": a["val"] - dentro["val"].sum(), "filed": max(a["filed"], dentro["filed"].max()),
                   "form": "10-K", "origen": "q4_derivado"})
    q = unir([q, pd.DataFrame(q4, columns=cols + ["origen"])], cols + ["origen"])
    return primero_conocido(q).sort_values("end")   # #4: gana el que se conoció primero


# Parte 2: saldos y tabla trimestral (formato largo).
def trimestres_saldo(h, nombre):
    """#5: el patrimonio y la deuda son saldos (una foto a una fecha, sin `start`): no se suman.
    Se toma el valor al cierre de cada período, con su primera publicación (#4)."""
    d = hechos_de(h, nombre)
    d = primera_publicacion(d[d["start"].isna()], ["end"])
    return d[["start", "end", "val", "filed", "form", "escala_corregida", "escala_sin_vecinos"]].assign(origen="saldo")

def tabla_trimestral(h):
    """Los 7 conceptos por trimestre, cada valor con SU `filed` y su origen (para auditar en nb02)."""
    partes = [trimestres_flujo(h, c).assign(concepto=c) for c in FLUJOS]
    partes += [trimestres_saldo(h, c).assign(concepto=c) for c in SALDOS]
    return unir(partes, ["start", "end", "val", "filed", "form", "escala_corregida", "escala_sin_vecinos", "origen", "concepto"])   # tipos fijos


# Parte 3: TTM y los 5 ratios, cada uno con su fecha de disponibilidad.
def ttm_flujo(tq, concepto):
    """#5 y #7: TTM = suma de los 4 ÚLTIMOS trimestres CONSECUTIVOS hasta cada `end`.
    Si falta uno (o no son consecutivos) el TTM queda NaN: nunca se rellena con ceros.
    #9: su `filed` es el más tardío de los 4 (existe desde que se publicó el último)."""
    s = tq[tq.concepto == concepto].sort_values("end").reset_index(drop=True)
    filas = []
    for i in range(3, len(s)):
        v = s.iloc[i - 3:i + 1]
        dias = (v["end"].iloc[-1] - v["end"].iloc[0]).days        # 4 trimestres seguidos ≈ 273 días entre cierres
        ok = 3 * DUR_TRIMESTRE[0] <= dias <= 3 * DUR_TRIMESTRE[1] and v["val"].notna().all()
        filas.append({"end": v["end"].iloc[-1], f"{concepto}_ttm": v["val"].sum() if ok else np.nan,
                      f"filed_{concepto}_ttm": v["filed"].max() if ok else pd.NaT})
    t = pd.DataFrame(filas, columns=["end", f"{concepto}_ttm", f"filed_{concepto}_ttm"])
    t[f"filed_{concepto}_ttm"] = pd.to_datetime(t[f"filed_{concepto}_ttm"])   # pandas 3: fecha aunque todo sea vacío
    t[f"{concepto}_ttm"] = t[f"{concepto}_ttm"].astype(float)                   # y número aunque la empresa no reporte el concepto (ADM, CLX)
    return t.set_index("end")

def ultimo_valor(tq, concepto):
    """#5 y #6: saldos y acciones en el cierre de cada trimestre (el último valor publicado para ese `end`)."""
    s = tq[tq.concepto == concepto].set_index("end")
    return s[["val", "filed"]].rename(columns={"val": concepto, "filed": f"filed_{concepto}"})

def eps_promedio(tq, n=VENTANA_NORM):
    """Promedio ANUAL de las utilidades por acción de los últimos 3 años (denominador del P/E normalizado):
    suma de la utilidad neta de los n trimestres consecutivos hasta cada `end` ÷ (n/4) años ÷ acciones del ÚLTIMO
    trimestre de la ventana. Se divide entre las acciones de hoy (no entre las de cada trimestre) para que un split
    dentro de la ventana no distorsione el promedio; es la misma convención del EPS TTM (#6).
    Vacío si falta un trimestre de utilidad o las acciones del último (nunca 0). Su `filed` es el más tardío
    de los n trimestres y de esas acciones: existe desde que se publicó el último."""
    u = tq[tq.concepto == "utilidad_neta"].set_index("end")[["val", "filed"]].sort_index()
    a = tq[tq.concepto == "acciones"].set_index("end")[["val", "filed"]]
    span = pd.Series(u.index, index=u.index).diff(n - 1).dt.days      # n trimestres seguidos ≈ (n−1)·91 días
    ok = span.between((n - 1) * DUR_TRIMESTRE[0], (n - 1) * DUR_TRIMESTRE[1])
    suma = u["val"].rolling(n, min_periods=n).sum()
    f_u = pd.to_datetime(u["filed"].astype("datetime64[ns]").astype("int64").rolling(n, min_periods=n).max())
    acc = a["val"].reindex(u.index); f_a = a["filed"].reindex(u.index).astype("datetime64[ns]")
    out = pd.DataFrame({"eps_prom_3a": (suma / (n / 4) / acc.where(acc > 0)).where(ok),
                        "filed_eps_prom_3a": pd.concat([f_u, f_a], axis=1).max(axis=1, skipna=False).where(ok)})
    out.loc[out.eps_prom_3a.isna(), "filed_eps_prom_3a"] = pd.NaT
    out.index = pd.to_datetime(out.index); return out


def ratios_ttm(tq):
    """Una fila por cierre de trimestre: flujos TTM, saldos y acciones, y los 5 ratios con filed_<ratio>."""
    r = pd.concat([ttm_flujo(tq, c) for c in ["utilidad_neta", "ingresos", "utilidad_operativa", "eps_reportado"]],
                  axis=1).sort_index()
    r.index = pd.to_datetime(r.index); r.index.name = "end"         # pandas 3: índice con tipo fecha
    for c in SALDOS + ["acciones"]:
        # saldo o acciones: el último valor con `end` ≤ cierre del trimestre (merge_asof hacia atrás, sin futuro).
        # Tolerancia de un trimestre (120 días): si el saldo de ese trimestre falta, el ratio queda vacío (#7)
        # en lugar de arrastrar un valor de años atrás que haría parecer disponible un dato que no existe.
        u = ultimo_valor(tq, c).sort_index().reset_index()
        r = pd.merge_asof(r.reset_index().sort_values("end"), u, on="end", direction="backward",
                          tolerance=pd.Timedelta(days=DUR_TRIMESTRE[1])).set_index("end")
    # #6: si faltan las acciones del trimestre, acciones implícitas = utilidad neta TTM ÷ EPS reportado TTM
    imp = r["acciones"].isna() & r["utilidad_neta_ttm"].notna() & r["eps_reportado_ttm"].notna() & (r["eps_reportado_ttm"] != 0)
    r.loc[imp, "acciones"] = r["utilidad_neta_ttm"] / r["eps_reportado_ttm"]
    r.loc[imp, "filed_acciones"] = r[["filed_utilidad_neta_ttm", "filed_eps_reportado_ttm"]].max(axis=1)
    r["acciones_implicitas"] = imp
    def ratio(num, den, nombre):
        """Cada ratio existe desde la publicación más tardía de SUS dos insumos (NaT si falta uno)."""
        # Dominio: con patrimonio ≤ 0 (recompras mayores que el patrimonio) el ROE y la deuda/patrimonio no se
        # pueden leer como ratio (cambian de signo o explotan): quedan vacíos, igual que el P/E con EPS ≤ 0
        r[nombre] = r[num] / r[den].where(r[den] > 0 if den == "patrimonio" else r[den] != 0)
        f = r[[f"filed_{num}", f"filed_{den}"]].where(r[nombre].notna())
        r[f"filed_{nombre}"] = f.max(axis=1).where(f.notna().all(axis=1))
    ratio("utilidad_neta_ttm", "acciones", "eps_ttm")             # #6: EPS TTM con las acciones del último trimestre
    ratio("patrimonio", "acciones", "bvps")
    ratio("utilidad_neta_ttm", "patrimonio", "roe_ttm")
    ratio("utilidad_operativa_ttm", "ingresos_ttm", "margen_operativo_ttm")
    ratio("deuda_lp", "patrimonio", "deuda_patrimonio")
    r = r.join(eps_promedio(tq), how="left")                       # P/E normalizado (P2 y P3)
    r.index = pd.to_datetime(r.index)                               # pandas 3: tipos fijos
    for c in [c for c in r.columns if c.startswith("filed_")]:
        r[c] = pd.to_datetime(r[c])
    return r.drop(columns=["eps_reportado_ttm", "filed_eps_reportado_ttm"]).reset_index()

def construir_tabla_trimestral(hechos: pd.DataFrame) -> pd.DataFrame:
    """Tabla trimestral en formato largo (una fila por empresa, concepto y cierre) a partir de los hechos de EDGAR."""
    return pd.concat([tabla_trimestral(h).assign(ticker=t) for t, h in hechos.groupby("ticker")], ignore_index=True)


def construir_ratios_ttm(hechos: pd.DataFrame, tq: pd.DataFrame | None = None) -> pd.DataFrame:
    """Ratios TTM de todas las empresas (una fila por empresa y cierre de trimestre), como `data/snapshots/ratios_ttm`.

    `tq` es la tabla trimestral ya construida (opcional: si se omite se calcula de `hechos`; nb01 la pasa para no repetir el cálculo).
    """
    if tq is None:
        tq = construir_tabla_trimestral(hechos)
    return pd.concat([ratios_ttm(tq[tq.ticker == t]).assign(ticker=t) for t in tq.ticker.unique()], ignore_index=True)


# --- Panel diario, etiqueta apilada y partición (nuevas, entrega 2) ---
def construir_panel_diario(precios_diarios: pd.DataFrame) -> pd.DataFrame:
    """Panel diario por ticker con las variables de magnitud, solo con ventanas hacia atrás (sin look-ahead).

    Entrada: columnas `fecha, ticker, close`. Salida: `fecha, ticker, close, r, abs_r, sigma20, sigma252, sigma20_sigma252`,
    con r = Δlog(close), σ20 y σ252 diarias (desviación muestral de las últimas SIGMA_CORTA_D y SIGMA_VENTANA_D
    sesiones; vacías mientras no completan su ventana) y su cociente. Un ticker con menos de 252 sesiones queda con σ252 vacía.
    """
    cols = ["fecha", "ticker", "close", "r", "abs_r", "sigma20", "sigma252", "sigma20_sigma252"]
    px = precios_diarios[["fecha", "ticker", "close"]].copy()
    px["fecha"] = px["fecha"].astype("datetime64[ns]")
    partes = []
    for t, g in px.sort_values(["ticker", "fecha"]).groupby("ticker", sort=False):
        g = g.set_index("fecha")
        r = np.log(g["close"]).diff()
        s252 = r.rolling(SIGMA_VENTANA_D, min_periods=SIGMA_VENTANA_D).std(ddof=1)   # σ diaria del último año
        s20 = r.rolling(SIGMA_CORTA_D, min_periods=SIGMA_CORTA_D).std(ddof=1)       # σ diaria del último mes
        partes.append(pd.DataFrame({"close": g["close"], "r": r, "abs_r": r.abs(), "sigma20": s20,
                                    "sigma252": s252, "sigma20_sigma252": s20 / s252}).assign(ticker=t).reset_index())
    if not partes:
        return pd.DataFrame(columns=cols)
    return pd.concat(partes, ignore_index=True)[cols]


def tabla_modelo(panel: pd.DataFrame, ks=K_GRID, n: int = N_DIAS) -> pd.DataFrame:
    """Panel + etiqueta apilada para cada k de `ks`: una fila por (fecha, ticker, k).

    Agrega `k`, `y` (1 si toca primero la barrera inferior, 0 si no; vacía si no hay etiqueta) y `censurada`
    (True si `y` es vacía con σ252 disponible: faltan sesiones por delante o hay un hueco de precios).
    Se descarta el calentamiento (σ252 vacía).
    """
    panel = panel.copy()
    panel["fecha"] = panel["fecha"].astype("datetime64[ns]")
    partes = []
    for t, g in panel.sort_values(["ticker", "fecha"]).groupby("ticker", sort=False):
        g = g.set_index("fecha", drop=False)                  # close y σ252 con el MISMO índice `fecha`
        for k in ks:
            lab = etiqueta_entrada(g["close"], g["sigma252"], k_inf=k, k_sup=K_SUP, n=n)
            d = g.reset_index(drop=True).assign(k=float(k), y=lab["etiqueta"].to_numpy())
            d["censurada"] = d["y"].isna() & d["sigma252"].notna()
            partes.append(d[d["sigma252"].notna()])           # fuera el calentamiento
    if not partes:
        return panel.iloc[:0].assign(k=pd.Series(dtype=float), y=pd.Series(dtype=float),
                                     censurada=pd.Series(dtype=bool))
    return pd.concat(partes, ignore_index=True)


def asignar_conjunto(fechas: pd.Series, final: bool = False, brecha: int = BRECHA, unidad: str = "sesiones") -> pd.Series:
    """Conjunto de cada fecha: "entrenamiento", "validacion", "prueba" o "brecha" (spec §6).

    El calendario es el de las fechas únicas ordenadas de `fechas`. La brecha descarta las últimas `brecha` fechas
    antes de INICIO_VALIDACION y antes de INICIO_PRUEBA, para que una etiqueta del conjunto anterior no mire dentro
    del siguiente. Con `final=True` (modelo final) no hay validación: "entrenamiento_final" va hasta antes de INICIO_PRUEBA
    (menos las últimas `brecha` fechas, que son "brecha") y "prueba" desde INICIO_PRUEBA.
    `unidad` solo documenta y valida el calendario: "sesiones" (fechas diarias, separación mediana <= 4 días) o
    "semanas" (separación mediana ~7 días); si no coincide se lanza ValueError.
    """
    f = pd.to_datetime(pd.Series(fechas))
    cal = np.sort(f.dropna().unique())
    if unidad not in ("sesiones", "semanas"):
        raise ValueError(f"unidad debe ser 'sesiones' o 'semanas', no {unidad!r}")
    if len(cal) > 1:
        sep = float(np.median(np.diff(cal) / np.timedelta64(1, "D")))
        if (unidad == "sesiones" and sep > 4) or (unidad == "semanas" and not 6 <= sep <= 8):
            raise ValueError(f"El calendario no es de {unidad}: separación mediana de {sep:g} días")
    cal = pd.DatetimeIndex(cal)

    def ultimas(corte):            # las `brecha` fechas del calendario justo antes de `corte`
        previas = cal[cal < pd.Timestamp(corte)]
        return previas[-brecha:] if brecha > 0 else previas[:0]

    if final:
        conj = np.where(f < pd.Timestamp(INICIO_PRUEBA), "entrenamiento_final", "prueba").astype(object)
        en_brecha = f.isin(ultimas(INICIO_PRUEBA))
    else:
        conj = np.select([f < pd.Timestamp(INICIO_VALIDACION), f < pd.Timestamp(INICIO_PRUEBA)],
                         ["entrenamiento", "validacion"], default="prueba").astype(object)
        en_brecha = f.isin(ultimas(INICIO_VALIDACION)) | f.isin(ultimas(INICIO_PRUEBA))
    conj = np.where(en_brecha, "brecha", conj).astype(object)
    conj[f.isna().to_numpy()] = np.nan
    return pd.Series(conj, index=f.index)


def submuestra(tabla: pd.DataFrame, paso: int = PASO_SUBMUESTRA) -> pd.DataFrame:
    """Una fila cada `paso` sesiones por ticker y por k (la sesión i con i % paso == 0 de su numeración; determinista)."""
    t = tabla.sort_values(["ticker", "k", "fecha"], kind="stable")
    i = t.groupby(["ticker", "k"]).cumcount()
    return t[(i % paso == 0).to_numpy()]


def k_de_nivel(precio: float, nivel: float, sigma_diaria: float, n: int = N_DIAS) -> float:
    """k = ln(precio/nivel) / (σ_diaria · √n): a cuántas desviaciones del horizonte queda el nivel del precio.

    Vacío (nan) si σ es vacía o no positiva, o si el precio o el nivel no son positivos.
    """
    if sigma_diaria is None or not np.isfinite(sigma_diaria) or sigma_diaria <= 0:
        return float("nan")
    if not (precio > 0 and nivel > 0):
        return float("nan")
    return float(np.log(precio / nivel) / (sigma_diaria * np.sqrt(n)))


def brier_skill(y: np.ndarray, p: np.ndarray, p_ref: float) -> float:
    """Brier skill score = 1 − Brier(p) / Brier(p_ref); positivo si p supera a la referencia constante o por grupo."""
    y = np.asarray(y, dtype=float)
    return float(1 - np.mean((np.asarray(p, dtype=float) - y) ** 2) / np.mean((np.asarray(p_ref, dtype=float) - y) ** 2))


def dependencia_sector(r_sem_accion: pd.Series, r_sem_spy: pd.Series, r_sem_xlp: pd.Series) -> dict:
    """Cuánto agrega el sector al mercado (nb04 §6): R² de `r ~ r_spy + r_xlp` y su aumento sobre `r ~ r_spy`.

    Los tres retornos semanales se alinean por fecha y se descartan los vacíos; con menos de 104 semanas (2 años) devuelve nan.
    """
    d = pd.concat([r_sem_accion, r_sem_spy, r_sem_xlp], axis=1, keys=["r", "r_spy", "r_xlp"]).dropna()
    if len(d) < 104:
        return {"r2_mercado_sector": float("nan"), "delta_r2_sector": float("nan")}
    m1 = smf.ols("r ~ r_spy", data=d).fit()               # solo mercado
    m2 = smf.ols("r ~ r_spy + r_xlp", data=d).fit()       # mercado + sector
    return {"r2_mercado_sector": float(m2.rsquared), "delta_r2_sector": float(m2.rsquared - m1.rsquared)}
