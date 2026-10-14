import numpy as np
import pandas as pd
import pytest

from asistente import edgar
from asistente import fundamentales as fu


def _ratios():
    return pd.DataFrame({
        "end": pd.to_datetime(["2019-12-31", "2020-12-31"]),
        "filed": pd.to_datetime(["2020-02-10", "2021-02-10"]),
        "utilidad_neta": [10.0, -5.0], "acciones": [10.0, 10.0], "patrimonio": [100.0, 90.0],
        "ingresos": [200.0, 180.0], "utilidad_bruta": [np.nan, np.nan], "utilidad_operativa": [20.0, 5.0],
        "deuda_lp": [50.0, 50.0], "caja": [10.0, 10.0], "cfo": [30.0, 20.0], "capex": [10.0, 10.0],
    })


def test_ratios_basicos_y_concepto_ausente_nan():
    r = fu.ratios_anuales(_ratios())
    assert r.loc[0, "roe"] == pytest.approx(0.10)
    assert r.loc[0, "eps"] == pytest.approx(1.0) and r.loc[0, "bvps"] == pytest.approx(10.0)
    assert np.isnan(r.loc[0, "margen_bruto"])          # utilidad bruta ausente → NaN, no 0
    assert r.loc[0, "roic"] == pytest.approx(20 * 0.79 / (100 + 50 - 10))


def test_pe_con_eps_negativo_es_nan_y_sin_look_ahead():
    r = fu.ratios_anuales(_ratios())
    precios = pd.DataFrame({"fecha": pd.to_datetime(["2020-01-31", "2020-06-26", "2021-06-25"]),
                            "close": [15.0, 20.0, 30.0]})
    m = fu.multiplos_semanales(precios, r)
    assert np.isnan(m.loc[0, "pe"])                    # antes del primer filed
    assert m.loc[1, "pe"] == pytest.approx(20.0)       # 20 / EPS 1
    assert np.isnan(m.loc[2, "pe"])                    # EPS 2020 = -0.5 → P/E sin sentido (T2)
    assert m.loc[2, "pb"] == pytest.approx(30 / 9.0)


def test_percentil_expansivo_no_mira_al_futuro():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 0.0])
    p = fu.percentil_expansivo(s, min_obs=3)
    assert p.iloc[:2].isna().all()
    assert p.iloc[3] == pytest.approx(1.0)             # 4 es el máximo de su historia hasta t=3
    assert p.iloc[4] == pytest.approx(0.2)             # 0 es el mínimo de 5 → 1/5
    s2 = pd.concat([s, pd.Series([100.0])], ignore_index=True)
    assert fu.percentil_expansivo(s2, 3).iloc[3] == p.iloc[3]   # un dato futuro no cambia el pasado


def test_percentil_en_grupo_y_relativo():
    ancho = pd.DataFrame({"A": [10.0, 30.0], "B": [20.0, 20.0], "C": [30.0, np.nan]})
    pg = fu.percentil_en_grupo(ancho)
    assert pg.loc[0, "C"] == pytest.approx(1.0) and np.isnan(pg.loc[1, "C"])
    rel = fu.multiplo_relativo(ancho)
    assert rel.loc[0, "A"] == pytest.approx(0.5) and rel.loc[1, "A"] == pytest.approx(30 / 25)


COMPANYFACTS_PARCIAL = {"facts": {"us-gaap": {
    "Revenues": {"units": {"USD": [
        {"val": 100, "end": "2019-12-31", "filed": "2020-02-10", "start": "2019-01-01", "form": "10-K", "fp": "FY"},
        {"val": 120, "end": "2020-12-31", "filed": "2021-02-10", "start": "2020-01-01", "form": "10-K", "fp": "FY"},
    ]}},
    "NetIncomeLoss": {"units": {"USD": [
        {"val": 10, "end": "2019-12-31", "filed": "2020-02-15", "start": "2019-01-01", "form": "10-K", "fp": "FY"},
    ]}},
}}}


def test_tabla_anual_concepto_ausente_es_nan_y_tiene_filed():
    hechos = edgar.hechos_a_df(COMPANYFACTS_PARCIAL)
    t = fu.tabla_anual(hechos)
    assert "filed" in t.columns
    for concepto in edgar.CONCEPTOS:
        assert concepto in t.columns
    assert t["patrimonio"].isna().all()                # ausente → NaN, nunca 0
    assert t["ingresos"].notna().all()
    fila_2019 = t[t["end"] == pd.Timestamp("2019-12-31")].iloc[0]
    assert fila_2019["filed"] == pd.Timestamp("2020-02-15")  # la última publicación entre conceptos del año


def _r(filed):
    return pd.DataFrame({"filed": pd.to_datetime(filed), "eps": [8.0, 8.0],
                         "bvps": [40.0, 40.0], "acciones": [100.0, 100.0]})


def _sp(*pares):
    return pd.DataFrame({"fecha": pd.to_datetime([p[0] for p in pares]), "ratio": [p[1] for p in pares]})


def test_ajustar_por_splits_posterior_divide():
    out = fu.ajustar_por_splits(_r(["2020-02-01", "2021-02-01"]), _sp(("2020-08-31", 4.0)))
    assert out.eps.tolist() == [2.0, 8.0] and out.bvps.tolist() == [10.0, 40.0]
    assert out.acciones.tolist() == [400.0, 100.0]


def test_ajustar_por_splits_compuesto_y_nan():
    r = _r(["2020-02-01", "2021-02-01"]); r.loc[0, "eps"] = np.nan
    out = fu.ajustar_por_splits(r, _sp(("2020-08-31", 2.0), ("2021-06-01", 3.0)))
    assert np.isnan(out.eps[0]) and out.eps[1] == pytest.approx(8 / 3)
    assert out.bvps[0] == pytest.approx(40 / 6)


def test_ajustar_por_splits_sin_splits_no_muta():
    r = _r(["2020-02-01", "2021-02-01"])
    out = fu.ajustar_por_splits(r, _sp())
    pd.testing.assert_frame_equal(out, r)
    assert out is not r
