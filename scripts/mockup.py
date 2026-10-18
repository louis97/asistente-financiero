"""Mockup (wireframe) del dashboard del asistente bursátil — versión 2.

Los niveles y las probabilidades son de EJEMPLO (ilustrativos; se marcan en la imagen).
Las cifras del panel de riesgo que dependen del sector salen de los datos reales
de nb04 §6.3 para el ticker de ejemplo (KO, industria piloto consumo defensivo):
R² del modelo mercado + sector y ΔR² que aporta el sector.

Cambios de la v2 respecto a la v1 (feedback 2026-10-18):
  - franja "Cómo leer esta pantalla" con definiciones de una línea;
  - P/E y P/B en columnas separadas y columna "% vs. precio actual" en cada nivel;
  - encabezados en lenguaje llano, con la columna de la lectura técnica marcada
    "se entrena en la entrega 2";
  - interpretación de la fundamental movida a "Notas" bajo la tabla;
  - marca descriptiva del precio actual, sin veredicto;
  - panel de riesgo con 5 filas más espaciadas y una línea de explicación.

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
VERDE = "#2e7d32"
COLORES = {"Entrada": AZUL, "Salida": NARANJA}

# Horizonte de la etiqueta de entrada (nb04 §4.3; punto 4 §4.5).
N_DIAS = 60
HORIZONTE_SALIDAS = "3 años"

# nivel, tipo, precio, percentil historia, percentil industria, nota P2 (índice en NOTAS, None si no aplica),
# lectura técnica (solo entradas), lectura probabilística (solo salidas).
# N = 60 días hábiles; horizonte de salidas = 3 años.
NIVELES = [
    ("Deep value", "Entrada", 56.0, 6, 35, 1,
     f"21 % (modelo SVM, se entrena en la entrega 2)\n"
     f"línea base por volatilidad diaria: 16 %\nrango de incertidumbre: 15–27 %",
     "—"),
    ("Value", "Entrada", 61.6, 18, 52, 2,
     f"42 % (modelo SVM, se entrena en la entrega 2)\n"
     f"línea base por volatilidad diaria: 35 %\nrango de incertidumbre: 36–48 %",
     "—"),
    ("Valoración histórica", "Entrada", 67.2, 48, 68, 3,
     f"71 % (modelo SVM, se entrena en la entrega 2)\n"
     f"línea base por volatilidad diaria: 66 %\nrango de incertidumbre: 64–78 %",
     "—"),
    ("Salida negativo", "Salida", 75.6, 71, 80, None, "—",
     "81 % (simulación con historia)\nrango de incertidumbre: 75–87 %"),
    ("Salida base", "Salida", 81.2, 85, 88, None, "—",
     "62 % (simulación con historia)\nrango de incertidumbre: 55–69 %"),
    ("Salida positivo", "Salida", 89.6, 96, 94, None, "—",
     "37 % (simulación con historia)\nrango de incertidumbre: 30–44 %"),
]

# Notas bajo la tabla: una por entrada barata; se enumeran y se referencian por índice en la fila.
NOTAS = {
    1: "Nota 1 (Deep value). ¿Suele ser temporal? Cuando estuvo así de barata,\n"
       "su P/E subió +18 % en los 3 años siguientes: precio +15 %, utilidades\n"
       "promedio −3 %. Lectura: el rebote pasado vino del precio (posible\n"
       "oportunidad).",
    2: "Nota 2 (Value). ¿Suele ser temporal? Cuando estuvo así de barata, su\n"
       "P/E subió +12 % en los 3 años siguientes: precio −4 %, utilidades\n"
       "promedio −16 %. Lectura: el rebote pasado vino de la caída de las\n"
       "utilidades (posible trampa de valor).",
    3: "Nota 3 (Valoración histórica). No está barata frente a su historia:\n"
       "la lectura «¿suele ser temporal?» no aplica.",
}

# Franja "Cómo leer esta pantalla": 8 definiciones de una línea (incluye SVM), coherentes con el glosario.
GLOSARIO_FRANJA = [
    ("P/E", "precio ÷ utilidad por acción (TTM = últimos 12 meses). Dice cuántos dólares se pagan "
            "por cada dólar de utilidad."),
    ("P/B", "precio ÷ patrimonio por acción. Dice cuántos dólares se pagan por cada dólar de "
            "patrimonio contable."),
    ("percentil", "«entre los valores pasados, ¿en qué puesto queda el de hoy?». p6 = más barata "
                  "que el 94 % de su historia."),
    ("industria piloto", "consumo defensivo (alimentos, bebidas, aseo personal y del hogar, y tabaco): "
                         "bienes que se compran en cualquier fase del ciclo económico."),
    ("SVM", "siglas de support vector machine; un modelo que aprende a separar casos positivos de "
            "negativos y entrega una probabilidad."),
    ("lectura técnica", "probabilidad de que el precio toque el nivel en 60 días hábiles, con el "
                        "modelo SVM. Solo en entradas."),
    ("lectura probabilística", "probabilidad de que el precio alcance la salida en el horizonte, "
                               "por simulación con la historia. Solo en salidas."),
    ("línea base", "frecuencia histórica con la que el precio tocó niveles a la misma distancia en "
                   "días de volatilidad parecida. Si el modelo no la supera, no aporta."),
]

# Panel de riesgo: las primeras cuatro cifras son ilustrativas; la quinta sale de nb04 §6.3 para KO
# (R² del modelo r ~ r_SPY + r_XLP y ΔR² que aporta el XLP sobre el modelo r ~ r_SPY). Semanal,
# 927 semanas 2009–2026.
RIESGO = [
    ("Cuánto se mueve en un año típico (volatilidad)", "16 %",
     "subida o bajada típica anual (valor ilustrativo)."),
    ("Peor semana típica (1 de cada 20 cae al menos esto)", "−3,4 %",
     "percentil 5 del retorno semanal (valor ilustrativo)."),
    ("Caídas semanales fuertes al año", "2,1 vs 1,0",
     "veces observadas frente a lo esperado si el mercado fuera normal (valor ilustrativo)."),
    ("Peor caída desde un pico (y cuánto tardó en recuperarse)", "−37 % · 14 meses",
     "mayor caída acumulada observada; año de referencia 2020 (valor ilustrativo)."),
    ("Cuánto se mueve con el sector (XLP)", "R² 0,61 · ΔR² 0,29",
     "KO: el modelo mercado + sector explica 61 % del movimiento; añadir el sector al mercado "
     "aporta 0,29 más de R² (cifras reales, nb04 §6.3)."),
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
    ax.text(0.0, 0.88, f"{TICKER}  |  Precio: ${PRECIO:.2f}  |  P/E (TTM, últimos 12 meses): "
            f"{PRECIO / EPS:.1f}x  |  P/B: {PRECIO / VLA:.1f}x",
            fontsize=14.5, weight="bold", va="center")
    ax.text(0.0, 0.58, f"Último reporte: {REPORTE}.  El P/E y los niveles por múltiplo se actualizan "
            "solos con cada reporte trimestral (10-Q) y anual (10-K).", fontsize=10.5, va="center")
    ax.text(0.0, 0.28, "Herramienta de apoyo, no es asesoría de inversión. "
            "Muestra probabilidades con su incertidumbre; nunca dice «compra» ni «vende».",
            fontsize=10.5, color=ROJO, weight="bold", va="center")
    ax.text(0.0, 0.00, "MOCKUP (v2): los niveles y las probabilidades son de EJEMPLO (ilustrativos); "
            "la cifra «R² · ΔR²» del panel de riesgo es real para KO (nb04 §6.3).",
            fontsize=9.5, color=GRIS, va="center", style="italic")
    ax.text(1.0, 0.88, "Industria: consumo defensivo (industria piloto del EDA)",
            fontsize=10, ha="right", va="center", color="white", weight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc=VERDE, ec="none"))


def franja_glosario(ax):
    """Franja 'Cómo leer esta pantalla' con 8 definiciones de una línea, incluida SVM (hallazgo H1)."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=True,
                               fc="#f5f8fb", ec="#9fb8d0", lw=0.8))
    ax.text(0.015, 0.92, "Cómo leer esta pantalla (glosario de bolsillo)",
            fontsize=10.5, weight="bold", va="center", color=AZUL)
    # 8 entradas en una sola columna, cada una en una línea, con etiqueta en negrita.
    n = len(GLOSARIO_FRANJA)
    y0, y1 = 0.80, 0.05
    for k, (termino, def_) in enumerate(GLOSARIO_FRANJA):
        y = y0 - k * (y0 - y1) / max(n - 1, 1)
        ax.text(0.015, y, f"{termino}:", fontsize=9.3, weight="bold", va="center")
        ax.text(0.145, y, def_, fontsize=9.3, va="center", color="#222")


