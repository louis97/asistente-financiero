"""Tablas de Damodaran Online (NYU Stern) por industria: benchmark académico gratuito."""
from pathlib import Path

import pandas as pd

_BASE = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/"
URLS = {"roc": _BASE + "roc.xls", "ev_ebitda": _BASE + "vebitda.xls",
        "pe": _BASE + "pedata.xls", "margenes": _BASE + "margin.xls"}

MAPA_INDUSTRIAS: dict[str, list[str]] = {
    "tecnologia": ["Software (System & Application)", "Software (Internet)", "Computers/Peripherals",
                   "Semiconductor", "Telecom. Equipment"],
    "consumo_defensivo": ["Beverage (Soft)", "Food Processing", "Household Products",
                          "Retail (General)", "Retail (Grocery and Food)"],
    "financiero": ["Bank (Money Center)", "Banks (Regional)", "Brokerage & Investment Banking"],
}


def leer_tabla(ruta: Path | str) -> pd.DataFrame:
    libro = pd.ExcelFile(ruta)
    hoja = "Industry Averages" if "Industry Averages" in libro.sheet_names else libro.sheet_names[0]
    crudo = pd.read_excel(libro, sheet_name=hoja, header=None)
    fila = next((i for i in range(min(15, len(crudo)))
                 if crudo.iloc[i].astype(str).str.strip().eq("Industry Name").any()), None)
    if fila is None:
        raise ValueError("No se encontró la fila de encabezado 'Industry Name'")
    tabla = crudo.iloc[fila + 1:].copy()
    nombres = (crudo.iloc[fila].astype(str).str.strip().str.lower()
               .str.replace(r"[^0-9a-z]+", "_", regex=True).str.strip("_"))
    # Damodaran repite nombres de columna (p. ej. EV/EBITDA para dos grupos de empresas): sufijo _2, _3...
    tabla.columns = nombres + nombres.groupby(nombres).cumcount().map(lambda n: f"_{n + 1}" if n else "")
    tabla = tabla.dropna(subset=["industry_name"]).reset_index(drop=True)
    for c in tabla.columns[1:]:
        tabla[c] = pd.to_numeric(tabla[c], errors="coerce")
    return tabla


def filas_industria(tabla: pd.DataFrame, industria: str) -> pd.DataFrame:
    return tabla[tabla["industry_name"].isin(MAPA_INDUSTRIAS[industria])].reset_index(drop=True)
