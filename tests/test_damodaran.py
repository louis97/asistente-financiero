import pandas as pd
import pytest

from asistente import damodaran as dm


def _excel_damodaran(tmp_path):
    ruta = tmp_path / "pedata.xlsx"
    filas = [["Date updated:", "2026-01-05", None],
             ["Created by:", "Aswath Damodaran", None],
             [None, None, None],
             ["Industry Name", "Number of firms", "Current PE"],
             ["Beverage (Soft)", 30, 25.1],
             ["Bank (Money Center)", 10, 11.2],
             [None, None, None]]
    pd.DataFrame(filas).to_excel(ruta, header=False, index=False)
    return ruta


def test_leer_tabla_detecta_encabezado(tmp_path):
    t = dm.leer_tabla(_excel_damodaran(tmp_path))
    assert list(t.columns) == ["industry_name", "number_of_firms", "current_pe"]
    assert len(t) == 2 and t.loc[0, "current_pe"] == pytest.approx(25.1)


def test_filas_industria(tmp_path):
    t = dm.leer_tabla(_excel_damodaran(tmp_path))
    f = dm.filas_industria(t, "consumo_defensivo")
    assert list(f["industry_name"]) == ["Beverage (Soft)"]


def test_sin_encabezado_falla_claro(tmp_path):
    ruta = tmp_path / "malo.xlsx"
    pd.DataFrame([["a", 1], ["b", 2]]).to_excel(ruta, header=False, index=False)
    with pytest.raises(ValueError, match="Industry Name"):
        dm.leer_tabla(ruta)


def test_hoja_industry_averages_y_columnas_repetidas(tmp_path):
    ruta = tmp_path / "vebitda.xlsx"
    filas = [["Industry Name", "EV/EBITDA", "EV/EBITDA"], ["Food Processing", 10.0, 12.0]]
    with pd.ExcelWriter(ruta) as w:
        pd.DataFrame([["End Game", "texto"]]).to_excel(w, sheet_name="Variables & FAQ", header=False, index=False)
        pd.DataFrame(filas).to_excel(w, sheet_name="Industry Averages", header=False, index=False)
    t = dm.leer_tabla(ruta)
    assert list(t.columns) == ["industry_name", "ev_ebitda", "ev_ebitda_2"]
    assert t.loc[0, "ev_ebitda_2"] == pytest.approx(12.0)
