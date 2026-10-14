"""Monte Carlo con medida real: línea base GBM de la triple barrera y modelo de índice único."""
import numpy as np
import pandas as pd

from asistente import riesgo


def prob_triple_barrera_gbm(sigma: float, k_inf: float, k_sup: float, n: int, mu: float = 0.0,
                            n_sims: int = 20000, semilla: int = 0) -> float:
    """P(tocar la barrera inferior antes que la superior) en n semanas bajo un GBM.

    Es la probabilidad INCONDICIONAL: las trayectorias que no tocan ninguna barrera
    dentro de n semanas cuentan como 0, igual que en `etiquetas.etiqueta_entrada`.
    """
    rng = np.random.default_rng(semilla)
    pasos = rng.normal(mu - sigma ** 2 / 2, sigma, size=(n_sims, n))
    log_camino = np.cumsum(pasos, axis=1)
    ancho = sigma * np.sqrt(n)
    toca_inf = log_camino <= -k_inf * ancho
    toca_sup = log_camino >= k_sup * ancho
    primero_inf = np.where(toca_inf.any(axis=1), toca_inf.argmax(axis=1), n)
    primero_sup = np.where(toca_sup.any(axis=1), toca_sup.argmax(axis=1), n)
    return float(np.mean(primero_inf < primero_sup))


def simular_indice_unico(r_activo: pd.Series, r_etf: pd.Series, n: int, n_sims: int = 10000,
                         semilla: int = 0, con_sector: bool = True) -> np.ndarray:
    d = pd.concat([r_activo, r_etf], axis=1, keys=["a", "m"]).dropna()
    ba = riesgo.beta_alpha(d["a"], d["m"])
    resid = (d["a"] - (ba["alpha"] + ba["beta"] * d["m"])).to_numpy()
    rng = np.random.default_rng(semilla)
    idx_m = rng.integers(0, len(d), size=(n_sims, n))
    idx_e = rng.integers(0, len(d), size=(n_sims, n))
    sector = d["m"].to_numpy()[idx_m] if con_sector else np.full((n_sims, n), d["m"].mean())
    r_sim = ba["alpha"] + ba["beta"] * sector + resid[idx_e]
    return np.exp(np.cumsum(r_sim, axis=1))


def prob_alcanzar(trayectorias: np.ndarray, nivel_rel: float) -> float:
    if nivel_rel >= 1:
        return float(np.mean(trayectorias.max(axis=1) >= nivel_rel))
    return float(np.mean(trayectorias.min(axis=1) <= nivel_rel))