def tabla_niveles(ax):
    ax.axis("off")
    cols = ["Nivel del usuario\n(editable)",
            "Precio",
            "% vs. precio\nactual",
            "P/E (TTM)",
            "P/B",
            "Fundamental:\npercentil P/E\n(historia · industria)",
            f"Prob. de tocar en {N_DIAS} días\n(modelo SVM, se entrena\nen la entrega 2)\nSolo entradas",
            f"Prob. de alcanzar la salida\n(simulación con historia)\nHorizonte: {HORIZONTE_SALIDAS} (editable)\nSolo salidas"]
    filas = []
    for n, t, p, h, i, nota_idx, tec, prob in NIVELES:
        pct = (p / PRECIO - 1) * 100
        pct_txt = f"{pct:+.0f} %".replace("-", "−")
        fund = f"p{h} historia · p{i} industria"
        if nota_idx is not None:
            fund += f"\n→ ver Nota {nota_idx}"
        filas.append([f"{n}\n({t.lower()})",
                      f"${p:.2f}", pct_txt,
                      f"{p / EPS:.1f}x", f"{p / VLA:.1f}x",
                      fund, tec, prob])
    tab = ax.table(cellText=filas, colLabels=cols, loc="center", cellLoc="center",
                   colWidths=[0.12, 0.06, 0.07, 0.06, 0.05, 0.14, 0.26, 0.24])
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.8)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#9e9e9e")
        if r == 0:
            cell.set_height(0.19)
            cell.set_facecolor("#eceff1")
            cell.set_text_props(weight="bold")
        else:
            cell.set_height(0.14)
            cell.set_facecolor("#e8f1f8" if NIVELES[r - 1][1] == "Entrada" else "#fbeee4")
            if c == 0:
                cell.set_text_props(weight="bold", color=COLORES[NIVELES[r - 1][1]])
    ax.set_title("Seis niveles del usuario (3 de entrada, 3 de salida), en precio y en múltiplo, "
                 "con sus tres lecturas. Los valores son ilustrativos (la cifra «SVM» proviene de un "
                 "modelo que se entrena en la entrega 2).",
                 fontsize=10, loc="left", pad=10)


