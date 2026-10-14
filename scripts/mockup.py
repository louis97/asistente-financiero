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
# P(SVM) / base GBM (solo entradas), P(MC) total / parte sector / parte propia
NIVELES = [
    ("Deep value", "Entrada", 82.0, 11.0, 8, 15, "0.31 / 0.22", "0.28 (s 0.17 | p 0.11)"),
    ("Value", "Entrada", 90.0, 12.1, 18, 28, "0.47 / 0.38", "0.44 (s 0.27 | p 0.17)"),
    ("Valoración histórica", "Entrada", 97.0, 13.0, 45, 52, "0.62 / 0.55", "0.60 (s 0.36 | p 0.24)"),
    ("Negativo (conservador)", "Salida", 108.0, 14.5, 62, 60, "n/a", "0.55 (s 0.33 | p 0.22)"),
    ("Base", "Salida", 120.0, 16.1, 78, 71, "n/a", "0.36 (s 0.20 | p 0.16)"),
    ("Positivo", "Salida", 140.0, 18.8, 92, 88, "n/a", "0.15 (s 0.08 | p 0.07)"),
]
COLORES = {"Entrada": "#1b6ca8", "Salida": "#c2571a"}


def precio_ilustrativo(n=156, semilla=7):
    rng = np.random.default_rng(semilla)
    r = rng.normal(0.0008, 0.03, n)
    p = PRECIO * np.exp(np.cumsum(r) - r.sum())
    return p


def main():
    fig = plt.figure(figsize=(14, 9.2), facecolor="white")
    gs = fig.add_gridspec(3, 2, height_ratios=[0.5, 2.6, 2.8], width_ratios=[1.7, 1],
                          hspace=0.3, wspace=0.12, left=0.06, right=0.97, top=0.97, bottom=0.13)

    # Encabezado
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    ax.text(0.0, 0.7, f"{TICKER}  |  Precio: ${PRECIO:.2f}  |  Último reporte (filed): {FILED}",
            fontsize=15, weight="bold", va="center")
    ax.text(0.0, 0.15, "MOCKUP - TODOS LOS VALORES SON ILUSTRATIVOS, NO PROVIENEN DE DATOS REALES",
            fontsize=10, color="#b00020", va="center")
    ax.text(1.0, 0.7, "Niveles recalculados tras el reporte (precio = múltiplo x EPS)",
            fontsize=9, ha="right", va="center", color="#444")

    # Tabla de 6 niveles
    ax = fig.add_subplot(gs[1, :]); ax.axis("off")
    cols = ["Nivel", "Tipo", "Precio", "Múltiplo\nimplícito (P/E)", "Percentil\nhistórico", "Percentil\nindustria",
            "P(SVM) / base GBM\n(solo entradas)", "P(Monte Carlo): total\n(s: sector | p: propia)"]
    filas = [[n, t, f"${p:.0f}", f"{m:.1f}x", f"{h}", f"{i}", s, mc] for n, t, p, m, h, i, s, mc in NIVELES]
    tab = ax.table(cellText=filas, colLabels=cols, loc="center", cellLoc="center",
                   colWidths=[0.16, 0.07, 0.07, 0.11, 0.09, 0.09, 0.18, 0.23])
    tab.auto_set_font_size(False); tab.set_fontsize(9.5); tab.scale(1, 2.0)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#999")
        if r == 0:
            cell.set_facecolor("#eceff1"); cell.set_text_props(weight="bold")
        else:
            cell.set_facecolor("#e8f1f8" if NIVELES[r - 1][1] == "Entrada" else "#fbeee4")
    ax.set_title("Seis niveles x tres lecturas (fundamental comparativa, técnica SVM, probabilística)",
                 fontsize=11, loc="left", pad=2)

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

    # Panel de riesgo
    ax = fig.add_subplot(gs[2, 1]); ax.axis("off")
    ax.set_title("Panel de riesgo (ilustrativo)", fontsize=10, loc="left", pad=14)
    riesgo = [("Volatilidad anualizada (hist / EWMA / GARCH)", "28% / 31% / 30%"),
              ("VaR 95% / 99% semanal (hist)", "-6.1% / -9.4%"),
              ("Expected Shortfall 95%", "-8.0%"),
              ("Beta vs SPY / vs ETF sectorial", "1.12 / 0.95"),
              ("Parte sistemática de la varianza (R2)", "0.58"),
              ("Max drawdown (ventana)", "-34%"),
              ("Merton: PD = N(-d2)", "0.4%")]
    for k, (a, b) in enumerate(riesgo):
        y = 0.90 - k * 0.13
        ax.text(0.0, y, a, fontsize=9, va="center"); ax.text(1.0, y, b, fontsize=9, va="center", ha="right", weight="bold")
        ax.plot([0, 1], [y - 0.06, y - 0.06], color="#ddd", lw=0.6)

    fig.text(0.06, 0.04, "No es asesoría de inversión. El contenido no constituye una recomendación profesional "
             "en los términos del art. 2.40.1.1.2 del Decreto 2555 de 2010.\n"
             "Las probabilidades son estimaciones con incertidumbre, no señales de compra/venta.",
             fontsize=9.5, color="#b00020", weight="bold", va="center")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA, dpi=130)
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
