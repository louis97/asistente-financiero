"""Pruebas de validación reutilizables: cobertura y independencia de VaR, calibración y bootstrap por fechas."""
from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.special import xlogy


def kupiec(x: int, n: int, p: float = 0.05) -> tuple[float, float]:
    """Prueba de cobertura incondicional de Kupiec (1995): devuelve (LR, p-valor), chi2 con 1 gl."""
    ph = x / n
    lr = -2 * (xlogy(n - x, 1 - p) + xlogy(x, p)) + 2 * (xlogy(n - x, 1 - ph) + xlogy(x, ph))
    lr = float(max(lr, 0.0))
    return lr, float(stats.chi2.sf(lr, 1))


def christoffersen(excepciones: pd.Series, p: float = 0.05) -> dict:
    """Independencia y cobertura condicional de Christoffersen (1998).

    `excepciones` es una serie booleana en orden temporal (los NaN se descartan).
    Devuelve lr_ind, p_ind (chi2 1 gl), lr_cc = LR_Kupiec + LR_ind y p_cc (chi2 2 gl).
    Se usa xlogy, de modo que los conteos en cero no producen NaN.
    """
    e = excepciones.dropna().astype(int).to_numpy()
    a, b = e[:-1], e[1:]
    n00 = int(((a == 0) & (b == 0)).sum())
    n01 = int(((a == 0) & (b == 1)).sum())
    n10 = int(((a == 1) & (b == 0)).sum())
    n11 = int(((a == 1) & (b == 1)).sum())
    tot = n00 + n01 + n10 + n11
    pi = (n01 + n11) / tot
    pi01 = n01 / (n00 + n01) if (n00 + n01) else 0.0
    pi11 = n11 / (n10 + n11) if (n10 + n11) else 0.0
    ll0 = xlogy(n00 + n10, 1 - pi) + xlogy(n01 + n11, pi)
    ll1 = (xlogy(n00, 1 - pi01) + xlogy(n01, pi01)
           + xlogy(n10, 1 - pi11) + xlogy(n11, pi11))
    lr_ind = float(max(-2 * (ll0 - ll1), 0.0))
    lr_uc, _ = kupiec(int(e.sum()), len(e), p)
    lr_cc = lr_uc + lr_ind
    return {
        "lr_ind": lr_ind,
        "p_ind": float(stats.chi2.sf(lr_ind, 1)),
        "lr_cc": float(lr_cc),
        "p_cc": float(stats.chi2.sf(lr_cc, 2)),
    }


def calibracion_logistica(y, p) -> dict:
    """Regresión logit(P(y=1)) = a + b·logit(p). Devuelve {'a': intercepto, 'b': pendiente}."""
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, dtype=float)
    X = sm.add_constant(np.log(p / (1 - p)))
    res = sm.Logit(y, X).fit(disp=0)
    return {"a": float(res.params[0]), "b": float(res.params[1])}


def ic_bootstrap_fechas(
    df: pd.DataFrame,
    estadistico: Callable[[pd.DataFrame], float],
    bloque: int,
    reps: int = 300,
    semilla: int = 42,
    col_fecha: str = "fecha",
    nivel: float = 0.95,
) -> tuple[float, float, float]:
    """Bootstrap por bloques de fechas consecutivas comunes.

    Remuestrea bloques contiguos de `bloque` fechas únicas (todas las filas de cada fecha viajan
    juntas); usa ceil(n_fechas/bloque) bloques, truncados a n_fechas fechas. Devuelve
    (estimación en df completo, ic_inf, ic_sup). Réplicas con NaN se ignoran.
    """
    fechas = np.sort(df[col_fecha].unique())
    nf = len(fechas)
    if bloque > nf:
        raise ValueError(
            f"El bloque ({bloque}) es mayor que el número de fechas únicas ({nf}); reduzca el bloque."
        )
    filas = df.groupby(col_fecha).indices
    rng = np.random.default_rng(semilla)
    nbl = int(np.ceil(nf / bloque))
    est = float(estadistico(df))
    vals = np.empty(reps)
    for r in range(reps):
        ini = rng.integers(0, nf - bloque + 1, nbl)
        fs = np.concatenate([fechas[i:i + bloque] for i in ini])[:nf]
        ix = np.concatenate([filas[f] for f in fs])
        vals[r] = estadistico(df.iloc[ix])
    q = (1 - nivel) / 2 * 100
    lo, hi = np.nanpercentile(vals, [q, 100 - q])
    return est, float(lo), float(hi)
