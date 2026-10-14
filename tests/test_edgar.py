import pandas as pd
import pytest

from asistente import edgar


def _fact(val, end, filed, start=None, form="10-K", fp="FY"):
    d = {"val": val, "end": end, "filed": filed, "form": form, "fp": fp}
    if start:
        d["start"] = start
    return d


COMPANYFACTS = {"facts": {"us-gaap": {
    "Revenues": {"units": {"USD": [
        _fact(100, "2019-12-31", "2020-02-10", start="2019-01-01"),
        _fact(100, "2019-12-31", "2021-02-10", start="2019-01-01"),   # comparativo repetido en el 10-K siguiente
        _fact(30, "2020-03-31", "2020-05-01", start="2020-01-01", form="10-Q", fp="Q1"),
    ]}},
    "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        _fact(120, "2020-12-31", "2021-02-10", start="2020-01-01"),
    ]}},
    "StockholdersEquity": {"units": {"USD": [_fact(500, "2020-12-31", "2021-02-10")]}},
}}}


def test_mapa_ticker_cik_rellena_ceros():
    m = edgar.mapa_ticker_cik({"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple"}})
    assert m == {"AAPL": "0000320193"}


def test_hechos_a_df_columnas():
    df = edgar.hechos_a_df(COMPANYFACTS)
    assert {"concepto", "unidad", "start", "end", "val", "form", "fp", "filed"} <= set(df.columns)
    assert pd.api.types.is_datetime64_any_dtype(df["filed"])


def test_serie_anual_usa_alternativas_y_primer_filed():
    df = edgar.hechos_a_df(COMPANYFACTS)
    s = edgar.serie_anual(df, ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"], "USD")
    assert list(s["val"]) == [100, 120]                      # 2019 de Revenues, 2020 del nombre alternativo
    assert s.iloc[0]["filed"] == pd.Timestamp("2020-02-10")  # primera publicación, no el comparativo posterior
    assert len(s) == 2                                       # el 10-Q no entra


def test_concepto_ausente_devuelve_vacio_no_cero():
    df = edgar.hechos_a_df(COMPANYFACTS)
    s = edgar.serie_anual(df, ["GrossProfit"], "USD")
    assert s.empty


def test_alinear_por_filed_sin_look_ahead():
    precios = pd.DataFrame({"fecha": pd.to_datetime(["2021-01-15", "2021-02-12"]), "close": [10.0, 11.0]})
    fund = pd.DataFrame({"end": pd.to_datetime(["2020-12-31"]), "filed": pd.to_datetime(["2021-02-10"]),
                         "val": [120.0]})
    out = edgar.alinear_por_filed(precios, fund)
    assert pd.isna(out.loc[0, "val"])   # 15-ene: el reporte del 31-dic aún no se había publicado
    assert out.loc[1, "val"] == 120.0   # 12-feb: ya publicado (filed 10-feb)


def test_descargar_json_exige_user_agent(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(RuntimeError):
        edgar.descargar_json("https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json")
