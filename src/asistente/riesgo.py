"""Métricas de riesgo por activo (curso IIND-4414), reversión a la media (OU) y Merton."""
import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from scipy.stats import norm


def log_retornos(close: pd.Series) -> pd.Series:
    return np.log(close).diff()


def vol_historica(r: pd.Series, ventana: int = 52, periodos: int = 52) -> pd.Series:
    return r.rolling(ventana, min_periods=ventana).std(ddof=1) * np.sqrt(periodos)


def vol_ewma(r: pd.Series, lam: float = 0.94, periodos: int = 52) -> pd.Series:
    var = (r ** 2).ewm(alpha=1 - lam, adjust=False).mean()
    return np.sqrt(var) * np.sqrt(periodos)


def var_historico(r: pd.Series, alpha: float = 0.05) -> float:
    return float(np.nanquantile(r, alpha))


def var_parametrico(r: pd.Series, alpha: float = 0.05) -> float:
    return float(r.mean() + norm.ppf(alpha) * r.std(ddof=1))


def es_historico(r: pd.Series, alpha: float = 0.05) -> float:
    var = var_historico(r, alpha)
    return float(r[r <= var].mean())


def var_historico_movil(r: pd.Series, ventana: int = 52, alpha: float = 0.05) -> pd.Series:
    return r.rolling(ventana, min_periods=ventana).quantile(alpha)


def max_drawdown(close: pd.Series) -> tuple[float, pd.Series]:
    serie = close / close.cummax() - 1
    return float(serie.min()), serie


def beta_alpha(r: pd.Series, r_m: pd.Series) -> dict:
    d = pd.concat([r, r_m], axis=1, keys=["r", "m"]).dropna()
    beta, alpha = np.polyfit(d["m"], d["r"], 1)
    resid = d["r"] - (alpha + beta * d["m"])
    r2 = 1 - resid.var(ddof=1) / d["r"].var(ddof=1)
    return {"beta": float(beta), "alpha": float(alpha), "r2": float(r2),
            "sigma_idio": float(resid.std(ddof=1))}


def sharpe(r: pd.Series, rf: float = 0.0, periodos: int = 52) -> float:
    exceso = r - rf / periodos
    return float(exceso.mean() / exceso.std(ddof=1) * np.sqrt(periodos))


def ajuste_ou(x: pd.Series, dt: float = 1 / 52) -> dict:
    s = pd.Series(x).dropna()
    dx, rezago = s.diff().iloc[1:], s.shift(1).iloc[1:]
    b, a = np.polyfit(rezago, dx, 1)
    sigma = float((dx - (a + b * rezago)).std(ddof=1))
    if not -2 < b < 0:
        return {"m": np.nan, "eta": np.nan, "vida_media_anios": np.nan, "sigma": sigma}
    eta = -np.log(1 + b) / dt
    return {"m": float(-a / b), "eta": float(eta), "vida_media_anios": float(np.log(2) / eta),
            "sigma": sigma}


def merton(E: float, sigma_E: float, D: float, r: float, T: float = 1.0) -> dict:
    def ecuaciones(z):
        V, sV = z
        d1 = (np.log(V / D) + (r + sV ** 2 / 2) * T) / (sV * np.sqrt(T))
        d2 = d1 - sV * np.sqrt(T)
        return [V * norm.cdf(d1) - D * np.exp(-r * T) * norm.cdf(d2) - E,
                norm.cdf(d1) * sV * V - sigma_E * E]
    V, sV = fsolve(ecuaciones, x0=[E + D, sigma_E * E / (E + D)])
    d2 = (np.log(V / D) + (r - sV ** 2 / 2) * T) / (sV * np.sqrt(T))
    return {"V": float(V), "sigma_V": float(sV), "d2": float(d2), "pd": float(norm.cdf(-d2))}
