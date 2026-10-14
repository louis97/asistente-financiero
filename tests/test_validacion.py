"""Pruebas de validacion: Kupiec, Christoffersen, calibración logística y bootstrap por fechas."""
import numpy as np
import pandas as pd
import pytest

from asistente.validacion import (
    calibracion_logistica,
    christoffersen,
    ic_bootstrap_fechas,
    kupiec,
)


def test_kupiec_lr_cero_cuando_tasa_igual_a_p():
    lr, p = kupiec(50, 1000, 0.05)
    assert lr == pytest.approx(0.0, abs=1e-9)
    assert p == pytest.approx(1.0)


def test_kupiec_valor_conocido():
    lr, p = kupiec(63, 875, 0.05)
    assert lr == pytest.approx(7.894, abs=1e-3)
    assert 0 < p < 0.05


def test_christoffersen_alternada_iid_sin_agrupamiento():
    exc = pd.Series(np.random.default_rng(3).uniform(size=2000) < 0.05)
    r = christoffersen(exc, p=0.05)
    assert set(r) == {"lr_ind", "p_ind", "lr_cc", "p_cc"}
    assert r["p_ind"] > 0.1  # iid: no rechaza independencia (p = 0.22 con esta semilla)


def test_christoffersen_excepciones_juntas():
    exc = pd.Series([False] * 90 + [True] * 10 + [False] * 100)
    r = christoffersen(exc, p=0.05)
    assert r["p_ind"] < 1e-3
    assert r["p_cc"] < 1e-3


def test_christoffersen_sin_transiciones_11_es_finito():
    exc = pd.Series([False, True] * 30)
    r = christoffersen(exc)
    assert all(np.isfinite(v) for v in r.values())


def test_christoffersen_sin_excepciones_es_finito():
    r = christoffersen(pd.Series([False] * 100))
    assert all(np.isfinite(v) for v in r.values())


def test_calibracion_logistica_recupera_a0_b1():
    rng = np.random.default_rng(1)
    p = rng.uniform(0.05, 0.95, 20_000)
    y = (rng.uniform(size=p.size) < p).astype(int)
    r = calibracion_logistica(y, p)
    assert abs(r["a"]) < 0.15
    assert abs(r["b"] - 1) < 0.15


def _df(valores):
    fechas = pd.date_range("2020-01-01", periods=len(valores), freq="W")
    return pd.DataFrame({"fecha": np.repeat(fechas, 2), "x": np.repeat(valores, 2)})


def test_bootstrap_fechas_serie_constante_ic_degenerado():
    est, lo, hi = ic_bootstrap_fechas(_df(np.full(40, 3.0)), lambda d: d.x.mean(), bloque=4, reps=50)
    assert est == lo == hi == 3.0


def test_bootstrap_fechas_bloque_mayor_que_muestra():
    with pytest.raises(ValueError, match="bloque"):
        ic_bootstrap_fechas(_df(np.arange(5.0)), lambda d: d.x.mean(), bloque=10)


def test_bootstrap_fechas_ic_contiene_estimacion_y_reproducible():
    df = _df(np.random.default_rng(0).normal(size=100))
    a = ic_bootstrap_fechas(df, lambda d: d.x.mean(), bloque=5, reps=100)
    b = ic_bootstrap_fechas(df, lambda d: d.x.mean(), bloque=5, reps=100)
    assert a == b
    assert a[1] <= a[0] <= a[2]
