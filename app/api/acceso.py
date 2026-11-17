"""Acceso mínimo (la Tarea 07 lo reemplaza manteniendo la firma de `usuario_actual`).

Nunca queda abierto por omisión: sin ACCESO_ABIERTO=1 responde 401 siempre; con ACCESO_ABIERTO=1 y sin CODIGOS_HASH
no se verifica el código, pero el alias es obligatorio (aísla los datos por usuario).
"""
import os

from fastapi import Header, HTTPException


def usuario_actual(x_alias: str = Header(None), x_codigo: str = Header(None)) -> str:
    if os.environ.get("ACCESO_ABIERTO") != "1" or os.environ.get("CODIGOS_HASH"):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    alias = (x_alias or "").strip()
    if not alias:
        raise HTTPException(status_code=401, detail="Falta el alias (encabezado X-Alias)")
    return alias
