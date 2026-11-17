"""Herramienta de operación: calcula el sha256 de un código de acceso para el secreto CODIGOS_HASH.

Uso: uv run python scripts/generar_hash_codigo.py <alias>
Pide el código sin eco (getpass) y dos veces en una terminal; si no es terminal, lo lee de la entrada estándar.
Imprime solo  "<alias>": "<hash>"  (para pegar dentro del JSON de CODIGOS_HASH). No escribe archivos ni imprime el código.
"""
import getpass
import hashlib
import sys

if len(sys.argv) != 2 or not sys.argv[1].strip():
    sys.exit("Uso: python scripts/generar_hash_codigo.py <alias>")
alias = sys.argv[1].strip()

if sys.stdin.isatty():
    codigo = getpass.getpass("Código: ")
    if codigo != getpass.getpass("Repita el código: "):
        sys.exit("Los códigos no coinciden.")
else:
    codigo = sys.stdin.readline().rstrip("\n")

if not codigo:
    sys.exit("El código está vacío.")
if len(codigo) < 12:
    print("Aviso: el código tiene menos de 12 caracteres; use uno más largo.", file=sys.stderr)
print(f'"{alias}": "{hashlib.sha256(codigo.encode()).hexdigest()}"')
