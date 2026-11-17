"""Carga y predicción del modelo técnico (probabilidad de que el precio toque la entrada en 60 sesiones)."""
import json
import threading

import joblib
import numpy as np
import pandas as pd
import sklearn

from app.api import config
import comunes as cm   # noqa: E402  (config agrega notebooks/ al sys.path)

CLAVES_META = ["algoritmo", "variables", "k_grid", "cortes_decil_sigma", "tasa_ref_por_decil_k",
               "calibracion_prueba", "version_sklearn"]
_cache: tuple | None = None
_lock = threading.Lock()


def cargar_modelo() -> tuple:
    """(pipeline, metadata); se carga una vez. Detiene el arranque con un mensaje claro si algo no coincide."""
    global _cache
    with _lock:
        if _cache is not None:
            return _cache
        ruta_meta, ruta_mod = config.MODELO_DIR / "metadata.json", config.MODELO_DIR / "modelo.joblib"
        if not ruta_meta.exists() or not ruta_mod.exists():
            raise RuntimeError(f"Falta el modelo en {config.MODELO_DIR} (modelo.joblib y metadata.json)")
        meta = json.loads(ruta_meta.read_text(encoding="utf-8"))
        for clave in CLAVES_META:
            if clave not in meta:
                raise RuntimeError(f"metadata.json no tiene la clave «{clave}»")
        if list(meta["variables"]) != list(cm.VARIABLES):
            raise RuntimeError(f"Las variables del modelo {meta['variables']} no coinciden con las de comunes.py {cm.VARIABLES}")
        if meta["version_sklearn"] != sklearn.__version__:
            raise RuntimeError(f"La versión de scikit-learn del modelo ({meta['version_sklearn']}) no coincide con la instalada "
                               f"({sklearn.__version__}); reentrene el modelo o instale esa versión")
        _cache = (joblib.load(ruta_mod), meta)
        return _cache


def k_rejilla(k: float, meta: dict) -> float:
    """El k de la rejilla de entrenamiento más cercano."""
    grilla = np.array(meta["k_grid"], dtype=float)
    return float(grilla[np.argmin(np.abs(grilla - k))])


def prob_toque(pipe, fila_variables: dict, k: float) -> float:
    """predict_proba del pipeline con las variables de la última fila del panel y el k del nivel."""
    X = pd.DataFrame([{**fila_variables, "k": k}])[list(cm.VARIABLES)]
    return float(pipe.predict_proba(X)[:, 1][0])


def linea_base(sigma252: float, k: float, meta: dict) -> float:
    """Tasa de toque del entrenamiento en el decil de σ252 de hoy y en el k de la rejilla más cercano."""
    cortes = np.asarray(meta["cortes_decil_sigma"], dtype=float)
    decil = int(np.searchsorted(cortes, sigma252, side="left"))          # (a, b]: igual que pd.cut del entrenamiento
    return float(meta["tasa_ref_por_decil_k"][str(k_rejilla(k, meta))][decil])


def ic_prob(prob: float, meta: dict) -> tuple[float, float]:
    """IC95 de la tasa observada en la prueba para el tramo de probabilidad donde cae `prob` (no envuelve a `prob`)."""
    tramos = meta["calibracion_prueba"]
    for t in tramos:
        if prob <= t["tramo_hi"]:
            return float(t["ic_lo"]), float(t["ic_hi"])
    return float(tramos[-1]["ic_lo"]), float(tramos[-1]["ic_hi"])
