from asistente import config


def test_universo_tiene_tres_industrias_de_diez():
    assert set(config.UNIVERSO) == {"tecnologia", "consumo_defensivo", "financiero"}
    assert all(len(v) == 10 for v in config.UNIVERSO.values())


def test_cada_industria_tiene_etf():
    assert config.ETF_SECTOR == {"tecnologia": "XLK", "consumo_defensivo": "XLP", "financiero": "XLF"}


def test_tickers_y_industria_de():
    ts = config.tickers()
    assert len(ts) == 30 and len(set(ts)) == 30
    assert config.industria_de("KO") == "consumo_defensivo"


def test_industria_de_ticker_desconocido():
    import pytest
    with pytest.raises(KeyError):
        config.industria_de("ZZZZ")
