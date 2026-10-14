import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from asistente import riesgo as rg

IDX = pd.date_range("2015-01-02", periods=200, freq="W-FRI")


def test_log_retornos():
    c = pd.Series(np.exp(np.arange(5) * 0.01), index=IDX[:5])
    assert rg.log_retornos(c).dropna().to_numpy() == pytest.approx([0.01] * 4)


def test_vol_historica_anualiza_con_media():
    r = pd.Series(np.tile([0.01, -0.03], 100), index=IDX)
    v = rg.vol_historica(r, ventana=52, periodos=52)
    assert v.iloc[:51].isna().all()
    assert v.iloc[-1] == pytest.approx(r.iloc[-52:].std(ddof=1) * np.sqrt(52))


def test_vol_ewma_constante():
    r = pd.Series(0.02, index=IDX)
    assert rg.vol_ewma(r, lam=0.94, periodos=1).iloc[-1] == pytest.approx(0.02)


def test_var_y_es_historicos():
    r = pd.Series(np.arange(-50, 50) / 1000.0)
    var = rg.var_historico(r, 0.05)
    assert var == pytest.approx(np.quantile(r, 0.05))
    assert rg.es_historico(r, 0.05) <= var


def test_var_parametrico_formula():
    r = pd.Series([0.01, -0.02, 0.03, 0.0, -0.01])
    esperado = r.mean() + norm.ppf(0.05) * r.std(ddof=1)
    assert rg.var_parametrico(r, 0.05) == pytest.approx(esperado)


def test_max_drawdown():
    mdd, serie = rg.max_drawdown(pd.Series([100.0, 120.0, 60.0, 90.0]))
    assert mdd == pytest.approx(-0.5) and serie.iloc[0] == 0.0


def test_beta_alpha_exactos():
    rm = pd.Series(np.random.default_rng(1).normal(0, 0.02, 200), index=IDX)
    ri = 0.001 + 1.5 * rm
    out = rg.beta_alpha(ri, rm)
    assert out["beta"] == pytest.approx(1.5) and out["alpha"] == pytest.approx(0.001)
    assert out["r2"] == pytest.approx(1.0)


def test_sharpe():
    r = pd.Series([0.01, 0.03, 0.02, 0.0])
    assert rg.sharpe(r, periodos=52) == pytest.approx(r.mean() / r.std(ddof=1) * np.sqrt(52))


def test_ou_recupera_parametros():
    rng = np.random.default_rng(7)
    m, phi, n = 20.0, 0.9, 5000
    x = np.empty(n); x[0] = m
    for t in range(1, n):
        x[t] = m * (1 - phi) + phi * x[t - 1] + rng.normal(0, 0.5)
    out = rg.ajuste_ou(pd.Series(x), dt=1 / 52)
    assert out["m"] == pytest.approx(20.0, abs=0.3)
    assert out["eta"] == pytest.approx(-np.log(0.9) * 52, rel=0.15)
    assert out["vida_media_anios"] == pytest.approx(np.log(2) / out["eta"])
    assert out["sigma"] == pytest.approx(0.5 * np.sqrt(52), rel=0.05)


def test_ou_sin_reversion_da_nan():
    x = pd.Series(1.1 ** np.arange(50, dtype=float))
    assert np.isnan(rg.ajuste_ou(x)["eta"])


def test_merton_ejemplo_hull_y_consistencia():
    out = rg.merton(E=3.0, sigma_E=0.80, D=10.0, r=0.05, T=1.0)   # Hull: V≈12.40, σV≈0.2123, PD≈12.7%
    assert out["V"] == pytest.approx(12.40, rel=0.01)
    assert out["sigma_V"] == pytest.approx(0.2123, rel=0.02)
    assert out["pd"] == pytest.approx(0.127, abs=0.01)
    d1 = out["d2"] + out["sigma_V"]
    E_rec = out["V"] * norm.cdf(d1) - 10.0 * np.exp(-0.05) * norm.cdf(out["d2"])
    assert E_rec == pytest.approx(3.0, rel=1e-4)


@pytest.mark.parametrize("kwargs", [
    dict(E=0.0, sigma_E=0.80, D=10.0, r=0.05, T=1.0),
    dict(E=3.0, sigma_E=-0.1, D=10.0, r=0.05, T=1.0),
    dict(E=3.0, sigma_E=0.80, D=0.0, r=0.05, T=1.0),
    dict(E=3.0, sigma_E=0.80, D=10.0, r=0.05, T=0.0),
])
def test_merton_entradas_invalidas_dan_nan(kwargs):
    out = rg.merton(**kwargs)
    assert all(np.isnan(out[k]) for k in ("V", "sigma_V", "d2", "pd"))
