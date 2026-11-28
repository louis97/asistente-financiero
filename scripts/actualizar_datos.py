"""Tarea diaria: refresca `data/produccion/` (precios con y sin ajuste por dividendos, splits, ratios TTM, estado y latencia) y no toca nada si algo falla.

Uso (sin argumentos):  SEC_USER_AGENT="<nombre y correo>" uv run python scripts/actualizar_datos.py

Solo orquesta: la descarga y el cálculo viven en `notebooks/comunes.py` (una sola fuente).
Los precios semanales sin ajuste por dividendos (`precios_semanales_sd`) y los splits (`splits`) alimentan los múltiplos y percentiles de la API;
si faltan en la carpeta (producción anterior a este cambio) se descargan y se escriben sin sembrar nada: la siembra solo ocurre si faltan los tres parquet básicos.
Variables de entorno: DATA_DIR (por defecto data/produccion) y SEC_USER_AGENT (obligatoria; su valor nunca se imprime ni se guarda).
Códigos de salida: 0 = bien (con o sin cambios, o recién sembrado); 1 = falló (la carpeta de datos queda intacta).
"""
import io
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "notebooks"))
import comunes as cm  # noqa: E402

PARQUETS = ["precios_diarios", "precios_semanales", "ratios_ttm"]          # básicos: si falta alguno, se siembra
PARQUETS_NUEVOS = ["precios_semanales_sd", "splits"]                        # se refrescan igual, pero su ausencia no dispara la siembra
COLS_LATENCIA = ["ticker", "form", "filed", "fecha_recalculo", "dias"]
MIN_FILAS = 0.99                       # una descarga con menos del 99 % de las filas actuales se trata como falla


class Falla(Exception):
    """Falla de una fuente; el mensaje nombra cuál."""


