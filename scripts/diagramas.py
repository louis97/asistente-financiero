"""Diagramas del proyecto (entrega 2). Solo matplotlib y las constantes de `notebooks/comunes.py`.

Cada diagrama es una función `diagrama_xxx(destino)`; para agregar otro basta con escribir otra función y
llamarla en `main()`. Uso: `uv run python scripts/diagramas.py`.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # sin ventana: solo guarda el PNG
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
import comunes as cm                       # constantes (N, K_GRID, BRECHA, fechas de la partición) y rutas

# Arial si está instalada; si no, DejaVu Sans (viene con matplotlib).
_FUENTES = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = "Arial" if "Arial" in _FUENTES else "DejaVu Sans"

# Paleta sobria (un color por tipo de bloque)
C_DATOS, C_PREP, C_MODELO, C_RAMA, C_PRODUCTO = "#dbe9f6", "#e3f1df", "#fdebd0", "#efe1f4", "#f6dcdc"
C_BORDE, C_TEXTO = "#4a4a4a", "#1f1f1f"


def _caja(ax, x, y, w, h, titulo, lineas, color):
    """Caja redondeada con un título en negrita y líneas de detalle; devuelve sus puntos de anclaje."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=color, ec=C_BORDE, lw=1.1))
    ax.text(x + w / 2, y + h - 0.16, titulo, ha="center", va="top", fontsize=10.5, fontweight="bold", color=C_TEXTO)
    ax.text(x + w / 2, y + h - 0.52, "\n".join(lineas), ha="center", va="top", fontsize=8.2,
            color=C_TEXTO, linespacing=1.35)
    return {"izq": (x, y + h / 2), "der": (x + w, y + h / 2), "arr": (x + w / 2, y + h), "aba": (x + w / 2, y)}


def _linea(ax, pts):
    """Polilínea sin punta (las puntas las pone _flecha en el último tramo)."""
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=C_BORDE, lw=1.4, solid_capstyle="butt")


def _flecha(ax, p, q, texto=None):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", lw=1.4, color=C_BORDE, shrinkA=0, shrinkB=0, mutation_scale=16))
    if texto:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.12, texto, ha="center", va="bottom", fontsize=8, color=C_BORDE)


