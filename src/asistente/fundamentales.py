"""Ratios anuales desde EDGAR, múltiplos semanales sin look-ahead y percentiles."""
import numpy as np
import pandas as pd

from asistente import edgar


def tabla_anual(hechos: pd.DataFrame) -> pd.DataFrame:
    series = []
    for nombre, (alternativas, unidad) in edgar.CONCEPTOS.items():
        s = edgar.serie_anual(hechos, alternativas, unidad)
        series.append(s.rename(columns={"val": nombre, "filed": f"filed_{nombre}"})
                      .drop(columns="concepto").set_index("end"))
    tabla = pd.concat(series, axis=1).sort_index()
    cols_filed = [c for c in tabla.columns if c.startswith("filed_")]
    tabla["filed"] = tabla[cols_filed].max(axis=1)  # conservador: el año está completo cuando todo se publicó
    for nombre in edgar.CONCEPTOS:
        if nombre not in tabla.columns:
            tabla[nombre] = np.nan
    return tabla.drop(columns=cols_filed).reset_index().rename(columns={"index": "end"})


def _div(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.where(b != 0)


def ratios_anuales(tabla: pd.DataFrame, tasa_impuesto: float = 0.21) -> pd.DataFrame:
    r = tabla.copy()
    r["roe"] = _div(r["utilidad_neta"], r["patrimonio"])
    r["margen_bruto"] = _div(r["utilidad_bruta"], r["ingresos"])
    r["margen_operativo"] = _div(r["utilidad_operativa"], r["ingresos"])
    r["margen_neto"] = _div(r["utilidad_neta"], r["ingresos"])
    r["deuda_patrimonio"] = _div(r["deuda_lp"], r["patrimonio"])
    r["capex_ventas"] = _div(r["capex"], r["ingresos"])
    r["eps"] = _div(r["utilidad_neta"], r["acciones"])
    r["bvps"] = _div(r["patrimonio"], r["acciones"])
    r["fcf"] = r["cfo"] - r["capex"]
    capital_invertido = r["patrimonio"] + r["deuda_lp"] - r["caja"]
    r["roic"] = _div(r["utilidad_operativa"] * (1 - tasa_impuesto), capital_invertido)
    return r


def multiplos_semanales(precios: pd.DataFrame, ratios: pd.DataFrame) -> pd.DataFrame:
    m = edgar.alinear_por_filed(precios, ratios[["filed", "eps", "bvps", "fcf", "acciones"]])
    m["pe"] = m["close"] / m["eps"].where(m["eps"] > 0)      # EPS <= 0 → P/E sin sentido (T2)
    m["pb"] = m["close"] / m["bvps"].where(m["bvps"] > 0)
    m["fcf_yield"] = _div(m["fcf"], m["close"] * m["acciones"])
    return m


def percentil_expansivo(serie: pd.Series, min_obs: int = 52) -> pd.Series:
    def _pct(w: np.ndarray) -> float:
        actual = w[-1]
        if np.isnan(actual):
            return np.nan
        w = w[~np.isnan(w)]
        return float((w <= actual).mean())
    return serie.expanding(min_periods=min_obs).apply(_pct, raw=True)


def percentil_en_grupo(ancho: pd.DataFrame) -> pd.DataFrame:
    return ancho.rank(axis=1, pct=True)


def multiplo_relativo(ancho: pd.DataFrame) -> pd.DataFrame:
    return ancho.div(ancho.median(axis=1), axis=0)
