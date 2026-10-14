import numpy as np
import pandas as pd
import pytest

from asistente import indicadores as ind

IDX = pd.date_range("2015-01-02", periods=120, freq="W-FRI")


def test_rsi_serie_creciente_es_100_y_decreciente_es_0():
    sube = pd.Series(np.arange(1, 121, dtype=float), index=IDX)
    assert ind.rsi(sube).iloc[-1] == pytest.approx(100.0)
    assert ind.rsi(sube[::-1].reset_index(drop=True)).iloc[-1] == pytest.approx(0.0)


def test_rsi_calentamiento_es_nan():
    s = pd.Series(np.random.default_rng(0).normal(100, 1, 120), index=IDX)
    r = ind.rsi(s, n=14)
    assert r.iloc[:14].isna().all() and r.iloc[14:].notna().all()
    assert r.dropna().between(0, 100).all()


def test_dist_media_constante_es_cero_y_calentamiento_nan():
    s = pd.Series(50.0, index=IDX)
    d = ind.dist_media(s, 20, "sma")
    assert d.iloc[:19].isna().all() and (d.iloc[19:] == 0).all()
    assert ind.dist_media(s, 20, "ema").iloc[-1] == pytest.approx(0.0)


def test_volumen_relativo_cero_es_nan():
    v = pd.Series(100.0, index=IDX)
    v.iloc[50] = 0.0
    vr = ind.volumen_relativo(v, 20)
    assert np.isnan(vr.iloc[50]) and vr.iloc[30] == pytest.approx(1.0)


def test_posicion_donchian_extremos():
    s = pd.Series(np.arange(120, dtype=float), index=IDX)
    assert ind.posicion_donchian(s, 20).iloc[-1] == pytest.approx(1.0)
    plano = pd.Series(5.0, index=IDX)
    assert ind.posicion_donchian(plano, 20).dropna().empty   # max = min → NaN


def test_momentum_12_1():
    s = pd.Series(np.arange(1, 121, dtype=float), index=IDX)
    m = ind.momentum_12_1(s)
    assert m.iloc[:52].isna().all()
    assert m.iloc[60] == pytest.approx(s.iloc[56] / s.iloc[8] - 1)


def test_historia_corta_no_rellena():
    s = pd.Series(np.linspace(10, 20, 30), index=IDX[:30])   # p.ej. una IPO reciente
    t = ind.tabla_indicadores(s, pd.Series(1000.0, index=IDX[:30]))
    assert t["mom_12_1"].isna().all() and t["dist_sma50"].isna().all()
    assert list(t.columns) == ["rsi14", "dist_sma20", "dist_sma50", "dist_ema20", "vol_rel20", "donchian20", "mom_12_1"]