def notas_tabla(ax):
    """Recuadro con las notas 1–3 (lectura «¿suele ser temporal?» de la fundamental; hallazgo H2)."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=True,
                               fc="#fdf7ee", ec="#d6b78a", lw=0.8, clip_on=False))
    ax.text(0.015, 0.95, "Notas de la columna Fundamental (lectura comparativa, solo entradas baratas)",
            fontsize=10, weight="bold", va="top", color="#8a5a1a")
    y_inicial = 0.80
    paso_por_nota = 0.30
    for k in sorted(NOTAS):
        y = y_inicial - (k - 1) * paso_por_nota
        ax.text(0.015, y, NOTAS[k], fontsize=8.6, va="top", clip_on=False)


def grafico_precio(ax):
    p = precio_ejemplo()
    x = np.arange(len(p))
    ax.plot(x, p, color="#222", lw=1.3)
    # Marca del precio actual: punto + anotación descriptiva, sin veredicto (hallazgo H4).
    ax.axhline(PRECIO, color="#444", ls=":", lw=1)
    ax.scatter([len(p) - 1], [PRECIO], color="#000", zorder=5, s=28)
    # Niveles vecinos para la anotación.
    bajos = [(n, pr) for n, t, pr, *_ in NIVELES if pr < PRECIO]
    altos = [(n, pr) for n, t, pr, *_ in NIVELES if pr > PRECIO]
    cercano_bajo = max(bajos, key=lambda nv: nv[1]) if bajos else None
    cercano_alto = min(altos, key=lambda nv: nv[1]) if altos else None
    partes = []
    if cercano_bajo is not None:
        partes.append(f"{cercano_bajo[0]} ${cercano_bajo[1]:.2f}")
    partes.append(f"precio actual ${PRECIO:.2f}")
    if cercano_alto is not None:
        partes.append(f"{cercano_alto[0]} ${cercano_alto[1]:.2f}")
    frase = " · ".join(partes)
    ax.text(0.02, 0.02, f"Posición: {frase} (descriptivo, sin veredicto).",
            transform=ax.transAxes, fontsize=8.8, color=GRIS, style="italic")
    for n, t, pr, *_ in NIVELES:
        ax.axhline(pr, color=COLORES[t], ls="--", lw=1)
        ax.text(len(p) + 1, pr, f"{n} ${pr:.0f}", fontsize=8, va="center", color=COLORES[t],
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax.set_xlim(0, len(p) + 42)
    ax.set_xlabel("Semanas (últimos 3 años, ejemplo)")
    ax.set_ylabel("Precio ($)")
    ax.set_title("Precio semanal y los 6 niveles (azul: entrada, naranja: salida)",
                 fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)


def panel_riesgo(ax):
    """Panel de riesgo con 5 filas espaciadas y una línea de ayuda (hallazgo H2)."""
    ax.axis("off")
    ax.set_title("Panel de riesgo (descriptivo, con datos pasados)",
                 fontsize=10, loc="left", pad=6)
    n = len(RIESGO)
    y0, y1 = 0.94, 0.06
    paso = (y0 - y1) / n
    for k, (nombre, valor, ayuda) in enumerate(RIESGO):
        y = y0 - k * paso
        ax.text(0.0, y, nombre, fontsize=9.4, va="center", weight="bold")
        ax.text(1.0, y, valor, fontsize=10.3, va="center", ha="right", weight="bold", color=AZUL)
        ax.text(0.0, y - paso * 0.42, ayuda, fontsize=8.5, va="center", color=GRIS, wrap=True)
        if k < n - 1:
            ax.plot([0, 1], [y - paso * 0.85, y - paso * 0.85],
                    color="#ddd", lw=0.6, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def desempeno_historico(ax):
    """Recuadro de desempeño histórico del SVM. En la entrega 1 los valores no
    se calculan; se marcan como 'se calcula en la entrega 2' (punto 4 §4.4)."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=GRIS, lw=1))
    ax.text(0.02, 0.86, "Desempeño histórico del modelo técnico (SVM)",
            fontsize=10, weight="bold", va="center")
    ax.text(0.02, 0.68, "Para que la probabilidad del SVM se lea con contexto, incluidos los errores (RN1).",
            fontsize=8.5, va="center", color=GRIS, style="italic")
    for k, (nombre, valor) in enumerate(DESEMPENO):
        y = 0.50 - k * 0.17
        ax.text(0.02, y, nombre, fontsize=9.3, va="center", weight="bold")
        ax.text(0.98, y, valor, fontsize=9, va="center", ha="right", color=GRIS, style="italic")


