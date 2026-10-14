"""Indicadores técnicos sobre series semanales. El calentamiento queda en NaN (no se rellena)."""
import pandas as pd


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    ganancia = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    perdida = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    total = ganancia + perdida
    return 100 * ganancia / total.where(total > 0)


def dist_media(close: pd.Series, n: int, tipo: str = "sma") -> pd.Series:
    if tipo == "sma":
        media = close.rolling(n, min_periods=n).mean()
    elif tipo == "ema":
        media = close.ewm(span=n, adjust=False, min_periods=n).mean()
    else:
        raise ValueError(f"tipo desconocido: {tipo}")
    return close / media - 1


def volumen_relativo(volume: pd.Series, n: int = 20) -> pd.Series:
    v = volume.where(volume > 0)  # 0 = sin dato confiable (T2), no "cero negociación"
    return v / v.rolling(n, min_periods=n).mean()


def posicion_donchian(close: pd.Series, n: int = 20) -> pd.Series:
    alto = close.rolling(n, min_periods=n).max()
    bajo = close.rolling(n, min_periods=n).min()
    rango = (alto - bajo).where(alto > bajo)
    return (close - bajo) / rango


def momentum_12_1(close: pd.Series, periodos_anio: int = 52, salto: int = 4) -> pd.Series:
    return close.shift(salto) / close.shift(periodos_anio) - 1


def tabla_indicadores(close: pd.Series, volume: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({
        "rsi14": rsi(close, 14),
        "dist_sma20": dist_media(close, 20, "sma"),
        "dist_sma50": dist_media(close, 50, "sma"),
        "dist_ema20": dist_media(close, 20, "ema"),
        "vol_rel20": volumen_relativo(volume, 20),
        "donchian20": posicion_donchian(close, 20),
        "mom_12_1": momentum_12_1(close),
    })
