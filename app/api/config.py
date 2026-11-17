"""Configuración de la API: rutas, variables de entorno y acceso a `notebooks/comunes.py`.

Los secretos (SEC_USER_AGENT, SUPABASE_KEY, CODIGOS_HASH) se leen SOLO del entorno; nunca se escriben en archivos.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# `import comunes` (la fuente única de constantes y funciones del modelo y de los datos)
if str(ROOT / "notebooks") not in sys.path:
    sys.path.insert(0, str(ROOT / "notebooks"))

# Carpeta de datos pedida (relativa a ROOT si no es absoluta). Si no existe o le falta un archivo, `datos.py`
# usa DIR_SNAPSHOTS y lo informa en `fuente_datos` de /estado.
DATA_DIR = ROOT / os.environ.get("DATA_DIR", "data/produccion")
DIR_SNAPSHOTS = ROOT / "data" / "snapshots"
MODELO_DIR = ROOT / os.environ["MODELO_DIR"] if os.environ.get("MODELO_DIR") else ROOT / "app" / "modelo"

SEC_USER_AGENT = os.environ.get("SEC_USER_AGENT")            # sin él no se consulta EDGAR a demanda
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]

CACHE_HORAS = 24                                             # caché de las descargas a demanda (fuera de la piloto)
LIMITE_PING_S = 3                                            # límite de la consulta de keep-alive a la base de datos
SESIONES_SERIE = 1260                                        # ≈ 5 años de sesiones para el gráfico
