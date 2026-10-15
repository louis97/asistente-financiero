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
# EPS = utilidad por acción de los últimos 12 meses (TTM: suma de los 4 trimestres más recientes)
TICKER, PRECIO, EPS, VLA = "KO", 70.00, 2.80, 7.00
REPORTE = "10-Q del 2.º trimestre (ejemplo: 2026-07-28)"
AZUL, NARANJA, ROJO, GRIS = "#1b6ca8", "#c2571a", "#b00020", "#555555"
COLORES = {"Entrada": AZUL, "Salida": NARANJA}

# nivel, tipo, precio, percentil en su historia, percentil en la industria,
# lectura P2 "¿suele ser temporal?" (solo entradas baratas), lectura técnica (solo entradas),
# lectura probabilística (solo salidas). N = 40 días hábiles; horizonte de salidas = 3 años.
P2_OPORTUNIDAD = ("¿Suele ser temporal? Cuando estuvo así de\nbarata, su P/E subió +18 % en 3 años:\n"
                  "precio +15 %, utilidades −3 %\n→ por precio (posible oportunidad)")
P2_TRAMPA = ("¿Suele ser temporal? Cuando estuvo así de\nbarata, su P/E subió +12 % en 3 años:\n"
             "precio −4 %, utilidades −16 %\n→ por caída de utilidades (posible trampa de valor)")
P2_NO_APLICA = "No está barata frente a su historia:\nla lectura \"¿suele ser temporal?\" no aplica"
NIVELES = [
    ("Deep value", "Entrada", 56.0, 6, 35, P2_OPORTUNIDAD,
     "P(tocar en 40 días hábiles) = 21 %\nlínea base por volatilidad diaria: 16 %\nrango de incertidumbre: 15–27 %", "—"),
    ("Value", "Entrada", 61.6, 18, 52, P2_TRAMPA,
     "P(tocar en 40 días hábiles) = 42 %\nlínea base por volatilidad diaria: 35 %\nrango de incertidumbre: 36–48 %", "—"),
    ("Valoración histórica", "Entrada", 67.2, 48, 68, P2_NO_APLICA,
     "P(tocar en 40 días hábiles) = 71 %\nlínea base por volatilidad diaria: 66 %\nrango de incertidumbre: 64–78 %", "—"),
    ("Salida negativo", "Salida", 75.6, 71, 80, "", "—",
     "P(alcanzar en el horizonte) = 81 %\nsimulación con retornos históricos\nrango de incertidumbre: 75–87 %"),
    ("Salida base", "Salida", 81.2, 85, 88, "", "—",
     "P(alcanzar en el horizonte) = 62 %\nsimulación con retornos históricos\nrango de incertidumbre: 55–69 %"),
    ("Salida positivo", "Salida", 89.6, 96, 94, "", "—",
     "P(alcanzar en el horizonte) = 37 %\nsimulación con retornos históricos\nrango de incertidumbre: 30–44 %"),
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
    ax.text(0.0, 0.92, f"{TICKER}  |  Precio: ${PRECIO:.2f}  |  P/E (TTM, últimos 12 meses): {PRECIO / EPS:.1f}x  |  "
            f"P/B: {PRECIO / VLA:.1f}x", fontsize=14.5, weight="bold", va="center")
    ax.text(0.0, 0.64, f"Último reporte: {REPORTE}.  El P/E y los niveles por múltiplo se actualizan solos con cada "
            "reporte trimestral (10-Q) y anual (10-K).", fontsize=10.5, va="center")
    ax.text(0.0, 0.33, "Herramienta de apoyo, no es asesoría de inversión. "
            "Muestra probabilidades con su incertidumbre; nunca dice \"compra\" ni \"vende\".",
            fontsize=10.5, color=ROJO, weight="bold", va="center")
    ax.text(0.0, 0.02, "MOCKUP: todas las cifras son de EJEMPLO (inventadas para la validación del diseño).",
            fontsize=9.5, color=GRIS, va="center", style="italic")
    ax.text(1.0, 0.02, "Industria: consumo defensivo (piloto validado)", fontsize=10, ha="right", va="center",
            color="white", weight="bold", bbox=dict(boxstyle="round,pad=0.4", fc="#2e7d32", ec="none"))


def tabla_niveles(ax):
    ax.axis("off")
    cols = ["Nivel del usuario\n(editable)", "Precio", "Múltiplo\nP/E (TTM) · P/B",
            "Fundamental: percentil del P/E en su historia ·\nen la industria (p6 = más barato que el 94 %)\n"
            "y, en entradas baratas, ¿suele ser temporal?",
            "Técnica (SVM, solo entradas)\n¿compro ya o espero?",
            "Probabilística (solo salidas)\n¿qué tan probable es llegar?\n[ Horizonte: 3 años (editable) ▾ ]"]
    filas = []
    for n, t, p, h, i, p2, tec, prob in NIVELES:
        fund = f"p{h} en su historia · p{i} en la industria" + (f"\n{p2}" if p2 else "")
        filas.append([f"{n}\n({t.lower()})", f"${p:.2f}", f"{p / EPS:.1f}x · {p / VLA:.1f}x",
                      fund, tec, prob])
    tab = ax.table(cellText=filas, colLabels=cols, loc="center", cellLoc="center",
                   colWidths=[0.12, 0.06, 0.10, 0.27, 0.22, 0.23])
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.8)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#9e9e9e")
        cell.set_height(0.15 if r == 0 else (0.175 if r <= 3 else 0.1))
        if r == 0:
            cell.set_facecolor("#eceff1")
            cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#e8f1f8" if NIVELES[r - 1][1] == "Entrada" else "#fbeee4")
            if c == 0:
                cell.set_text_props(weight="bold", color=COLORES[NIVELES[r - 1][1]])
    ax.set_title("Seis niveles del usuario (3 de entrada, 3 de salida) en precio y en múltiplo, con tres lecturas "
                 "por nivel. Los niveles por múltiplo se recalculan con cada reporte (precio = múltiplo × EPS TTM).",
                 fontsize=10, loc="left", pad=12)


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
    campos = [("Fecha", "2026-10-16"), ("Nivel", "Value ($61.60 · 22.0x P/E TTM)"),
              ("Lectura que más pesó", "Fundamental: p18 en su historia, pero el rebote pasado vino de caída de utilidades"),
              ("Decisión", "Esperar; orden límite en $61.60"),
              ("Nota", "\"Está barata, pero puede ser trampa de valor; quiero ver si el próximo 10-Q confirma las utilidades.\"")]
    for k, (a, b) in enumerate(campos):
        y = 0.68 - k * 0.15
        ax.text(0.015, y, a + ":", fontsize=9, va="center", color=GRIS)
        ax.text(0.20, y, b, fontsize=9, va="center")
    for k, txt in enumerate(["Editar niveles", "Guardar decisión"]):
        ax.text(0.70 + k * 0.155, 0.86, txt, fontsize=9, va="center", transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.4", fc="#eceff1", ec="#607d8b"))


def main():
    fig = plt.figure(figsize=(16, 14.5), facecolor="white")
    gs = fig.add_gridspec(4, 2, height_ratios=[0.7, 3.6, 2.4, 1.2], width_ratios=[1.35, 1],
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
             "distancia en días de volatilidad parecida (volatilidad diaria del último año). Si el modelo no la supera, "
             "no aporta.",
             fontsize=8.5, color=GRIS, va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=120)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
