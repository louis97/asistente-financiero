"""SEC EDGAR companyfacts: hechos XBRL anuales alineados por fecha de publicación (filed)."""
import os
import time

import pandas as pd
import requests

URL_TICKERS = "https://www.sec.gov/files/company_tickers.json"
URL_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

# nombre -> (alternativas XBRL en orden de prioridad, unidad)
CONCEPTOS: dict[str, tuple[list[str], str]] = {
    "ingresos": (["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"], "USD"),
    "utilidad_bruta": (["GrossProfit"], "USD"),
    "utilidad_operativa": (["OperatingIncomeLoss"], "USD"),
    "utilidad_neta": (["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"], "USD"),
    "patrimonio": (["StockholdersEquity",
                    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"], "USD"),
    "deuda_lp": (["LongTermDebt", "LongTermDebtNoncurrent"], "USD"),
    "caja": (["CashAndCashEquivalentsAtCarryingValue"], "USD"),
    "cfo": (["NetCashProvidedByUsedInOperatingActivities"], "USD"),
    "capex": (["PaymentsToAcquirePropertyPlantAndEquipment"], "USD"),
    "acciones": (["WeightedAverageNumberOfDilutedSharesOutstanding",
                  "WeightedAverageNumberOfSharesOutstandingBasic"], "shares"),
}
_DURACION_ANUAL = (330, 400)  # días; filtra flujos que no son de año completo


def mapa_ticker_cik(company_tickers: dict) -> dict[str, str]:
    return {v["ticker"]: str(v["cik_str"]).zfill(10) for v in company_tickers.values()}


def descargar_json(url: str) -> dict:
    agente = os.environ.get("SEC_USER_AGENT")
    if not agente:
        raise RuntimeError("Defina SEC_USER_AGENT='Nombre correo' (requisito de la SEC)")
    time.sleep(0.15)  # < 10 solicitudes por segundo
    r = requests.get(url, headers={"User-Agent": agente}, timeout=30)
    r.raise_for_status()
    return r.json()


def hechos_a_df(companyfacts: dict, taxonomia: str = "us-gaap") -> pd.DataFrame:
    filas = []
    for concepto, contenido in companyfacts.get("facts", {}).get(taxonomia, {}).items():
        for unidad, hechos in contenido.get("units", {}).items():
            for h in hechos:
                filas.append({"concepto": concepto, "unidad": unidad, "start": h.get("start"),
                              "end": h.get("end"), "val": h.get("val"), "form": h.get("form"),
                              "fp": h.get("fp"), "filed": h.get("filed")})
    df = pd.DataFrame(filas, columns=["concepto", "unidad", "start", "end", "val", "form", "fp", "filed"])
    for c in ("start", "end", "filed"):
        df[c] = pd.to_datetime(df[c])
    return df


def serie_anual(hechos: pd.DataFrame, alternativas: list[str], unidad: str) -> pd.DataFrame:
    """Un valor anual (10-K, FY) por fin de período, tomando la PRIMERA publicación.

    Para cada período gana la publicación más temprana (`filed`); `alternativas` solo desempata
    entre nombres XBRL publicados el mismo día, en su orden de prioridad.
    Un concepto ausente devuelve un DataFrame vacío (nunca ceros).
    """
    cols = ["end", "filed", "val", "concepto"]
    d = hechos[(hechos.concepto.isin(alternativas)) & (hechos.unidad == unidad)
               & (hechos.form == "10-K") & (hechos.fp == "FY")].copy()
    if d.empty:
        return pd.DataFrame({
            "end": pd.Series(dtype=hechos["end"].dtype),
            "filed": pd.Series(dtype=hechos["filed"].dtype),
            "val": pd.Series(dtype="float64"),
            "concepto": pd.Series(dtype=object),
        })
    dur = (d["end"] - d["start"]).dt.days
    d = d[d["start"].isna() | dur.between(*_DURACION_ANUAL)]
    d = d[d["filed"] >= d["end"]]  # publicado antes del cierre del período: imposible
    d["prioridad"] = d["concepto"].map({c: i for i, c in enumerate(alternativas)})
    d = d.sort_values(["end", "filed", "prioridad"]).drop_duplicates("end", keep="first")
    return d[cols].reset_index(drop=True)


def alinear_por_filed(precios: pd.DataFrame, fundamentales: pd.DataFrame) -> pd.DataFrame:
    """Une a cada fecha de precio el último dato fundamental ya publicado (filed <= fecha)."""
    p = precios.dropna(subset=["fecha"]).copy()
    f = fundamentales.dropna(subset=["filed"]).copy()
    p["fecha"] = p["fecha"].astype("datetime64[ns]")  # merge_asof exige la misma resolución
    f["filed"] = f["filed"].astype("datetime64[ns]")
    p, f = p.sort_values("fecha"), f.sort_values("filed")
    return pd.merge_asof(p, f, left_on="fecha", right_on="filed", direction="backward")
