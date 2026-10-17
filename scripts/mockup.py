"""Mockup (wireframe) del dashboard del asistente bursátil.

Los niveles y las probabilidades son de EJEMPLO (ilustrativos; se marcan en la imagen).
Las cifras del panel de riesgo que dependen del sector salen de los datos reales
de nb04 §6.1 para el ticker de ejemplo (KO, industria piloto consumo defensivo):
R² del modelo mercado + sector y ΔR² que aporta el sector.
Salida: entregables/entrega_1/assets/mockup.png
Uso: uv run python scripts/mockup.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SALIDA = Path(__file__).resolve().parents[1] / "entregables/entrega_1/assets/mockup.png"

# Cifras de ejemplo del encabezado: precio = P/E x EPS y precio = P/B x valor en libros por acción.
# EPS = utilidad por acción de los últimos 12 meses (TTM: suma de los 4 trimestres más recientes).
# Son valores ilustrativos; la imagen lo marca.
TICKER, PRECIO, EPS, VLA = "KO", 70.00, 2.80, 7.00
REPORTE = "10-Q del 2.º trimestre (ejemplo: 2026-07-28)"
AZUL, NARANJA, ROJO, GRIS = "#1b6ca8", "#c2571a", "#b00020", "#555555"
COLORES = {"Entrada": AZUL, "Salida": NARANJA}

# Horizonte de la etiqueta de entrada (nb04 §4.3; punto 4 §4.5).
N_DIAS = 60
HORIZONTE_SALIDAS = "3 años"

# nivel, tipo, precio, percentil en su historia, percentil en la industria,
# lectura P2 "¿suele ser temporal?" (solo entradas baratas), lectura técnica (solo entradas),
# lectura probabilística (solo salidas). N = 60 días hábiles; horizonte de salidas = 3 años.
P2_OPORTUNIDAD = ("¿Suele ser temporal? Cuando estuvo así de\nbarata, su P/E subió +18 % en 3 años:\n"
                  "precio +15 %, utilidades −3 %\n→ por precio (posible oportunidad)")
P2_TRAMPA = ("¿Suele ser temporal? Cuando estuvo así de\nbarata, su P/E subió +12 % en 3 años:\n"
             "precio −4 %, utilidades −16 %\n→ por caída de utilidades (posible trampa de valor)")
P2_NO_APLICA = "No está barata frente a su historia:\nla lectura \"¿suele ser temporal?\" no aplica"
NIVELES = [
    ("Deep value", "Entrada", 56.0, 6, 35, P2_OPORTUNIDAD,
     f"P(tocar en {N_DIAS} días hábiles) = 21 %\nlínea base por volatilidad diaria: 16 %\nrango de incertidumbre: 15–27 %", "—"),
    ("Value", "Entrada", 61.6, 18, 52, P2_TRAMPA,
     f"P(tocar en {N_DIAS} días hábiles) = 42 %\nlínea base por volatilidad diaria: 35 %\nrango de incertidumbre: 36–48 %", "—"),
    ("Valoración histórica", "Entrada", 67.2, 48, 68, P2_NO_APLICA,
     f"P(tocar en {N_DIAS} días hábiles) = 71 %\nlínea base por volatilidad diaria: 66 %\nrango de incertidumbre: 64–78 %", "—"),
    ("Salida negativo", "Salida", 75.6, 71, 80, "", "—",
     "P(alcanzar en el horizonte) = 81 %\nsimulación con retornos históricos\nrango de incertidumbre: 75–87 %"),
    ("Salida base", "Salida", 81.2, 85, 88, "", "—",
     "P(alcanzar en el horizonte) = 62 %\nsimulación con retornos históricos\nrango de incertidumbre: 55–69 %"),
    ("Salida positivo", "Salida", 89.6, 96, 94, "", "—",
     "P(alcanzar en el horizonte) = 37 %\nsimulación con retornos históricos\nrango de incertidumbre: 30–44 %"),
]

# Panel de riesgo: las primeras cuatro cifras son ilustrativas; las dos del sector salen
# de nb04 §6.1 para KO (R² del modelo r ~ r_SPY + r_XLP y ΔR² que aporta el XLP sobre
# el modelo r ~ r_SPY). Semanal, 927 semanas 2009–2026.
RIESGO = [
    ("Volatilidad del último año", "16 % (valor ilustrativo)", "cuánto se mueve el precio en un año típico"),
    ("Peor semana típica (percentil 5)", "−3,4 % (valor ilustrativo)", "1 de cada 20 semanas cae al menos esto"),
    ("Frecuencia de caídas fuertes", "2,1 vs 1,0 (valor ilustrativo)", "caídas semanales grandes por año: real vs lo esperado"),
    ("Caída máxima (desde un pico)", "−37 % (valor ilustrativo)", "2020; tardó 14 meses en recuperarse"),
    ("Cuánto se mueve con el sector (XLP)", "R² 0,61 · ΔR² 0,29", "KO (nb04 §6.1): el modelo mercado + sector explica 61 %;\nañadir el sector al mercado agrega 0,29 en R²"),
]

# Recuadro de desempeño histórico del modelo técnico. Las métricas se calculan
# en la entrega 2 (se entrena el SVM allá; punto 4 §4.4): se dejan como marcadores.
DESEMPENO = [
    ("AUC vs línea base", "se calcula en la entrega 2"),
    ("Brier (calibración)", "se calcula en la entrega 2"),
    ("Diagrama de calibración", "se calcula en la entrega 2"),
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
    ax.text(0.0, 0.02, "MOCKUP: los niveles y las probabilidades son de EJEMPLO (ilustrativos). "
            "El panel de riesgo del sector trae cifras reales de KO (nb04 §6.1).",
            fontsize=9.5, color=GRIS, va="center", style="italic")
    ax.text(1.0, 0.02, "Industria: consumo defensivo (industria piloto del EDA)", fontsize=10, ha="right", va="center",
            color="white", weight="bold", bbox=dict(boxstyle="round,pad=0.4", fc="#2e7d32", ec="none"))


def tabla_niveles(ax):
    ax.axis("off")
    cols = ["Nivel del usuario\n(editable)", "Precio", "Múltiplo\nP/E (TTM) · P/B",
            "Fundamental: percentil del P/E en su historia ·\nen la industria (p6 = más barato que el 94 %)\n"
            "y, en entradas baratas, ¿suele ser temporal?",
            "Técnica (SVM, solo entradas)\n¿compro ya o espero?",
            f"Probabilística (solo salidas)\n¿qué tan probable es llegar?\n[ Horizonte: {HORIZONTE_SALIDAS} (editable) ▾ ]"]
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
    ax.set_title("Panel de riesgo (descriptivo, datos pasados)", fontsize=10, loc="left", pad=6)
    for k, (nombre, valor, ayuda) in enumerate(RIESGO):
        y = 0.92 - k * 0.19
        ax.text(0.0, y, nombre, fontsize=9.5, va="center", weight="bold")
        ax.text(1.0, y, valor, fontsize=10, va="center", ha="right", weight="bold", color=AZUL)
        ax.text(0.0, y - 0.08, ayuda, fontsize=8.3, va="center", color=GRIS)
        ax.plot([0, 1], [y - 0.14, y - 0.14], color="#ddd", lw=0.6, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def desempeno_historico(ax):
    """Recuadro de desempeño histórico del SVM. En la entrega 1 los valores no
    se calculan; se marcan como 'se calcula en la entrega 2' (punto 4 §4.4)."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=GRIS, lw=1))
    ax.text(0.02, 0.88, "Desempeño histórico del modelo técnico (SVM)",
            fontsize=10, weight="bold", va="center")
    ax.text(0.02, 0.72, "Para que el score se lea con contexto, incluidos los errores (RN1).",
            fontsize=8.5, va="center", color=GRIS, style="italic")
    for k, (nombre, valor) in enumerate(DESEMPENO):
        y = 0.56 - k * 0.17
        ax.text(0.02, y, nombre, fontsize=9.3, va="center", weight="bold")
        ax.text(0.98, y, valor, fontsize=9, va="center", ha="right", color=GRIS, style="italic")


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
    fig = plt.figure(figsize=(16, 15.5), facecolor="white")
    gs = fig.add_gridspec(5, 2, height_ratios=[0.7, 3.6, 2.4, 1.1, 1.1],
                          width_ratios=[1.35, 1],
                          hspace=0.32, wspace=0.12, left=0.05, right=0.97, top=0.97, bottom=0.06)
    encabezado(fig.add_subplot(gs[0, :]))
    tabla_niveles(fig.add_subplot(gs[1, :]))
    grafico_precio(fig.add_subplot(gs[2, 0]))
    panel_riesgo(fig.add_subplot(gs[2, 1]))
    desempeno_historico(fig.add_subplot(gs[3, :]))
    registro_decision(fig.add_subplot(gs[4, :]))
    fig.text(0.05, 0.030, "Validado en consumo defensivo (21 empresas, benchmarks SPY y XLP). "
             "En otras industrias el modelo no está validado y la pantalla lo avisa.",
             fontsize=10, color="#2e7d32", weight="bold", va="center")
    fig.text(0.05, 0.010, "Línea base por volatilidad: frecuencia histórica con la que el precio tocó niveles a la misma "
             "distancia en días de volatilidad parecida (volatilidad diaria del último año). Si el modelo no la supera, "
             "no aporta.",
             fontsize=8.5, color=GRIS, va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=120)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
