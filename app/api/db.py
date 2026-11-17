"""Persistencia de decisiones y niveles del usuario: Supabase si hay SUPABASE_URL y SUPABASE_KEY, memoria si no.

Toda consulta de Supabase filtra por el alias autenticado (nunca por el cuerpo ni la ruta). Cualquier fallo de red o
de Supabase se convierte en ErrorBaseDatos (503); la clave no se imprime ni se registra.
"""
import base64
import json
import logging
import os
import threading
from datetime import datetime, timezone

log = logging.getLogger("api")


class ErrorBaseDatos(Exception):
    """La base de datos no responde o falló; la API la convierte en 503."""


class Repositorio:
    """Interfaz: todas las operaciones están aisladas por alias."""

    def crear_decision(self, alias: str, ticker: str, nivel: str, lectura: dict, nota: str) -> dict: ...
    def listar_decisiones(self, alias: str) -> list[dict]: ...
    def leer_niveles(self, alias: str, ticker: str) -> dict | None: ...
    def guardar_niveles(self, alias: str, ticker: str, entradas: list, salidas: list) -> dict: ...
    def ping(self) -> bool: ...


class RepositorioMemoria(Repositorio):
    """Vive mientras viva el proceso (Render puede reiniciarlo en cualquier momento)."""

    def __init__(self):
        self._lock = threading.Lock()
        self._decisiones: list[dict] = []
        self._niveles: dict[tuple[str, str], dict] = {}

    def crear_decision(self, alias, ticker, nivel, lectura, nota):
        with self._lock:
            fila = {"id": len(self._decisiones) + 1, "alias": alias, "fecha": datetime.now(timezone.utc).isoformat(),
                    "ticker": ticker, "nivel": nivel, "lectura": lectura, "nota": nota}
            self._decisiones.append(fila)
            return dict(fila)

    def listar_decisiones(self, alias):
        with self._lock:
            return [dict(f) for f in reversed(self._decisiones) if f["alias"] == alias]

    def leer_niveles(self, alias, ticker):
        with self._lock:
            fila = self._niveles.get((alias, ticker))
            return dict(fila) if fila else None

    def guardar_niveles(self, alias, ticker, entradas, salidas):
        with self._lock:
            fila = {"ticker": ticker, "entradas": entradas, "salidas": salidas,
                    "actualizado": datetime.now(timezone.utc).isoformat()}
            self._niveles[(alias, ticker)] = fila
            return dict(fila)

    def ping(self):
        return True


class RepositorioSupabase(Repositorio):
    """Tablas `decisiones` y `niveles_usuario` (app/api/supabase.sql), con la clave del rol de servicio."""

    def __init__(self, url: str, key: str):
        from supabase import create_client                       # import perezoso: la memoria no lo necesita
        from supabase.lib.client_options import SyncClientOptions
        _rechazar_clave_publica(key)
        # timeout de 10 s y sin reintentos: una base caída debe fallar rápido (503), no colgar la API
        self._c = create_client(url, key, options=SyncClientOptions(postgrest_client_timeout=10, postgrest_client_retry=False))

    def _ejecutar(self, consulta):
        try:
            return consulta.execute().data
        except Exception as e:                                   # red, 4xx/5xx de PostgREST, JSON inesperado
            log.warning("Fallo de Supabase: %s", type(e).__name__)   # solo el tipo: el mensaje podría traer la URL
            raise ErrorBaseDatos from None

    def crear_decision(self, alias, ticker, nivel, lectura, nota):
        filas = self._ejecutar(self._c.table("decisiones").insert(
            {"alias": alias, "ticker": ticker, "nivel": nivel, "lectura": lectura, "nota": nota}))
        return _decision(filas[0])

    def listar_decisiones(self, alias):
        filas = self._ejecutar(self._c.table("decisiones").select("*").eq("alias", alias).order("fecha", desc=True).order("id", desc=True))
        return [_decision(f) for f in filas]

    def leer_niveles(self, alias, ticker):
        filas = self._ejecutar(self._c.table("niveles_usuario").select("ticker,entradas,salidas,actualizado")
                               .eq("alias", alias).eq("ticker", ticker).limit(1))
        return {k: filas[0][k] for k in ("ticker", "entradas", "salidas", "actualizado")} if filas else None

    def guardar_niveles(self, alias, ticker, entradas, salidas):
        fila = {"alias": alias, "ticker": ticker, "entradas": entradas, "salidas": salidas,
                "actualizado": datetime.now(timezone.utc).isoformat()}
        filas = self._ejecutar(self._c.table("niveles_usuario").upsert(fila, on_conflict="alias,ticker"))
        return {k: filas[0][k] for k in ("ticker", "entradas", "salidas", "actualizado")}

    def ping(self):
        try:
            self._c.table("niveles_usuario").select("alias").limit(1).execute()
            return True
        except Exception:
            return False


class RepositorioCaido(Repositorio):
    """Se usa si no se pudo construir el cliente (URL o clave inválidas): la API arranca y responde 503."""

    def ping(self):
        return False

    def _caido(self, *a, **k):
        raise ErrorBaseDatos

    crear_decision = listar_decisiones = leer_niveles = guardar_niveles = _caido


def _decision(f: dict) -> dict:
    return {"id": f["id"], "fecha": f["fecha"], "ticker": f["ticker"], "nivel": f["nivel"],
            "lectura": f.get("lectura") or {}, "nota": f.get("nota") or ""}


def _rechazar_clave_publica(key: str) -> None:
    """La clave pública (anon) no lee nada por RLS: se rechaza al construir para que /estado diga supabase_ok: false."""
    if key.startswith("sb_publishable_"):
        raise ValueError("clave pública")
    try:
        carga = key.split(".")[1]
        rol = json.loads(base64.urlsafe_b64decode(carga + "=" * (-len(carga) % 4))).get("role")
    except Exception:
        return                                                   # no es un JWT (clave nueva del servicio): no hay nada que revisar
    if rol == "anon":
        raise ValueError("clave pública")


_repo: Repositorio | None = None


def obtener_repositorio() -> Repositorio:
    """Supabase si hay SUPABASE_URL y SUPABASE_KEY; si no, la memoria. Si el cliente no se puede construir, uno 'caído'."""
    global _repo
    if _repo is None:
        url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
        if url and key:
            try:
                _repo = RepositorioSupabase(url, key)
            except Exception as e:
                log.warning("No se pudo crear el cliente de Supabase: %s", type(e).__name__)
                _repo = RepositorioCaido()
        else:
            _repo = RepositorioMemoria()
    return _repo
