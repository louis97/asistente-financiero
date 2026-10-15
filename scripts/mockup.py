"""Mockup (wireframe) del dashboard del asistente bursátil.

Todas las cifras son de EJEMPLO (ilustrativas, no provienen de datos reales).
Ticker de ejemplo: KO, de la industria piloto (consumo defensivo).
Salida: entregables/entrega_1/assets/mockup.png
Uso: uv run python scripts/mockup.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SALIDA = Path(__file__).resolve().parents[1] / "entregables/entrega_1/assets/mockup.png"

# Cifras de ejemplo: precio = P/E x EPS y precio = P/B x valor en libros por acción
TICKER, PRECIO, EPS, VLA, FILED = "KO", 70.00, 2.80, 7.00, "2026-02-20"
AZUL, NARANJA, ROJO, GRIS = "#1b6ca8", "#c2571a", "#b00020", "#555555"
COLORES = {"Entrada": AZUL, "Salida": NARANJA}

# nivel, tipo, precio, percentil en su historia, percentil en la industria,
# lectura técnica (solo entradas), lectura probabilística (solo salidas)
NIVELES = [
    ("Deep value", "Entrada", 56.0, 6, 35,
     "P(tocar en 20 días) = 12 %\nlínea base por volatilidad: 9 %\nrango de incertidumbre: 8–16 %", "—"),
    ("Value", "Entrada", 61.6, 22, 52,
     "P(tocar en 20 días) = 35 %\nlínea base por volatilidad: 28 %\nrango de incertidumbre: 29–41 %", "—"),
    ("Valoración histórica", "Entrada", 67.2, 48, 68,
     "P(tocar en 20 días) = 63 %\nlínea base por volatilidad: 57 %\nrango de incertidumbre: 56–70 %", "—"),
    ("Salida negativo", "Salida", 75.6, 71, 80, "—",
     "P(alcanzar en 12 meses) = 58 %\nsimulación con retornos históricos\nrango de incertidumbre: 52–64 %"),
    ("Salida base", "Salida", 81.2, 85, 88, "—",
     "P(alcanzar en 12 meses) = 34 %\nsimulación con retornos históricos\nrango de incertidumbre: 28–40 %"),
    ("Salida positivo", "Salida", 89.6, 96, 94, "—",
     "P(alcanzar en 12 meses) = 13 %\nsimulación con retornos históricos\nrango de incertidumbre: 9–17 %"),
]

RIESGO = [
    ("Volatilidad del último año", "16 %", "cuánto se mueve el precio en un año típico"),
    ("Peor semana típica (percentil 5)", "−3,4 %", "1 de cada 20 semanas cae al menos esto"),
    ("Frecuencia de caídas fuertes", "2,1 vs 1,0", "caídas semanales grandes por año: real vs lo esperado"),
    ("Caída máxima (desde un pico)", "−37 %", "2020; tardó 14 meses en recuperarse"),
    ("Cuánto se mueve con el sector (XLP)", "R² 0,55", "el XLP explica 0,25 más que el SPY solo"),
]


def precio_ejemplo(n=156, semilla=11):
    """Serie semanal inventada que termina en el precio actual."""
    rng = np.random.default_rng(semilla)
    r = rng.normal(0.0012, 0.022, n)
    return PRECIO * np.exp(np.cumsum(r) - r.sum())


def encabezado(ax):
    ax.axis("off")
    ax.text(0.0, 0.80, f"{TICKER}  |  Precio: ${PRECIO:.2f}  |  P/E: {PRECIO / EPS:.1f}x  |  "
            f"P/B: {PRECIO / VLA:.1f}x  |  Último reporte (10-K): {FILED}", fontsize=14.5, weight="bold", va="center")
    ax.text(0.0, 0.38, "Herramienta de apoyo, no es asesoría de inversión. "
            "Muestra probabilidades con su incertidumbre; nunca dice \"compra\" ni \"vende\".",
            fontsize=10.5, color=ROJO, weight="bold", va="center")
    ax.text(0.0, 0.02, "MOCKUP: todas las cifras son de EJEMPLO (inventadas para la validación del diseño).",
            fontsize=9.5, color=GRIS, va="center", style="italic")
    ax.text(1.0, 0.02, "Industria: consumo defensivo (piloto validado)", fontsize=10, ha="right", va="center",
            color="white", weight="bold", bbox=dict(boxstyle="round,pad=0.4", fc="#2e7d32", ec="none"))


def tabla_niveles(ax):
    ax.axis("off")
    cols = ["Nivel del usuario\n(editable)", "Precio", "Múltiplo\nP/E · P/B",
            "Fundamental: percentil del P/E\nen su historia · en la industria\n(p6 = más barato que el 94 %)",
            "Técnica (SVM, solo entradas)\n¿compro ya o espero?",
            "Probabilística (solo salidas)\n¿qué tan probable es llegar?"]
    filas = []
    for n, t, p, h, i, tec, prob in NIVELES:
        filas.append([f"{n}\n({t.lower()})", f"${p:.2f}", f"{p / EPS:.1f}x · {p / VLA:.1f}x",
                      f"p{h} · p{i}", tec, prob])
    tab = ax.table(cellText=filas, colLabels=cols, loc="center", cellLoc="center",
                   colWidths=[0.15, 0.07, 0.11, 0.16, 0.27, 0.24])
    tab.auto_set_font_size(False)
    tab.set_fontsize(9)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#9e9e9e")
        cell.set_height(0.19 if r == 0 else 0.135)
        if r == 0:
            cell.set_facecolor("#eceff1")
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#e8f1f8" if NIVELES[r - 1][1] == "Entrada" else "#fbeee4")
            if c == 0:
                cell.set_text_props(weight="bold", color=COLORES[NIVELES[r - 1][1]])
    ax.set_title("Seis niveles del usuario (3 de entrada, 3 de salida) en precio y en múltiplo, con tres lecturas "
                 "por nivel. Los niveles por múltiplo se recalculan solos con cada reporte (precio = múltiplo × EPS).",
                 fontsize=10, loc="left", pad=4)


def grafico_precio(ax):
    p = precio_ejemplo()
    x = np.arange(len(p))
    ax.plot(x, p, color="#222", lw=1.3)
    for n, t, pr, *_ in NIVELES:
        ax.axhline(pr, color=COLORES[t], ls="--", lw=1)
        ax.text(len(p) + 1, pr, f"{n} ${pr:.0f}", fontsize=8, va="center", color=COLORES[t],
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax.set_xlim(0, len(p) + 40)
    ax.set_xlabel("Semanas (últimos 3 años, ejemplo)")
    ax.set_ylabel("Precio ($)")
    ax.set_title("Precio semanal y los 6 niveles (azul: entrada, naranja: salida)", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)


def panel_riesgo(ax):
    ax.axis("off")
    ax.set_title("Panel de riesgo (descriptivo, datos pasados; ejemplo)", fontsize=10, loc="left", pad=6)
    for k, (nombre, valor, ayuda) in enumerate(RIESGO):
        y = 0.92 - k * 0.19
        ax.text(0.0, y, nombre, fontsize=9.5, va="center", weight="bold")
        ax.text(1.0, y, valor, fontsize=10, va="center", ha="right", weight="bold", color=AZUL)
        ax.text(0.0, y - 0.075, ayuda, fontsize=8.5, va="center", color=GRIS)
        ax.plot([0, 1], [y - 0.13, y - 0.13], color="#ddd", lw=0.6, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def registro_decision(ax):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=GRIS, lw=1))
    ax.text(0.015, 0.86, "Registro de decisión (lo escribe el usuario)", fontsize=10, weight="bold", va="center")
    campos = [("Fecha", "2026-10-16"), ("Nivel", "Value ($61.60 · 22.0x P/E)"),
              ("Lectura que más pesó", "Fundamental: p22 en su historia"),
              ("Decisión", "Esperar; orden límite en $61.60"),
              ("Nota", "\"El P/E está por debajo de su historia, pero quiero ver el próximo 10-Q.\"")]
    for k, (a, b) in enumerate(campos):
        y = 0.68 - k * 0.15
        ax.text(0.015, y, a + ":", fontsize=9, va="center", color=GRIS)
        ax.text(0.20, y, b, fontsize=9, va="center")
    for k, txt in enumerate(["Editar niveles", "Guardar decisión"]):
        ax.text(0.70 + k * 0.155, 0.86, txt, fontsize=9, va="center", transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.4", fc="#eceff1", ec="#607d8b"))


def main():
    fig = plt.figure(figsize=(16, 13.5), facecolor="white")
    gs = fig.add_gridspec(4, 2, height_ratios=[0.55, 3.0, 2.6, 1.25], width_ratios=[1.35, 1],
                          hspace=0.32, wspace=0.12, left=0.05, right=0.97, top=0.97, bottom=0.07)
    encabezado(fig.add_subplot(gs[0, :]))
    tabla_niveles(fig.add_subplot(gs[1, :]))
    grafico_precio(fig.add_subplot(gs[2, 0]))
    panel_riesgo(fig.add_subplot(gs[2, 1]))
    registro_decision(fig.add_subplot(gs[3, :]))
    fig.text(0.05, 0.035, "Validado en consumo defensivo (21 empresas, benchmarks SPY y XLP). "
             "En otras industrias el modelo no está validado y la pantalla lo avisa.",
             fontsize=10, color="#2e7d32", weight="bold", va="center")
    fig.text(0.05, 0.012, "Línea base por volatilidad: frecuencia histórica con la que el precio tocó niveles a la misma "
             "distancia en semanas de volatilidad parecida. Si el modelo no la supera, no aporta.",
             fontsize=8.5, color=GRIS, va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=120)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
