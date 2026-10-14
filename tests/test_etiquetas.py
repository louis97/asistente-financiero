import numpy as np
import pandas as pd
import pytest

from asistente import etiquetas as et

IDX = pd.date_range("2020-01-03", periods=10, freq="W-FRI")
SIGMA = pd.Series(0.05 / np.sqrt(4), index=IDX)  # con n=4 y k=1 las barreras quedan en ±5% (en log)


def _close(valores):
    return pd.Series(valores, index=IDX[: len(valores)], dtype=float)


def test_toca_inferior_primero_es_entrada():
    c = _close([100, 99, 90, 120, 120, 120, 120, 120, 120, 120])
    out = et.etiqueta_entrada(c, SIGMA, k_inf=1, k_sup=1, n=4)
    assert out.loc[IDX[0], "etiqueta"] == 1.0
    assert out.loc[IDX[0], "resultado"] == "entrada" and out.loc[IDX[0], "semanas"] == 2


def test_toca_superior_primero_es_escape():
    c = _close([100, 101, 110, 80, 80, 80, 80, 80, 80, 80])
    out = et.etiqueta_entrada(c, SIGMA, 1, 1, 4)
    assert out.loc[IDX[0], "etiqueta"] == 0.0 and out.loc[IDX[0], "resultado"] == "escape"


def test_sin_toque_es_tiempo():
    c = _close([100] * 10)
    out = et.etiqueta_entrada(c, SIGMA, 1, 1, 4)
    assert out.loc[IDX[0], "etiqueta"] == 0.0 and out.loc[IDX[0], "resultado"] == "tiempo"
    assert np.isnan(out.loc[IDX[0], "semanas"])


def test_ultimas_n_filas_censuradas_aunque_toquen():
    c = _close([100, 100, 100, 100, 100, 100, 100, 50, 50, 50])   # el toque en t=7 no "resuelve" t=6
    out = et.etiqueta_entrada(c, SIGMA, 1, 1, 4)
    assert out["etiqueta"].iloc[-4:].isna().all()
    assert out["etiqueta"].iloc[:6].notna().all()


def test_sigma_nan_da_nan():
    s = SIGMA.copy(); s.iloc[0] = np.nan
    out = et.etiqueta_entrada(_close([100] * 10), s, 1, 1, 4)
    assert np.isnan(out.loc[IDX[0], "etiqueta"])


def test_etiqueta_retorno_absoluta_y_relativa():
    c = _close([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
    b = _close([100, 110, 120, 130, 140, 150, 160, 170, 180, 190])
    abs_ = et.etiqueta_retorno(c, 2)
    rel = et.etiqueta_retorno(c, 2, benchmark=b)
    assert abs_.iloc[0] == 1.0 and rel.iloc[0] == 0.0
    assert abs_.iloc[-2:].isna().all() and rel.iloc[-2:].isna().all()
