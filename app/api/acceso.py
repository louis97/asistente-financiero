"""Acceso por alias y código: X-Alias y X-Codigo contra los sha256 del secreto CODIGOS_HASH (JSON alias -> hash hex).

El código nunca se guarda ni se registra. Los tres fallos (falta un encabezado, alias desconocido, código errado)
responden el mismo 401 con el mismo cuerpo, y siempre se calcula un sha256 y una comparación en tiempo constante.
ACCESO_ABIERTO=1 (solo uso local) vale únicamente si CODIGOS_HASH no está definido.
"""
import hashlib
import hmac
import json
import logging
import os

from fastapi import Header, HTTPException

log = logging.getLogger("api")

_RELLENO = hashlib.sha256(b"relleno-alias-inexistente").hexdigest()   # se compara cuando el alias no existe
_cache: tuple[str | None, dict[str, str]] = (None, {})                # (texto de la variable, hashes válidos)


def _hay_hashes() -> bool:
    return bool(os.environ.get("CODIGOS_HASH"))


def _acceso_abierto() -> bool:
    return os.environ.get("ACCESO_ABIERTO") == "1" and not _hay_hashes()


def cargar_hashes() -> dict[str, str]:
    """Lee y valida CODIGOS_HASH; se recalcula si cambia la variable. Inválido o ausente: {} (todo da 401)."""
    global _cache
    crudo = os.environ.get("CODIGOS_HASH")
    if _cache[0] == crudo:
        return _cache[1]
    hashes: dict[str, str] = {}
    if crudo:
        try:
            dato = json.loads(crudo)
            if isinstance(dato, dict):
                hashes = {str(a): h.strip().lower() for a, h in dato.items() if isinstance(h, str)}
            else:
                raise ValueError
        except ValueError:
            log.warning("CODIGOS_HASH no es un JSON válido (objeto alias -> sha256); el acceso queda cerrado")
    _cache = (crudo, hashes)
    return hashes


def avisar_configuracion() -> None:
    """Se llama al arrancar: avisa (sin imprimir contenido) si el acceso quedó sin configurar o abierto."""
    if _acceso_abierto():
        log.warning("ACCESO_ABIERTO=1: la verificación del código está desactivada (solo uso local)")
        return
    if os.environ.get("ACCESO_ABIERTO") == "1":
        log.warning("ACCESO_ABIERTO=1 se ignora porque CODIGOS_HASH está definido")
    if not cargar_hashes() and not os.environ.get("CODIGOS_HASH"):
        log.warning("CODIGOS_HASH falta: las rutas protegidas responden 401")


def _no_autorizado() -> HTTPException:
    return HTTPException(status_code=401, detail="Credenciales inválidas")


def usuario_actual(x_alias: str = Header(None), x_codigo: str = Header(None)) -> str:
    alias = (x_alias or "").strip()
    if _acceso_abierto():
        if not alias:
            raise _no_autorizado()
        return alias
    esperado = cargar_hashes().get(alias, _RELLENO)
    calculado = hashlib.sha256((x_codigo or "").encode()).hexdigest()
    coincide = hmac.compare_digest(calculado.encode(), esperado.encode())
    if not (alias and x_codigo and alias in cargar_hashes() and coincide):
        raise _no_autorizado()
    return alias