def registro_decision(ax):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec=GRIS, lw=1))
    ax.text(0.015, 0.86, "Registro de decisión (lo escribe el usuario)",
            fontsize=10, weight="bold", va="center")
    campos = [("Fecha", "2026-10-18"),
              ("Nivel", "Value ($61.60 · 22.0x P/E TTM · −12 % vs. precio actual)"),
              ("Lectura que más pesó", "Fundamental: p18 en su historia, pero el rebote pasado vino "
               "de caída de utilidades (Nota 2)."),
              ("Decisión", "Esperar; orden límite en $61.60."),
              ("Nota", "«Está barata, pero puede ser trampa de valor; quiero ver si el próximo "
               "10-Q confirma las utilidades.»")]
    for k, (a, b) in enumerate(campos):
        y = 0.68 - k * 0.15
        ax.text(0.015, y, a + ":", fontsize=9, va="center", color=GRIS)
        ax.text(0.21, y, b, fontsize=9, va="center")
    for k, txt in enumerate(["Editar niveles", "Guardar decisión"]):
        ax.text(0.70 + k * 0.155, 0.86, txt, fontsize=9, va="center", transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.4", fc="#eceff1", ec="#607d8b"))


def main():
    # Figura más grande que la v1 para dar aire a la franja de glosario, al panel de riesgo
    # y a las notas de la columna Fundamental (hallazgos H1 y H2).
    fig = plt.figure(figsize=(17, 20), facecolor="white")
    gs = fig.add_gridspec(
        6, 2,
        height_ratios=[0.65, 1.9, 3.4, 2.3, 1.7, 1.1],
        width_ratios=[1.35, 1],
        hspace=0.32, wspace=0.12,
        left=0.04, right=0.98, top=0.975, bottom=0.055,
    )
    encabezado(fig.add_subplot(gs[0, :]))
    franja_glosario(fig.add_subplot(gs[1, :]))
    tabla_niveles(fig.add_subplot(gs[2, :]))
    grafico_precio(fig.add_subplot(gs[3, 0]))
    panel_riesgo(fig.add_subplot(gs[3, 1]))
    notas_tabla(fig.add_subplot(gs[4, 0]))
    desempeno_historico(fig.add_subplot(gs[4, 1]))
    registro_decision(fig.add_subplot(gs[5, :]))
    fig.text(0.04, 0.030, "Industria piloto: consumo defensivo (21 empresas, referentes SPY y XLP). "
             "En otras industrias la pantalla avisa que el análisis no se ha probado.",
             fontsize=10, color=VERDE, weight="bold", va="center")
    fig.text(0.04, 0.010, "Línea base por volatilidad: frecuencia histórica con la que el precio tocó "
             "niveles a la misma distancia en días de volatilidad parecida (volatilidad diaria del "
             "último año). Si el modelo no la supera, no aporta.",
             fontsize=8.5, color=GRIS, va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=120)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
