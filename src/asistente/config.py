"""Constantes del proyecto: universo, benchmarks, fechas y rutas."""
from pathlib import Path

UNIVERSO: dict[str, list[str]] = {
    "tecnologia": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ORCL", "ADBE", "CRM", "CSCO", "INTC"],
    "consumo_defensivo": ["KO", "PEP", "PG", "WMT", "COST", "CL", "MDLZ", "KMB", "GIS", "KHC"],
    "financiero": ["JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "SCHW"],
}
ETF_SECTOR: dict[str, str] = {"tecnologia": "XLK", "consumo_defensivo": "XLP", "financiero": "XLF"}
BENCHMARK = "SPY"
INICIO = "2009-01-01"
PERIODOS_ANIO = 52

RAIZ = Path(__file__).resolve().parents[2]
DIR_SNAPSHOTS = RAIZ / "data" / "snapshots"
DIR_ASSETS = RAIZ / "entregables" / "entrega_1" / "assets"


def tickers() -> list[str]:
    return [t for lista in UNIVERSO.values() for t in lista]


def industria_de(ticker: str) -> str:
    for industria, lista in UNIVERSO.items():
        if ticker in lista:
            return industria
    raise KeyError(ticker)
