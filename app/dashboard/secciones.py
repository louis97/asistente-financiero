"""Secciones de la pantalla. Aquí solo se presenta: todo cálculo (lecturas, riesgo, modelo) viene de la API."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import pandas as pd
import streamlit as st

from app.dashboard.cliente import ErrorAcceso, ErrorServicio, ErrorValidacion
from app.dashboard.textos import (ALGORITMOS, NOMBRES_NIVEL, DISCLAIMER, GLOSARIO_BOLSILLO, LEYENDA_ASESORIA, PERIODO_PRUEBA,
                                  SUBTITULO_BANNER, TOOLTIPS)

# Paleta del mockup (validada con el validador de dataviz: azul y naranja separables con visión normal y con daltonismo)
AZUL, NARANJA = "#1f6aa5", "#c2571a"
FONDO_AZUL, FONDO_NARANJA, TINTA = "#e6f0f9", "#fbece2", "#1b2a38"
VERDE, ROJO = "#2e7d32", "#b00020"
SIN_DATO = "no disponible"


# ------------------------------------------------------------------ formato (coma decimal, punto de miles)
def _es(texto: str) -> str:
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def num(x, dec=2, sufijo=""):
    return SIN_DATO if x is None else _es(f"{x:,.{dec}f}").replace("-", "−") + sufijo


def pct(x, dec=None):
    """Fracción → «21 %»; con un decimal si es menor que 10 %."""
    if x is None:
        return SIN_DATO
    d = dec if dec is not None else (1 if abs(x) < 0.1 else 0)
    return _es(f"{x * 100:.{d}f}").replace("-", "−") + " %"


def usd(x):
    return "$" + num(x, 2)


def rango(lo, hi):
    if lo is None or hi is None:
        return SIN_DATO
    d = 1 if min(abs(lo), abs(hi)) < 0.1 else 0                    # mismos decimales en los dos extremos
    return f"{pct(lo, d)[:-2]}–{pct(hi, d)}"


def pctil(x):
    return None if x is None else f"p{round(x * 100)}"


def _nombre(n):
    return n["nombre"][:1].upper() + n["nombre"][1:]


# ------------------------------------------------------------------ banner, encabezado y avisos
def banner():
    st.markdown(f":red[**{DISCLAIMER}** {SUBTITULO_BANNER}]")     # el color :red[] se adapta al tema claro u oscuro
    st.caption(LEYENDA_ASESORIA)


def _instantanea(fuente):
    return "datos de la instantánea, no de la actualización diaria" if fuente == "snapshot" else "datos de la actualización diaria"


def encabezado(res):
    lec = res["lecturas"]
    pe, pb = lec["pe_actual"], lec["pb_actual"]
    izq, der = st.columns([4, 1.3])
    izq.markdown(f"### {lec['ticker']}  |  Precio: {usd(lec['precio'])}  |  P/E (TTM): "
                 f"{num(pe, 1, 'x')}  |  P/B: {num(pb, 1, 'x')}", help=TOOLTIPS["P/E"] + " " + TOOLTIPS["P/B"])
    if lec["industria_validada"]:
        der.markdown(f"<span style='background:{VERDE};color:white;padding:4px 10px;border-radius:6px;font-weight:700'>"
                     f"Industria: consumo defensivo (industria piloto)</span>", unsafe_allow_html=True)
    else:
        der.markdown(f"<span style='background:{ROJO};color:white;padding:4px 10px;border-radius:6px;font-weight:700'>"
                     f"industria no validada</span>", unsafe_allow_html=True)
    st.markdown(f"**Datos al {lec['fecha_dato']}** · {_instantanea(lec['fuente_datos'])}")
    if res["origen"] == "ejemplo":
        st.caption("Niveles de ejemplo (-20 %, -12 %, -4 %, +8 %, +16 % y +28 % del precio actual); no son una sugerencia. "
                   "Cámbialos abajo, en «Editar niveles».")
    elif res["origen"] == "guardados":
        st.caption("Niveles guardados por ti.")


def avisos(res):
    lec = res["lecturas"]
    if res["acceso"] == "invalido":
        st.error("Credenciales inválidas")
    for a in lec["advertencias"]:
        st.warning(a)
    if any("fuera del rango entrenado" in a for a in lec["advertencias"]):
        st.caption("Fuera del rango entrenado: " + TOOLTIPS["fuera del rango entrenado"])
    for a in res.get("avisos", []):
        st.warning(a)
    if not lec["industria_validada"]:
        st.warning("Industria no validada: el modelo técnico y la simulación no se han probado en esta industria, "
                   "así que las probabilidades de las dos últimas columnas llevan esta advertencia. "
                   "La lectura fundamental y el panel de riesgo sí se muestran.")


def franja_glosario():
    with st.container(border=True):
        st.markdown("**Cómo leer esta pantalla (glosario de bolsillo)**")
        for t, d in GLOSARIO_BOLSILLO.items():
            st.markdown(f"**{t}:** {d}")


# ------------------------------------------------------------------ tabla de 6 niveles
def _motivo(advertencias, *claves, defecto):
    for a in advertencias:
        if any(c in a.lower() for c in claves):
            return a.split(": ", 1)[-1] if ": " in a else a
    return defecto


def _fila(i, n, adv, industria_validada):
    es_ent = n["tipo"] == "entrada"
    # Fundamental
    if n["pe_implicito"] is None:
        fund = f"{SIN_DATO}: " + _motivo(adv, "utilidad", "p/e", defecto="sin datos de utilidad por acción")
    else:
        partes = [f"{pctil(n['percentil_historia']) or SIN_DATO} historia",
                  f"{pctil(n['percentil_industria'])} industria" if n["percentil_industria"] is not None else "industria sin comparar"]
        if n["percentil_pe_norm"] is not None:
            partes.append(f"P/E normalizado {pctil(n['percentil_pe_norm'])}")
        fund = " · ".join(partes) + (f" → ver Nota {i + 1}" if es_ent else "")
    # Técnica (solo entradas) y probabilística (solo salidas)
    tec, prob = "—", "—"
    if es_ent:
        t = n["tecnica"]
        tec = (f"{pct(t['prob'])} · línea base {pct(t['linea_base'])} · rango de la calibración histórica "
               f"{rango(t['ic_lo'], t['ic_hi'])}" if t and t["prob"] is not None else
               f"{SIN_DATO}: " + _motivo(adv, "técnica", "historia", defecto="sin lectura técnica para este nivel"))
    else:
        p = n["probabilistica"]
        prob = (f"{pct(p['prob'])} · error de simulación {rango(p['ic_lo'], p['ic_hi'])}" if p and p["prob"] is not None else
                f"{SIN_DATO}: " + _motivo(adv, "probabilística", "simulación", "historia", defecto="sin simulación para este nivel"))
    return {"Nivel": f"{_nombre(n)} ({n['tipo']})", "Precio": usd(n["precio"]),
            "% vs. precio actual": ("+" if n["pct_vs_actual"] > 0 else "") + pct(n["pct_vs_actual"], 0),
            "P/E (TTM)": num(n["pe_implicito"], 1, "x"), "P/B": num(n["pb_implicito"], 1, "x"),
            "Fundamental (percentiles)": fund,
            "Prob. de tocar en 60 días (técnica)": tec,
            "Prob. de alcanzar la salida (simulación)": prob}


def tabla_niveles(res):
    lec = res["lecturas"]
    st.markdown("**Seis niveles del usuario** (3 de entrada, en azul, y 3 de salida, en naranja), con sus tres lecturas.")
    filas = [_fila(i, n, lec["advertencias"], lec["industria_validada"]) for i, n in enumerate(lec["niveles"])]
    df = pd.DataFrame(filas)
    tipos = [n["tipo"] for n in lec["niveles"]]

    def colorear(fila):
        fondo = FONDO_AZUL if tipos[fila.name] == "entrada" else FONDO_NARANJA
        return [f"background-color: {fondo}; color: {TINTA}"] * len(fila)

    cols = list(df.columns)
    ayudas = {cols[0]: TOOLTIPS["nivel"] + " " + " ".join(TOOLTIPS["nivel: " + n] for n in NOMBRES_NIVEL), cols[2]: TOOLTIPS["% vs. precio actual"], cols[3]: TOOLTIPS["P/E"],
              cols[4]: TOOLTIPS["P/B"], cols[5]: "Percentil del P/E del nivel en la historia de la empresa y frente a la industria, solo si hay P/E. " + TOOLTIPS["percentil"] + " " + TOOLTIPS["P/E normalizado"],
              cols[6]: "Probabilidad de tocar el nivel en 60 días hábiles, solo entradas. " + TOOLTIPS["modelo técnico"] + " Entre paréntesis: la línea base y el " + TOOLTIPS["rango de la calibración histórica"],
              cols[7]: "Probabilidad de alcanzar la salida en 52 semanas, solo salidas. " + TOOLTIPS["lectura probabilística"] + " " + TOOLTIPS["error de simulación"] + " " + TOOLTIPS["horizonte 52 semanas"]}
    cfg = {c: st.column_config.TextColumn(c, help=ayudas.get(c), width="large" if i >= 5 else "medium") for i, c in enumerate(cols)}
    st.dataframe(df.style.apply(colorear, axis=1), column_config=cfg, hide_index=True, width="stretch")
    st.caption("Horizonte 52 semanas (fijo) en la simulación; «error de simulación» mide la precisión del cálculo, "
               "no la incertidumbre del futuro.", help=TOOLTIPS["horizonte 52 semanas"])


def notas_fundamental(res):
    lec = res["lecturas"]
    with st.container(border=True):
        st.markdown("**Notas de la columna Fundamental** (lectura comparativa, solo entradas)")
        for i, n in enumerate(lec["niveles"][:3]):
            if n["lectura_trampa"]:
                txt = n["lectura_trampa"]
            elif not lec["industria_validada"]:
                txt = "sin lectura de posible deterioro de utilidades: el ticker está fuera de la industria piloto."
            elif n["pe_implicito"] is None:
                txt = "sin lectura de posible deterioro de utilidades: " + _motivo(lec["advertencias"], "utilidad", "p/e", defecto="sin datos de utilidad por acción")
            else:
                txt = "sin lectura de posible deterioro de utilidades para este nivel."
            st.markdown(f"**Nota {i + 1} ({_nombre(n)}).** {txt}")


# ------------------------------------------------------------------ panel de riesgo
def _txt_caida(rg):
    fondo = f"el fondo fue el {rg['caida_maxima_fecha']}; " if rg.get("caida_maxima_fecha") else ""
    if rg.get("recuperacion_semanas") is not None:
        rec = f"tardó {rg['recuperacion_semanas']} semanas en recuperarse"
    elif rg.get("caida_maxima_fecha"):
        rec = "aún no se recupera"
    else:
        rec = "sin dato de recuperación"
    return f"mayor caída acumulada desde un máximo en la historia semanal; {fondo}{rec}."


def panel_riesgo(rg):
    st.markdown("**Panel de riesgo** (descriptivo, con datos pasados)")
    fc = rg["frec_caidas_fuertes"]
    filas = [
        ("Cuánto se mueve en un año típico (volatilidad)", pct(rg["vol_anual"]), TOOLTIPS["σ (volatilidad)"],
         "subida o bajada típica anual."),
        ("Peor semana típica (1 de cada 20 cae al menos esto)", pct(rg["p5_semanal"]), TOOLTIPS["peor semana típica"],
         "percentil 5 del retorno semanal."),
        ("Caídas semanales fuertes: observadas vs esperadas", f"{pct(fc['observada'])} vs {pct(fc['esperada'])}",
         TOOLTIPS["caídas semanales fuertes"], "fracción de semanas con caída fuerte, observada frente a la esperada en un mercado sin rachas."),
        (f"Peor caída desde un pico (desde {(rg.get('desde') or '')[:4] or 'el inicio de los datos'})", pct(rg["caida_maxima"]),
         TOOLTIPS["caída máxima"], _txt_caida(rg)),
        ("Cuánto se mueve con el sector (R² · ΔR²)",
         f"R² {num(rg['r2_mercado_sector'])} · ΔR² {num(rg['delta_r2_sector'])}", TOOLTIPS["R² y ΔR²"],
         "R²: parte del movimiento explicada por mercado y sector; ΔR²: lo que el sector añade al mercado."),
    ]
    for etiqueta, valor, ayuda, expl in filas:
        c1, c2 = st.columns([3, 1.4])
        c1.markdown(f"**{etiqueta}**", help=ayuda)
        c2.markdown(f"<div style='text-align:right;font-weight:700'>{valor}</div>", unsafe_allow_html=True)
        st.caption(expl)


# ------------------------------------------------------------------ gráficos (matplotlib, tinta fija sobre fondo blanco)
def _separar_etiquetas(ys, hueco):
    """Ordena de abajo hacia arriba y empuja las etiquetas para que no se pisen; devuelve las y finales en el orden dado."""
    orden = sorted(range(len(ys)), key=lambda k: ys[k])
    final = {}
    prev = None
    for k in orden:
        y = ys[k] if prev is None else max(ys[k], prev + hueco)
        final[k] = prev = y
    return [final[k] for k in range(len(ys))]


def figura_niveles(serie, lec):
    fechas = pd.to_datetime(serie["fechas"])
    cierres = serie["cierres"]
    fig, ax = plt.subplots(figsize=(9, 4.4), dpi=110, facecolor="white")
    ax.set_facecolor("white")
    ax.plot(fechas, cierres, color="#2b2b2b", lw=1.3, label="Precio diario")
    span = fechas[-1] - fechas[0]
    x_lab = fechas[-1] + span * 0.015
    niveles = lec["niveles"]
    precios = [n["precio"] for n in niveles] + [lec["precio"]]
    lo, hi = min(min(cierres), *precios), max(max(cierres), *precios)
    pad = (hi - lo) * 0.05
    ax.set_ylim(lo - pad, hi + pad)
    colores = [AZUL if n["tipo"] == "entrada" else NARANJA for n in niveles] + ["#2b2b2b"]
    textos = [f"{_nombre(n)} {usd(n['precio'])}" for n in niveles] + [f"Actual {usd(lec['precio'])}"]
    ys = _separar_etiquetas(precios, (hi - lo) * 0.055)
    for n, p, c, t, y in zip(niveles + [None], precios, colores, textos, ys):
        if n is None:
            ax.axhline(p, color=c, lw=0.8, ls=":")
            ax.plot([fechas[-1]], [p], "o", color=c, ms=6, mec="white", mew=1.5, zorder=5)
        else:
            ax.axhline(p, color=c, lw=1.4, ls="--", xmax=0.99)
        ax.plot([fechas[-1], x_lab], [p, y], color=c, lw=0.8, clip_on=False)
        ax.text(x_lab, y, t, va="center", ha="left", fontsize=8, color="#333333", clip_on=False)
    ax.set_xlim(fechas[0], fechas[-1])
    ax.plot([], [], color=AZUL, ls="--", lw=1.4, label="Niveles de entrada")
    ax.plot([], [], color=NARANJA, ls="--", lw=1.4, label="Niveles de salida")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), frameon=False, fontsize=8, labelcolor="#333333", ncol=3)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.grid(axis="y", color="#e3e3e3", lw=0.6)
    ax.tick_params(colors="#555555", labelsize=8, length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#bbbbbb")
    fig.subplots_adjust(left=0.07, right=0.80, top=0.91, bottom=0.09)
    return fig


def _posicion(lec):
    ent = max((n for n in lec["niveles"] if n["tipo"] == "entrada"), key=lambda n: n["precio"])
    sal = min((n for n in lec["niveles"] if n["tipo"] == "salida"), key=lambda n: n["precio"])
    return (f"Posición: precio actual {usd(lec['precio'])}, entre {_nombre(ent)} {usd(ent['precio'])} y "
            f"{_nombre(sal)} {usd(sal['precio'])} (descriptivo, sin veredicto).")


def grafico_niveles(res):
    st.markdown("**Precio diario, últimos 5 años, y los 6 niveles** (azul: entrada, naranja: salida)")
    fig = figura_niveles(res["serie"], res["lecturas"])
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.caption(_posicion(res["lecturas"]))


def figura_calibracion(modelo):
    tramos = modelo["calibracion_prueba"]
    fig, ax = plt.subplots(figsize=(4.6, 4.0), dpi=110, facecolor="white")
    ax.set_facecolor("white")
    ax.plot([0, 1], [0, 1], color="#888888", ls="--", lw=1, label="Calibración perfecta")
    for k, t in enumerate(tramos):
        ax.fill_between([t["tramo_lo"], t["tramo_hi"]], t["ic_lo"], t["ic_hi"], color=AZUL, alpha=0.16, lw=0,
                        label="IC95 de la frecuencia real" if k == 0 else None)
        ax.plot([t["tramo_lo"], t["tramo_hi"]], [t["tasa_obs"]] * 2, color=AZUL, lw=3, solid_capstyle="butt",
                label="Frecuencia real en el tramo" if k == 0 else None)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.7)
    ax.set_xlabel("Probabilidad que dio el modelo (tramos)", fontsize=8, color="#333333")
    ax.set_ylabel("Frecuencia real de toque", fontsize=8, color="#333333")
    f = mt.FuncFormatter(lambda v, _: f"{v * 100:.0f} %")
    ax.xaxis.set_major_formatter(f)
    ax.yaxis.set_major_formatter(f)
    ax.grid(color="#e3e3e3", lw=0.6)
    ax.tick_params(colors="#555555", labelsize=8, length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#bbbbbb")
    ax.legend(loc="upper left", frameon=False, fontsize=7.5, labelcolor="#333333")
    fig.tight_layout()
    return fig


# ------------------------------------------------------------------ recuadro de desempeño del modelo
def _veredicto(m):
    lo, hi = m["delta_auc_ic95"]
    cifras = f"ΔAUC {num(m['delta_auc'], 3)}, IC95 [{num(lo, 3)}; {num(hi, 3)}]"
    if hi < 0:
        return f"En {PERIODO_PRUEBA} el modelo ordenó peor que la línea base ({cifras}): no aporta sobre ella."
    if lo > 0:
        return f"En {PERIODO_PRUEBA} el modelo ordenó mejor que la línea base ({cifras})."
    return f"En {PERIODO_PRUEBA} el modelo no se distinguió de la línea base ({cifras})."


def recuadro_desempeno(modelo):
    m = modelo["metricas_prueba"]
    alg = ALGORITMOS.get(modelo.get("algoritmo"), modelo.get("algoritmo", "modelo"))
    with st.container(border=True):
        st.markdown(f"**Desempeño histórico del modelo técnico ({alg})**")
        st.caption(f"Período de prueba: {PERIODO_PRUEBA}, datos que el modelo no vio al entrenarse. "
                   "Se incluye para leer la probabilidad con contexto, errores incluidos.")
        st.info(_veredicto(m) + " Úsalo como referencia informativa junto a la línea base: el modelo ordena sobre todo "
                "por qué tan lejos queda el nivel, y la línea base (volatilidad y distancia) hace casi lo mismo.")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("AUC del modelo", num(m["auc"], 3), help=TOOLTIPS["AUC"])
        c1.caption(f"IC95 [{num(m['auc_ic95'][0], 3)}; {num(m['auc_ic95'][1], 3)}]")
        c2.metric("AUC de la línea base", num(m["auc_linea_base"], 3), help=TOOLTIPS["línea base"])
        c3.metric("ΔAUC (modelo − línea base)", num(m["delta_auc"], 3), help=TOOLTIPS["ΔAUC"])
        c3.caption(f"IC95 [{num(m['delta_auc_ic95'][0], 3)}; {num(m['delta_auc_ic95'][1], 3)}]")
        c4.metric("Brier (calibración)", num(m["brier"], 3), help=TOOLTIPS["Brier"])
        c4.caption(f"Frente a una tasa constante: mejora {num(m['bss'], 3)} (IC95 [{num(m['bss_ic95'][0], 3)}; "
                   f"{num(m['bss_ic95'][1], 3)}]). Frente a la línea base: {num(m['bss_vs_linea_base'], 3)} "
                   f"(IC95 [{num(m['bss_vs_linea_base_ic95'][0], 3)}; {num(m['bss_vs_linea_base_ic95'][1], 3)}]).")
        tramos = modelo["calibracion_prueba"]
        arriba = sum(1 for t in tramos if t["ic_lo"] > t["tramo_hi"])
        abajo = sum(1 for t in tramos if t["ic_hi"] < t["tramo_lo"])
        coh = len(tramos) - arriba - abajo
        st.markdown("**Diagrama de calibración**", help=TOOLTIPS["calibración"])
        g, t = st.columns([1, 1])
        fig = figura_calibracion(modelo)
        g.pyplot(fig, width="stretch")
        plt.close(fig)
        t.markdown(f"Cada tramo agrupa lecturas por la probabilidad que dio el modelo (franja horizontal). El modelo está "
                   f"calibrado donde la franja cruza la diagonal. En {coh} de {len(tramos)} tramos la frecuencia real es "
                   f"compatible con lo prometido; {arriba} quedó por encima y {abajo} por debajo.")
        t.dataframe(pd.DataFrame([{"Tramo del modelo": f"{pct(x['tramo_lo'])} a {pct(x['tramo_hi'])}",
                                   "Frecuencia real": pct(x["tasa_obs"]), "IC95": rango(x["ic_lo"], x["ic_hi"]),
                                   "Lecturas": f"{x['n']:,}".replace(",", ".")} for x in tramos]),
                    hide_index=True, width="stretch")


# ------------------------------------------------------------------ edición de niveles (RF7)
def _leer_niveles_form():
    ss = st.session_state
    ent = [{"valor": float(ss[f"nv_valor_{i}"]), "unidad": ss[f"nv_unidad_{i}"]} for i in range(3)]
    sal = [{"valor": float(ss[f"nv_valor_{i}"]), "unidad": ss[f"nv_unidad_{i}"]} for i in range(3, 6)]
    return ent, sal


def _grupo_del_error(detalle):
    d = detalle.lower()
    if d.startswith("la entrada"):
        return "entradas"
    if d.startswith("la salida"):
        return "salidas"
    return "general"


def _cb_editar(cliente_fn):
    ss = st.session_state
    ss["err_niveles"], ss["ok_niveles"] = {}, None
    res = ss["res"]
    ent, sal = _leer_niveles_form()
    try:
        lec = cliente_fn().lecturas(res["ticker"], ent, sal)
    except ErrorValidacion as e:
        ss["err_niveles"] = {_grupo_del_error(e.detalle): e.detalle}     # no recalcula
        return
    except ErrorServicio as e:
        ss["err_niveles"] = {"general": e.mensaje}
        return
    res.update(lecturas=lec, entradas=ent, salidas=sal, origen="editados", avisos=[])
    ss["ok_niveles"] = "Niveles recalculados."


def _cb_guardar(cliente_fn):
    ss = st.session_state
    ss["err_niveles"], ss["ok_niveles"] = {}, None
    ent, sal = _leer_niveles_form()
    try:
        cliente_fn().guardar_niveles(ss["res"]["ticker"], ent, sal)
    except ErrorValidacion as e:
        ss["err_niveles"] = {_grupo_del_error(e.detalle): e.detalle}
        return
    except ErrorAcceso:
        ss["err_niveles"] = {"general": "Credenciales inválidas" if (ss.get("alias") or "").strip()
                             else "Inicia sesión con tu alias y código para guardar tus niveles."}
        return
    except ErrorServicio as e:
        ss["err_niveles"] = {"general": e.mensaje}
        return
    ss["ok_niveles"] = "Niveles guardados."


def edicion_niveles(res, cliente_fn):
    ss = st.session_state
    errores = ss.get("err_niveles") or {}
    with st.expander("Editar niveles (precio en dólares o múltiplo P/E)", expanded=True):
        with st.form("form_niveles"):
            cols = st.columns(2)
            slots = {}
            for g, (col, titulo, rot, ini) in enumerate([(cols[0], "Entradas (por debajo del precio actual)",
                                                          ["deep value", "value", "valoración histórica"], 0),
                                                         (cols[1], "Salidas (por encima del precio actual)",
                                                          ["negativo", "base", "positivo"], 3)]):
                with col:
                    st.markdown(f"**{titulo}**")
                    slots["entradas" if g == 0 else "salidas"] = st.empty()
                    for j, nombre in enumerate(rot):
                        i = ini + j
                        a, b = st.columns([2, 1])
                        a.number_input(nombre.capitalize(), min_value=0.01, step=0.5, format="%.2f", key=f"nv_valor_{i}",
                                       help=TOOLTIPS["nivel: " + nombre])
                        b.selectbox("Unidad", ["precio", "pe"], key=f"nv_unidad_{i}",
                                    help="precio: dólares por acción; pe: múltiplo P/E (TTM). " + TOOLTIPS["P/E"])
            slots["general"] = st.empty()
            b1, b2 = st.columns(2)
            b1.form_submit_button("Editar niveles", on_click=_cb_editar, args=(cliente_fn,))
            b2.form_submit_button("Guardar niveles", on_click=_cb_guardar, args=(cliente_fn,))
        for g, msg in errores.items():
            slots[g].error(msg)
        if ss.get("ok_niveles"):
            st.success(ss["ok_niveles"])


# ------------------------------------------------------------------ registro de decisiones (RF8)
LECTURAS = ["Fundamental", "Técnica", "Probabilística"]


def registro_decisiones(res, cliente_fn):
    lec = res["lecturas"]
    with st.container(border=True):
        st.markdown("**Registro de decisión** (lo escribe el usuario)")
        if res["acceso"] != "ok":
            st.info("Inicia sesión con tu alias y código (barra lateral) y pulsa Calcular para registrar decisiones y ver "
                    "tu historial y tus niveles guardados.")
            return
        etiquetas = {f"{_nombre(n)} ({n['tipo']}) · {usd(n['precio'])} · {pct(n['pct_vs_actual'], 0)} vs. precio actual": n
                     for n in lec["niveles"]}
        with st.form("form_registro", clear_on_submit=True):
            sel = st.selectbox("Nivel", list(etiquetas), key="reg_nivel",
                               help=TOOLTIPS["nivel"] + " " + " ".join(TOOLTIPS["nivel: " + n] for n in NOMBRES_NIVEL))
            lectura = st.selectbox("Lectura que más pesó", LECTURAS, key="reg_lectura",
                                   help="Fundamental: percentiles y múltiplos. Técnica: " + TOOLTIPS["lectura técnica"])
            decision = st.text_input("Decisión", key="reg_decision", max_chars=120)
            nota = st.text_area("Nota", key="reg_nota", max_chars=2000)
            enviar = st.form_submit_button("Guardar decisión")
        if enviar:
            n = etiquetas[sel]
            try:
                cliente_fn().crear_decision(lec["ticker"], f"{_nombre(n)} ({n['tipo']})",
                                            {"lectura_principal": lectura, "decision": decision, "precio": n["precio"],
                                             "pct_vs_actual": n["pct_vs_actual"], "fecha_dato": lec["fecha_dato"]}, nota)
                st.success("Decisión guardada.")
            except ErrorAcceso:
                st.error("Credenciales inválidas")
            except (ErrorServicio, ErrorValidacion) as e:
                st.error(getattr(e, "mensaje", None) or getattr(e, "detalle", "No se pudo guardar la decisión."))
        st.markdown("**Historial de decisiones** (la más reciente primero)")
        try:
            filas = cliente_fn().decisiones()
        except ErrorAcceso:
            st.error("Credenciales inválidas")
            return
        except ErrorServicio as e:
            st.warning(e.mensaje)
            return
        if not filas:
            st.caption("Aún no hay decisiones guardadas.")
            return
        filas = sorted(filas, key=lambda f: f["fecha"], reverse=True)
        st.dataframe(pd.DataFrame([{"Fecha": f["fecha"][:10], "Ticker": f["ticker"], "Nivel": f["nivel"],
                                    "Lectura que más pesó": f["lectura"].get("lectura_principal", ""),
                                    "Decisión": f["lectura"].get("decision", ""), "Nota": f["nota"]} for f in filas]),
                     hide_index=True, width="stretch")


# ------------------------------------------------------------------ pie
def _fecha_hora(iso):
    return SIN_DATO if not iso else iso.replace("T", " ")[:16] + " UTC"


def pie(res, estado):
    lec = res["lecturas"] if res else None
    st.divider()
    st.markdown(":green[**Industria piloto: consumo defensivo (21 empresas, referentes SPY y XLP). "
                "En otras industrias la pantalla avisa que el análisis no se ha probado.**]")
    st.caption("Línea base por volatilidad: frecuencia histórica con la que el precio tocó niveles a la misma distancia en días de "
               "volatilidad parecida. Si el modelo no la supera, no aporta.", help=TOOLTIPS["línea base"])
    fuente = _instantanea(estado["fuente_datos"])
    st.caption(f"Último dato: {estado['ultimo_dato'] or SIN_DATO} · último recálculo: {_fecha_hora(estado['ultimo_recalculo'])} · {fuente}."
               + (f" Datos de este ticker al {lec['fecha_dato']}." if lec else ""))
    st.markdown(f"**{DISCLAIMER}**")
    st.caption(LEYENDA_ASESORIA)
