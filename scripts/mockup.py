"""Mockup (wireframe) del dashboard del asistente bursatil.

Todos los valores son ILUSTRATIVOS (no provienen de datos reales).
Salida: entregables/entrega_1/assets/mockup.png
Uso: uv run python scripts/mockup.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SALIDA = Path(__file__).resolve().parents[1] / "entregables/entrega_1/assets/mockup.png"

TICKER, PRECIO, FILED = "XXXX", 100.0, "2026-08-01"

# nivel, tipo, precio, multiplo implicito (P/E), pct historico, pct industria,
# P(SVM) [IC] / base tasa por decil de σ (solo entradas), P(MC) con sector / sin sector, divergencia precio vs multiplo
NIVELES = [
    ("Deep value", "Entrada", 82.0, 11.0, 8, 15, "0.31 [0.24-0.38] · base σ 0.22", "con sector 0.28 · sin sector 0.11", False),
    ("Value", "Entrada", 90.0, 12.1, 18, 28, "0.47 [0.40-0.54] · base σ 0.38", "con sector 0.44 · sin sector 0.19", True),
    ("Valoración histórica", "Entrada", 97.0, 13.0, 45, 52, "0.62 [0.55-0.69] · base σ 0.55", "con sector 0.60 · sin sector 0.31", False),
    ("Negativo (conservador)", "Salida", 108.0, 14.5, 62, 60, "n/a", "con sector 0.55 · sin sector 0.40", False),
    ("Base", "Salida", 120.0, 16.1, 78, 71, "n/a", "con sector 0.36 · sin sector 0.21", False),
    ("Positivo", "Salida", 140.0, 18.8, 92, 88, "n/a", "con sector 0.15 · sin sector 0.09", False),
]
COLORES = {"Entrada": "#1b6ca8", "Salida": "#c2571a"}


def precio_ilustrativo(n=156, semilla=7):
    rng = np.random.default_rng(semilla)
    r = rng.normal(0.0008, 0.03, n)
    p = PRECIO * np.exp(np.cumsum(r) - r.sum())
    return p


def main():
    fig = plt.figure(figsize=(15, 11), facecolor="white")
    gs = fig.add_gridspec(3, 2, height_ratios=[0.45, 2.6, 3.4], width_ratios=[1.45, 1],
                          hspace=0.28, wspace=0.1, left=0.05, right=0.97, top=0.97, bottom=0.215)

    # Encabezado
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    ax.text(0.0, 0.7, f"{TICKER}  |  Precio: ${PRECIO:.2f}  |  Último reporte (filed): {FILED}",
            fontsize=15, weight="bold", va="center")
    ax.text(0.0, 0.15, "MOCKUP - ILUSTRATIVO: TODOS LOS VALORES SON INVENTADOS, NO PROVIENEN DE DATOS REALES",
            fontsize=10, color="#b00020", va="center")
    ax.text(1.0, 0.7, "Niveles por múltiplo recalculados tras el reporte (precio = múltiplo x EPS)",
            fontsize=9, ha="right", va="center", color="#444")

    # Tabla de 6 niveles
    ax = fig.add_subplot(gs[1, :]); ax.axis("off")
    cols = ["Nivel", "Tipo", "Precio", "Múltiplo\nimplícito (P/E)", "Percentil\nhistórico", "Percentil\nindustria",
            "P(SVM) [intervalo] · base decil σ\n(solo entradas)", "P(Monte Carlo)\ncon vs sin componente sector"]
    filas = []
    for n, t, p_, m, h, i_, svm, mc, div in NIVELES:
        filas.append([n + ("  ▲ diverge" if div else ""), t, f"${p_:.0f}", f"{m:.1f}x", f"p{h}", f"p{i_}", svm, mc])
    tab = ax.table(cellText=filas, colLabels=cols, loc="center", cellLoc="center",
                   colWidths=[0.165, 0.06, 0.06, 0.10, 0.075, 0.075, 0.24, 0.225])
    tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 2.0)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#999")
        if r == 0:
            cell.set_facecolor("#eceff1"); cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#e8f1f8" if NIVELES[r - 1][1] == "Entrada" else "#fbeee4")
            if c == 0 and NIVELES[r - 1][8]:
                cell.set_text_props(color="#b00020", weight="bold")
    ax.set_title("Seis niveles x tres lecturas (fundamental comparativa, técnica SVM, probabilística) - "
                 "▲ diverge: el nivel en precio y el nivel en múltiplo no coinciden (el usuario decide cuál conservar)",
                 fontsize=9.5, loc="left", pad=2)

    # Grafico de precio
    ax = fig.add_subplot(gs[2, 0])
    p = precio_ilustrativo(); x = np.arange(len(p))
    ax.plot(x, p, color="#222", lw=1.3)
    for n, t, pr, *_ in NIVELES:
        ax.axhline(pr, color=COLORES[t], ls="--", lw=1)
        ax.text(len(p) + 1, pr, f"{n} ${pr:.0f}", fontsize=8, va="center", color=COLORES[t],
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax.set_xlim(0, len(p) + 38); ax.set_xlabel("Semanas (ilustrativo)"); ax.set_ylabel("Precio ($)")
    ax.set_title("Precio semanal y los 6 niveles (azul: entrada, naranja: salida)", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)

    # Columna derecha: desempeno historico + panel de riesgo
    sub = gs[2, 1].subgridspec(2, 1, height_ratios=[1.0, 1.9], hspace=0.2)

    ax = fig.add_subplot(sub[0]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False, ec="#1b6ca8", lw=1.2))
    ax.text(0.02, 0.88, "Desempeño histórico (ilustrativo)", fontsize=10, weight="bold", va="center")
    hist = [("AUC walk-forward: SVM / base decil σ", "0.61 / 0.54"),
            ("Brier: SVM / base decil σ", "0.21 / 0.24"),
            ("% de errores (falsas entradas, umbral 0.5)", "37%")]
    for k, (a, b) in enumerate(hist):
        y = 0.62 - k * 0.22
        ax.text(0.02, y, a, fontsize=8.5, va="center"); ax.text(0.98, y, b, fontsize=8.5, va="center", ha="right", weight="bold")

    ax = fig.add_subplot(sub[1]); ax.axis("off")
    ax.set_title("Panel de riesgo (ilustrativo)", fontsize=10, loc="left", pad=10)
    riesgo = [("Volatilidad anualizada (hist / EWMA / GARCH)", "28% / 31% / 30%"),
              ("VaR 95% / 99% semanal (hist)", "-6.1% / -9.4%"),
              ("VaR paramétrico 95% / 99% semanal", "-5.8% / -8.3%"),
              ("Expected Shortfall 95%", "-8.0%"),
              ("Beta / alfa vs SPY (anual)", "1.12 / +1.8%"),
              ("Beta vs ETF sectorial · R2 (parte sistemática)", "0.95 · 0.58"),
              ("Sharpe (anualizado)", "0.42"),
              ("Max drawdown (ventana)", "-34%"),
              ("Merton d2 (orden relativo de apalancamiento)", "11.3")]
    for k, (a, b) in enumerate(riesgo):
        y = 0.94 - k * 0.108
        ax.text(0.0, y, a, fontsize=8.5, va="center"); ax.text(1.0, y, b, fontsize=8.5, va="center", ha="right", weight="bold")
        ax.plot([0, 1], [y - 0.05, y - 0.05], color="#ddd", lw=0.6)

    # Franja inferior: indicadores, botones, disclaimer
    fig.text(0.05, 0.14, "Rasgos que más pesaron en P(SVM) del nivel Deep value (ilustrativo): "
             "σ condicional alta (-), drawdown del SPY (+), RSI(14) alto (+).\n"
             "Un score es una probabilidad con su intervalo, su línea base y sus errores históricos; no es una señal.",
             fontsize=9, color="#222", va="center")
    for k, txt in enumerate(["Editar nivel", "Registrar decisión"]):
        fig.text(0.05 + k * 0.13, 0.085, txt, fontsize=10, ha="left", va="center",
                 bbox=dict(boxstyle="round,pad=0.5", fc="#eceff1", ec="#607d8b"))
    fig.text(0.31, 0.085, "(botones ilustrativos: no hacen nada en el wireframe)", fontsize=8.5, color="#666", va="center")
    fig.text(0.05, 0.033, "No es asesoría de inversión. El contenido no constituye una recomendación profesional "
             "en los términos del art. 2.40.1.1.2 del Decreto 2555 de 2010.\n"
             "Las probabilidades son estimaciones con incertidumbre, no señales de compra/venta. TODO ILUSTRATIVO.",
             fontsize=9.5, color="#b00020", weight="bold", va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=130)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
