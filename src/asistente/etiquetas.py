"""Etiquetas: triple barrera solo-largo para la entrada y retorno a N semanas (con censura)."""
import numpy as np
import pandas as pd


def etiqueta_entrada(close: pd.Series, sigma: pd.Series, k_inf: float, k_sup: float,
                     n: int) -> pd.DataFrame:
    precios = close.to_numpy(dtype=float)
    sig = sigma.reindex(close.index).to_numpy(dtype=float)
    total = len(precios)
    etiqueta = np.full(total, np.nan)
    resultado = np.full(total, None, dtype=object)
    semanas = np.full(total, np.nan)
    for t in range(total):
        if t + n >= total or np.isnan(sig[t]) or np.isnan(precios[t]):
            continue  # censurada (T3) o sin σ conocido en t
        ancho = sig[t] * np.sqrt(n)
        inferior = precios[t] * np.exp(-k_inf * ancho)
        superior = precios[t] * np.exp(k_sup * ancho)
        etiqueta[t], resultado[t] = 0.0, "tiempo"
        for h in range(1, n + 1):
            p = precios[t + h]
            if p <= inferior:
                etiqueta[t], resultado[t], semanas[t] = 1.0, "entrada", h
                break
            if p >= superior:
                etiqueta[t], resultado[t], semanas[t] = 0.0, "escape", h
                break
    return pd.DataFrame({"etiqueta": etiqueta, "resultado": resultado, "semanas": semanas},
                        index=close.index)


def etiqueta_retorno(close: pd.Series, n: int, benchmark: pd.Series | None = None) -> pd.Series:
    futuro = close.shift(-n) / close - 1
    umbral = 0.0 if benchmark is None else (benchmark.shift(-n) / benchmark - 1).reindex(close.index)
    etiqueta = (futuro > umbral).astype(float)
    return etiqueta.where(futuro.notna() & (pd.Series(umbral, index=close.index).notna()))