def diagrama_bloques(destino):
    """Flujo de datos del proyecto: fuentes → limpieza → variables → etiqueta → partición → estandarización → modelos,
    más las ramas fundamental y de simulación que confluyen en API → dashboard."""
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 6); ax.axis("off")
    ax.text(6.5, 5.9, "Del dato a la lectura: bloques del proyecto", ha="center", va="top", fontsize=13, fontweight="bold")

    w, h, paso = 1.72, 1.55, 1.83
    k = ", ".join(f"{v:g}" for v in cm.K_GRID)
    # Fila superior: las 7 etapas del modelo técnico
    y1 = 3.7
    xs = [0.15 + i * paso for i in range(7)]
    b1 = _caja(ax, xs[0], y1, w, h, "1. Fuentes", ["yfinance (precios)", "SEC EDGAR (utilidades)", "Damodaran (referencia)", "instantánea fechada"], C_DATOS)
    b2 = _caja(ax, xs[1], y1, w, h, "2. Limpieza", ["9 dimensiones de", "calidad; vacíos y ceros", "verificados", "(notebook 02)"], C_DATOS)
    b3 = _caja(ax, xs[2], y1, w, h, "3. Variables", ["σ20, σ252, σ20/σ252", "y |r|, solo hacia atrás", "descarta el calentamiento", "(no se imputa)"], C_PREP)
    b4 = _caja(ax, xs[3], y1, w, h, "4. Etiqueta", [f"N = {cm.N_DIAS} sesiones", f"rejilla de k: {k}", "censura: se aparta", "(mira al futuro)"], C_PREP)
    b5 = _caja(ax, xs[4], y1, w, h, "5. Partición", ["entrena 2010–2014", "valida 2015–2018", "prueba 2019+", f"brecha de {cm.BRECHA} sesiones"], C_PREP)
    b6 = _caja(ax, xs[5], y1, w, h, "6. Estandarización", ["z-score solo con el", "entrenamiento (pipeline", "del 07); submuestra", "de 1 de cada 5 filas"], C_PREP)
    b7 = _caja(ax, xs[6], y1, w, h, "7. Modelos", ["árbol de decisión", "SVM lineal", "SVM RBF", "+ referencias"], C_MODELO)
    for a_, b_ in zip((b1, b2, b3, b4, b5, b6), (b2, b3, b4, b5, b6, b7)):
        _flecha(ax, a_["der"], b_["izq"])
    ax.text(0.15, 0.12, "2009 se usa para calentar σ252 (252 sesiones); la brecha quita las últimas 60 sesiones antes de cada corte, "
            "así que el entrenamiento efectivo es 2010–2014. No aplican la codificación (no hay categóricas) ni la imputación (se descartan filas).", fontsize=8, color=C_BORDE, ha="left", va="bottom")

    # Fila inferior: dos ramas que confluyen en la API y el dashboard
    y2, hr = 1.0, 1.35
    rf = _caja(ax, 0.5, y2, 2.5, hr, "Rama fundamental", ["múltiplos (P/E, P/B) y", "percentiles frente a la", "historia y la industria"], C_RAMA)
    rs = _caja(ax, 3.4, y2, 2.5, hr, "Rama de simulación", ["bloques de 12 semanas", "de la acción; el XLP", "solo alinea las fechas"], C_RAMA)
    api = _caja(ax, 6.8, y2, 2.1, hr, "API", ["una lectura por cada", "uno de los 6 niveles"], C_PRODUCTO)
    dash = _caja(ax, 9.7, y2, 2.1, hr, "Dashboard", ["niveles, lecturas y", "decisiones guardadas"], C_PRODUCTO)
    # Los datos limpios y las variables alimentan las dos ramas (barra horizontal a y = yb)
    yb = 3.05
    _linea(ax, [b2["aba"], (b2["aba"][0], yb)])
    _linea(ax, [b3["aba"], (b3["aba"][0], yb)])
    _linea(ax, [(rf["arr"][0], yb), (b3["aba"][0], yb)])
    _flecha(ax, (rf["arr"][0], yb), rf["arr"])
    _flecha(ax, (rs["arr"][0], yb), rs["arr"])
    ax.text((b2["aba"][0] + b3["aba"][0]) / 2, yb + 0.08, "datos limpios y variables", fontsize=8, color=C_BORDE, ha="center", va="bottom")
    # Las ramas llegan a la API; los modelos también (técnica de entrada); la API alimenta el dashboard
    _flecha(ax, rs["der"], api["izq"])
    _linea(ax, [rf["aba"], (rf["aba"][0], 0.65), (api["aba"][0], 0.65)])
    _flecha(ax, (api["aba"][0], 0.65), api["aba"])
    _linea(ax, [b7["aba"], (b7["aba"][0], yb), (api["arr"][0], yb)])
    _flecha(ax, (api["arr"][0], yb), api["arr"])
    ax.text((b7["aba"][0] + api["arr"][0]) / 2, yb + 0.08, "técnica de entrada", fontsize=8, color=C_BORDE, ha="center", va="bottom")
    _flecha(ax, api["der"], dash["izq"])
    fig.tight_layout()
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=200, facecolor="white")
    plt.close(fig)


def main():
    cm.DIR_ASSETS_E2.mkdir(parents=True, exist_ok=True)
    diagrama_bloques(cm.DIR_ASSETS_E2 / "diagrama_bloques.png")
    print("diagrama_bloques.png guardado en", cm.DIR_ASSETS_E2)


if __name__ == "__main__":
    main()
