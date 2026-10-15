#!/usr/bin/env bash
set -euo pipefail
# Por defecto NO descarga: el notebook 01 se ejecuta siempre y usa las instantáneas de data/snapshots.
# RUN_DOWNLOAD=1 vuelve a descargar los datos dentro del kernel y exige SEC_USER_AGENT.
[[ "${RUN_DOWNLOAD:-0}" == 1 && -z "${SEC_USER_AGENT:-}" ]] && { echo "Falta SEC_USER_AGENT"; exit 1; }
export RUN_DOWNLOAD="${RUN_DOWNLOAD:-0}"
uv sync
for nb in notebooks/0{1,2,3,4}_*.ipynb; do
  uv run jupyter nbconvert --to notebook --execute --inplace "$nb"
done
uv run python scripts/mockup.py
