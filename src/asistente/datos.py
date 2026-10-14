"""Descarga de precios con yfinance e instantáneas parquet reproducibles."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from asistente import config

_COLUMNAS = ["fecha", "ticker", "close", "volume"]


def a_formato_largo(raw: pd.DataFrame, tickers: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Convierte la salida de yf.download (MultiIndex o plana) a formato largo.

    Un ticker sin ningún precio válido se reporta como faltante y no aparece en el resultado.
    """
    if raw is None or raw.empty:
        return pd.DataFrame(columns=_COLUMNAS), list(tickers)
    if isinstance(raw.columns, pd.MultiIndex):
        partes = []
        for t in tickers:
            if ("Close", t) not in raw.columns:
                continue
            partes.append(pd.DataFrame({
                "fecha": raw.index, "ticker": t,
                "close": raw[("Close", t)].to_numpy(),
                "volume": raw[("Volume", t)].to_numpy() if ("Volume", t) in raw.columns else float("nan"),
            }))
        largo = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=_COLUMNAS)
    else:
        largo = pd.DataFrame({"fecha": raw.index, "ticker": tickers[0],
                              "close": raw["Close"].to_numpy(), "volume": raw["Volume"].to_numpy()})
    largo = largo.dropna(subset=["close"]).reset_index(drop=True)
    presentes = set(largo["ticker"])
    faltantes = [t for t in tickers if t not in presentes]
    return largo[_COLUMNAS], faltantes


def descargar_precios(tickers: list[str], inicio: str, fin: str | None = None,
                      intervalo: str = "1wk") -> tuple[pd.DataFrame, list[str]]:
    import yfinance as yf
    raw = yf.download(tickers, start=inicio, end=fin, interval=intervalo,
                      auto_adjust=True, progress=False, group_by="column")
    return a_formato_largo(raw, tickers)


def a_ancho(df_largo: pd.DataFrame, campo: str = "close") -> pd.DataFrame:
    return df_largo.pivot(index="fecha", columns="ticker", values=campo).sort_index()


def guardar_snapshot(df: pd.DataFrame, nombre: str, directorio: Path | None = None) -> Path:
    directorio = Path(directorio or config.DIR_SNAPSHOTS)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{nombre}.parquet"
    df.to_parquet(ruta, index=False)
    meta = {"nombre": nombre, "filas": len(df),
            "fecha_descarga": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (directorio / f"{nombre}.meta.json").write_text(json.dumps(meta, indent=2))
    return ruta


def cargar_snapshot(nombre: str, directorio: Path | None = None) -> pd.DataFrame:
    directorio = Path(directorio or config.DIR_SNAPSHOTS)
    return pd.read_parquet(directorio / f"{nombre}.parquet")
