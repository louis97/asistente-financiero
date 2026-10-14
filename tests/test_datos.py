import numpy as np
import pandas as pd
import pytest

from asistente import datos

FECHAS = pd.date_range("2020-01-03", periods=3, freq="W-FRI")


def _raw_multiindex():
    cols = pd.MultiIndex.from_product([["Close", "Volume"], ["AAPL", "KO"]])
    vals = np.array([[10, 50, 100, 500], [11, 51, 110, 510], [12, 52, 120, 520]], dtype=float)
    return pd.DataFrame(vals, index=FECHAS, columns=cols)


def test_formato_largo_multiindex():
    largo, faltantes = datos.a_formato_largo(_raw_multiindex(), ["AAPL", "KO"])
    assert list(largo.columns) == ["fecha", "ticker", "close", "volume"]
    assert len(largo) == 6 and faltantes == []
    fila = largo[(largo.ticker == "KO") & (largo.fecha == FECHAS[1])].iloc[0]
    assert fila.close == 51 and fila.volume == 510


def test_formato_largo_columnas_planas_un_ticker():
    raw = pd.DataFrame({"Close": [1.0, 2.0, 3.0], "Volume": [5.0, 6.0, 7.0]}, index=FECHAS)
    largo, faltantes = datos.a_formato_largo(raw, ["SPY"])
    assert set(largo.ticker) == {"SPY"} and len(largo) == 3 and faltantes == []


def test_ticker_sin_datos_se_reporta_como_faltante():
    raw = _raw_multiindex()
    raw[("Close", "KO")] = np.nan
    raw[("Volume", "KO")] = np.nan
    largo, faltantes = datos.a_formato_largo(raw, ["AAPL", "KO", "ZZZZ"])
    assert set(largo.ticker) == {"AAPL"}
    assert faltantes == ["KO", "ZZZZ"]


def test_raw_vacio_no_falla():
    largo, faltantes = datos.a_formato_largo(pd.DataFrame(), ["AAPL"])
    assert largo.empty and faltantes == ["AAPL"]


def test_a_ancho():
    largo, _ = datos.a_formato_largo(_raw_multiindex(), ["AAPL", "KO"])
    ancho = datos.a_ancho(largo)
    assert list(ancho.columns) == ["AAPL", "KO"] and ancho.loc[FECHAS[2], "AAPL"] == 12


def test_snapshot_ida_y_vuelta(tmp_path):
    largo, _ = datos.a_formato_largo(_raw_multiindex(), ["AAPL", "KO"])
    ruta = datos.guardar_snapshot(largo, "precios_test", directorio=tmp_path)
    assert ruta.exists() and (tmp_path / "precios_test.meta.json").exists()
    pd.testing.assert_frame_equal(datos.cargar_snapshot("precios_test", directorio=tmp_path), largo)


def test_splits_a_df_reshape_y_tz_naive():
    idx = pd.DatetimeIndex(["2020-08-31", "2014-06-09"]).tz_localize("America/New_York")
    out = datos.splits_a_df({"AAPL": pd.Series([4.0, 7.0], index=idx), "KO": pd.Series([], dtype=float)})
    assert list(out.columns) == ["ticker", "fecha", "ratio"]
    assert len(out) == 2 and set(out.ticker) == {"AAPL"}
    assert out.fecha.dt.tz is None
    assert out.loc[out.fecha == "2020-08-31", "ratio"].iloc[0] == 4.0


def test_splits_a_df_vacio():
    out = datos.splits_a_df({"KO": pd.Series([], dtype=float)})
    assert out.empty and list(out.columns) == ["ticker", "fecha", "ratio"]


def test_formato_largo_ignora_adj_close_y_open():
    cols = pd.MultiIndex.from_product([["Adj Close", "Close", "Open", "Volume"], ["AAPL"]])
    raw = pd.DataFrame(np.array([[1, 10, 5, 100], [2, 11, 6, 110]], dtype=float),
                       index=FECHAS[:2], columns=cols)
    largo, faltantes = datos.a_formato_largo(raw, ["AAPL"])
    assert list(largo.columns) == ["fecha", "ticker", "close", "volume"]
    assert list(largo.close) == [10.0, 11.0] and faltantes == []


def test_descargar_precios_sin_ajuste_dividendos(monkeypatch):
    import sys, types
    llamadas = {}
    def fake_download(*a, **k):
        llamadas.update(k)
        return _raw_multiindex()
    monkeypatch.setitem(sys.modules, "yfinance", types.SimpleNamespace(download=fake_download))
    datos.descargar_precios(["AAPL", "KO"], "2020-01-01", ajuste_dividendos=False)
    assert llamadas["auto_adjust"] is False
    datos.descargar_precios(["AAPL", "KO"], "2020-01-01")
    assert llamadas["auto_adjust"] is True
