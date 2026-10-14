import numpy as np
import pandas as pd
import pytest

from asistente import simulacion as sim

IDX = pd.date_range("2015-01-02", periods=300, freq="W-FRI")


def test_gbm_barreras_simetricas_cerca_de_mitad():
    p = sim.prob_triple_barrera_gbm(sigma=0.03, k_inf=0.25, k_sup=0.25, n=12, n_sims=20000, semilla=1)
    assert 0.40 < p < 0.60


def test_gbm_barrera_lejana_casi_cero_y_reproducible():
    p1 = sim.prob_triple_barrera_gbm(0.03, k_inf=4, k_sup=1, n=12, semilla=3)
    p2 = sim.prob_triple_barrera_gbm(0.03, k_inf=4, k_sup=1, n=12, semilla=3)
    assert p1 < 0.02 and p1 == p2


def test_prob_alcanzar():
    tray = np.array([[1.0, 1.2, 1.1], [1.0, 0.9, 0.8], [1.0, 1.05, 1.0]])
    assert sim.prob_alcanzar(tray, 1.1) == pytest.approx(1 / 3)
    assert sim.prob_alcanzar(tray, 0.85) == pytest.approx(1 / 3)


def test_indice_unico_sin_sector_y_sin_residuo_es_plano():
    retf = pd.Series(np.random.default_rng(0).normal(0, 0.02, 300), index=IDX)
    ract = 1.2 * (retf - retf.mean())                 # α ≈ 0, ε = 0, sector con media 0
    tray = sim.simular_indice_unico(ract, retf, n=10, n_sims=500, semilla=0, con_sector=False)
    assert tray.shape == (500, 10)
    assert np.allclose(tray, 1.0, atol=1e-9)


def test_indice_unico_con_sector_tiene_dispersion():
    retf = pd.Series(np.random.default_rng(0).normal(0, 0.02, 300), index=IDX)
    ract = 1.2 * retf
    tray = sim.simular_indice_unico(ract, retf, n=10, n_sims=500, semilla=0)
    assert tray[:, -1].std() > 0.01
