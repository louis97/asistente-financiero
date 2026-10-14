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
