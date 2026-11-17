"""Persistencia de decisiones y niveles del usuario: Supabase si hay SUPABASE_URL y SUPABASE_KEY, memoria si no.

Toda consulta de Supabase filtra por el alias autenticado (nunca por el cuerpo ni la ruta). Cualquier fallo de red o
de Supabase se convierte en ErrorBaseDatos (503); la clave no se imprime ni se registra.
"""
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
        # timeout de 10 s y sin reintentos: una base caída debe fallar rápido (503), no colgar la API
        self._c = create_client(url, key, options=SyncClientOptions(postgrest_client_timeout=10, postgrest_client_retry=False))

    def _ejecutar(self, consulta, procesar):
        """Ejecuta y procesa la respuesta dentro del mismo try: cualquier falla (red, HTTP, cuerpo inesperado) es ErrorBaseDatos."""
        try:
            return procesar(consulta.execute().data)
        except Exception as e:
            log.warning("Fallo de Supabase: %s", type(e).__name__)   # solo el tipo: el mensaje podría traer la URL
            raise ErrorBaseDatos from None

    def crear_decision(self, alias, ticker, nivel, lectura, nota):
        return self._ejecutar(self._c.table("decisiones").insert(
            {"alias": alias, "ticker": ticker, "nivel": nivel, "lectura": lectura, "nota": nota}), lambda filas: _decision(filas[0]))

    def listar_decisiones(self, alias):
        return self._ejecutar(self._c.table("decisiones").select("*").eq("alias", alias).order("fecha", desc=True).order("id", desc=True),
                              lambda filas: [_decision(f) for f in filas])

    def leer_niveles(self, alias, ticker):
        return self._ejecutar(self._c.table("niveles_usuario").select("ticker,entradas,salidas,actualizado")
                              .eq("alias", alias).eq("ticker", ticker).limit(1),
                              lambda filas: _niveles(filas[0]) if filas else None)

    def guardar_niveles(self, alias, ticker, entradas, salidas):
        fila = {"alias": alias, "ticker": ticker, "entradas": entradas, "salidas": salidas,
                "actualizado": datetime.now(timezone.utc).isoformat()}
        return self._ejecutar(self._c.table("niveles_usuario").upsert(fila, on_conflict="alias,ticker"), lambda filas: _niveles(filas[0]))

    def ping(self):
        """Consulta SQL real a la tabla `salud` (una fila que solo ve la clave de servicio): sin permisos RLS filtra a [] y da False."""
        try:
            datos = self._c.table("salud").select("id").limit(1).execute().data
            return isinstance(datos, list) and len(datos) > 0
        except Exception:
            return False



class RepositorioCaido(Repositorio):
    """Se usa si no se pudo construir el cliente (URL o clave inválidas): la API arranca y responde 503."""

    def ping(self):
        return False

    def _caido(self, *a, **k):
        raise ErrorBaseDatos

    crear_decision = listar_decisiones = leer_niveles = guardar_niveles = _caido


def _niveles(f: dict) -> dict:
    return {k: f[k] for k in ("ticker", "entradas", "salidas", "actualizado")}


def _decision(f: dict) -> dict:
    return {"id": f["id"], "fecha": f["fecha"], "ticker": f["ticker"], "nivel": f["nivel"],
            "lectura": f.get("lectura") or {}, "nota": f.get("nota") or ""}


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
