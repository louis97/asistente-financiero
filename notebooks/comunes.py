"""Lo que comparten dos o más notebooks: universo, conceptos y ratios de EDGAR, rutas, carga de instantáneas y los dos bootstrap.

Todo lo demás vive dentro de cada notebook, junto a su explicación.
"""
from pathlib import Path

import numpy as np
import pandas as pd

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
