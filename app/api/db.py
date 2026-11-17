"""Persistencia de decisiones y niveles del usuario. Aquí solo hay la implementación en memoria (la Tarea 07 agrega Supabase)."""
import threading
from datetime import datetime, timezone


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


_repo: Repositorio | None = None


def obtener_repositorio() -> Repositorio:
    """Aquí siempre la memoria; la Tarea 07 devuelve la de Supabase cuando hay SUPABASE_URL."""
    global _repo
    if _repo is None:
        _repo = RepositorioMemoria()
    return _repo