def hoy_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def ahora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def escribir_atomico(destino: Path, escribir) -> Path:
    """Escribe en `<destino>.tmp` (mismo directorio, para que os.replace sea atómico). Devuelve la ruta temporal."""
    tmp = destino.with_name(destino.name + ".tmp")
    escribir(tmp)
    return tmp


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Mismo formato que al leer un parquet (ida y vuelta), para comparar sin diferencias de tipo."""
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    out = pd.read_parquet(buf)
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].astype("datetime64[ns]")
        elif pd.api.types.is_string_dtype(out[c]):
            out[c] = out[c].astype(object)
    return out.reset_index(drop=True)


def igual(a: pd.DataFrame, b: pd.DataFrame) -> bool:
    try:
        pd.testing.assert_frame_equal(normalizar(a), normalizar(b), check_dtype=False)
        return True
    except AssertionError:
        return False


def sembrar(dir_datos: Path) -> bool:
    """Copia la instantánea si falta algún parquet básico. Devuelve True si sembró (y entonces el script termina).

    Solo los básicos disparan la siembra. Si faltan únicamente `precios_semanales_sd` o `splits`, no se siembra: así no se
    sobrescriben los precios y ratios actuales con los de la instantánea; `main` los descarga y los escribe como cualquier cambio.
    En una siembra completa, de los nuevos solo se copian los que faltan."""
    if all((dir_datos / f"{n}.parquet").exists() for n in PARQUETS):
        return False
    dir_datos.mkdir(parents=True, exist_ok=True)
    copiar = PARQUETS + [n for n in PARQUETS_NUEVOS if not (dir_datos / f"{n}.parquet").exists()]
    tmps = []
    try:
        for n in copiar:
            tmps.append((escribir_atomico(dir_datos / f"{n}.parquet", lambda t, n=n: shutil.copyfile(cm.DIR_SNAPSHOTS / f"{n}.parquet", t)), dir_datos / f"{n}.parquet"))
        px = pd.read_parquet(cm.DIR_SNAPSHOTS / "precios_diarios.parquet", columns=["fecha"])
        estado = {"ultimo_dato": px.fecha.max().strftime("%Y-%m-%d"), "ultimo_recalculo": ahora_utc(),
                  "fuentes_ok": {"yfinance": True, "edgar": True}, "primera_ejecucion": hoy_utc()}
        tmps.append((escribir_atomico(dir_datos / "latencia.csv", lambda t: pd.DataFrame(columns=COLS_LATENCIA).to_csv(t, index=False)), dir_datos / "latencia.csv"))
        tmps.append((escribir_atomico(dir_datos / "estado.json", lambda t: t.write_text(json.dumps(estado, indent=2), encoding="utf-8")), dir_datos / "estado.json"))
        for tmp, destino in tmps:      # estado.json va al final
            os.replace(tmp, destino)
    finally:
        for tmp, _ in tmps:
            tmp.unlink(missing_ok=True)
    print(f"Siembra: copiados {', '.join(copiar)} desde data/snapshots; último dato {estado['ultimo_dato']}. "
          "Sin descargas ni filas de latencia (la primera ejecución solo siembra).")
    return True


def validar_precios(nuevo: pd.DataFrame, actual: pd.DataFrame, simbolos: list[str], nombre: str, ultimo_dato: pd.Timestamp | None):
    faltan = sorted(set(simbolos) - set(nuevo.ticker))
    if faltan:
        raise Falla(f"yfinance: faltan símbolos en {nombre}: {faltan}")
    if nuevo.close.isna().any() or (nuevo.close <= 0).any():
        raise Falla(f"yfinance: {nombre} trae cierres vacíos o no positivos")
    if len(nuevo) < MIN_FILAS * len(actual):
        raise Falla(f"yfinance: {nombre} trae {len(nuevo)} filas, menos del 99 % de las {len(actual)} actuales")
    if ultimo_dato is not None and nuevo.fecha.max() < ultimo_dato:
        raise Falla(f"yfinance: la última fecha de {nombre} ({nuevo.fecha.max().date()}) es anterior al último dato bueno ({ultimo_dato.date()})")


def main() -> int:
    dir_datos = Path(os.environ.get("DATA_DIR", "data/produccion"))
    if not dir_datos.is_absolute():
        dir_datos = RAIZ / dir_datos
    if not os.environ.get("SEC_USER_AGENT"):                       # nunca se imprime su valor
        print("Falta SEC_USER_AGENT (nombre y correo, como exige la SEC); no se hizo nada.", file=sys.stderr)
        return 1

    if sembrar(dir_datos):
        return 0

    tmps = []
    try:
        estado_ant = json.loads((dir_datos / "estado.json").read_text(encoding="utf-8"))
        ultimo_dato = pd.Timestamp(estado_ant["ultimo_dato"])
        primera = estado_ant["primera_ejecucion"]
        simbolos = cm.tickers() + [cm.BENCHMARK] + list(cm.ETF_SECTOR.values())          # 21 empresas + SPY + XLP
        inicio_lunes = (pd.Timestamp(cm.INICIO) + pd.offsets.Week(weekday=0)).strftime("%Y-%m-%d")
        # Los nuevos pueden faltar en una carpeta anterior: se comparan contra la instantánea y se escriben como cambio
        actual = {n: pd.read_parquet(dir_datos / f"{n}.parquet") for n in PARQUETS}
        actual.update({n: pd.read_parquet(dir_datos / f"{n}.parquet" if (dir_datos / f"{n}.parquet").exists() else cm.DIR_SNAPSHOTS / f"{n}.parquet")
                       for n in PARQUETS_NUEVOS})
        faltan_nuevos = [n for n in PARQUETS_NUEVOS if not (dir_datos / f"{n}.parquet").exists()]

        # 3. Precios (descarga completa: el ajuste por dividendos cambia toda la historia) y validación antes de escribir
        try:
            dia, falt_d = cm.descargar_precios(simbolos, cm.INICIO, "1d")
            sem, falt_s = cm.descargar_precios(simbolos, inicio_lunes, "1wk")
            sem_sd, falt_sd = cm.descargar_precios(simbolos, inicio_lunes, "1wk", ajuste_dividendos=False)   # precio pagado, para los múltiplos
            splits = cm.descargar_splits(cm.tickers())          # una consulta que lanza error es falla; sin splits para un ticker es válido
        except Exception as e:
            raise Falla(f"yfinance: {type(e).__name__}: {str(e)[:150]}") from None
        if falt_d or falt_s or falt_sd:
            raise Falla(f"yfinance: símbolos sin precios (diario {falt_d}, semanal {falt_s}, semanal sin dividendos {falt_sd})")
        validar_precios(dia, actual["precios_diarios"], simbolos, "precios_diarios", ultimo_dato)
        validar_precios(sem, actual["precios_semanales"], simbolos, "precios_semanales", None)
        validar_precios(sem_sd, actual["precios_semanales_sd"], simbolos, "precios_semanales_sd", None)
        if len(splits) < len(actual["splits"]):                 # los splits solo se acumulan: menos filas que antes es una consulta incompleta
            raise Falla(f"yfinance: splits trae {len(splits)} filas, menos de las {len(actual['splits'])} actuales")

        # 4. EDGAR: hechos de las 21 empresas, ratios TTM recalculados y reportes nuevos para la latencia (KPI 3)
        try:
            hechos = cm.descargar_hechos_edgar(cm.tickers())
            ratios = cm.construir_ratios_ttm(hechos)
        except Exception as e:
            raise Falla(f"EDGAR: {type(e).__name__}: {str(e)[:150]}") from None
        if set(ratios.ticker) != set(cm.tickers()):
            raise Falla(f"EDGAR: faltan empresas en los ratios: {sorted(set(cm.tickers()) - set(ratios.ticker))}")

        nuevos = {"precios_diarios": dia, "precios_semanales": sem, "ratios_ttm": ratios, "precios_semanales_sd": sem_sd, "splits": splits}
        cambiaron = [n for n in PARQUETS + PARQUETS_NUEVOS if n in faltan_nuevos or not igual(nuevos[n], actual[n])]

        lat = pd.read_csv(dir_datos / "latencia.csv", dtype=str)
        lat["filed"] = pd.to_datetime(lat["filed"]).astype(hechos.filed.dtype)      # vacío o no, `filed` es fecha
        rep = (hechos[hechos.form.isin(["10-Q", "10-K"]) & (hechos.filed >= pd.Timestamp(primera))]
               [["ticker", "form", "filed"]].drop_duplicates())
        rep = rep.merge(lat[["ticker", "form", "filed"]], how="left", on=["ticker", "form", "filed"], indicator=True).query("_merge == 'left_only'").drop(columns="_merge")
        filas = rep.assign(fecha_recalculo=hoy_utc(), dias=(pd.Timestamp(hoy_utc()) - rep.filed).dt.days)[COLS_LATENCIA]

        if not cambiaron and filas.empty:
            print("Sin cambios en precios, splits, ratios ni reportes nuevos: no se escribe nada.")
            return 0

        # 5. Escritura: todo a `.tmp` primero; luego os.replace; estado.json al final
        for n in cambiaron:
            tmps.append((escribir_atomico(dir_datos / f"{n}.parquet", lambda t, n=n: nuevos[n].to_parquet(t, index=False)), dir_datos / f"{n}.parquet"))
        if not filas.empty:
            todo = pd.concat([lat.assign(filed=lat.filed.dt.strftime("%Y-%m-%d")), filas.assign(filed=filas.filed.dt.strftime("%Y-%m-%d"))], ignore_index=True)
            tmps.append((escribir_atomico(dir_datos / "latencia.csv", lambda t: todo.to_csv(t, index=False)), dir_datos / "latencia.csv"))
        estado = {"ultimo_dato": dia.fecha.max().strftime("%Y-%m-%d"), "ultimo_recalculo": ahora_utc(),
                  "fuentes_ok": {"yfinance": True, "edgar": True}, "primera_ejecucion": primera}
        tmps.append((escribir_atomico(dir_datos / "estado.json", lambda t: t.write_text(json.dumps(estado, indent=2), encoding="utf-8")), dir_datos / "estado.json"))
        for tmp, destino in tmps:
            os.replace(tmp, destino)
        print(f"Actualizado: {cambiaron or 'solo reportes'}; reportes nuevos en latencia: {len(filas)}; último dato {estado['ultimo_dato']}.")
        return 0
    except Falla as e:
        print(f"FALLA de la fuente. {e}. No se tocó {dir_datos.name}: queda el último dato bueno.", file=sys.stderr)
        return 1
    except Exception as e:                                     # cualquier otra falla (lectura, escritura, etc.)
        print(f"FALLA inesperada ({type(e).__name__}: {str(e)[:150]}). Se conserva el último dato bueno.", file=sys.stderr)
        return 1
    finally:
        for tmp, _ in tmps:                                    # ningún .tmp huérfano llega a `git add`
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
