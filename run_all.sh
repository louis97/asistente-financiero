#!/usr/bin/env bash
set -euo pipefail
uv sync
uv run pytest -q
for nb in notebooks/0{1,2,3,4}_*.ipynb; do
  if [[ "${RUN_DOWNLOAD:-1}" == "0" && "$nb" == notebooks/01_* ]]; then
    echo "Saltando $nb (se usan las instantáneas de data/snapshots)"; continue
  fi
  uv run jupyter nbconvert --to notebook --execute --inplace "$nb"
done
