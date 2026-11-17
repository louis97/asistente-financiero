"""Traducción de los niveles del usuario y sus lecturas (fundamental, técnica y probabilística). Sin FastAPI."""
import math

import numpy as np
import pandas as pd

from app.api import datos as dt
from app.api import modelo as md
from app.api.esquemas import (NOMBRES_ENTRADAS, NOMBRES_SALIDAS, LecturaNivel, Nivel, Probabilistica,
                              RespuestaLecturas, Tecnica)
import comunes as cm   # noqa: E402

QUINTIL = 0.2                  # el "barato" de nb04 (percentil propio ≤ 0,2)
MAX_DESFASE_PARES = 14         # días: un par cuyo último dato es más viejo que esto no entra al percentil de la industria
MSG_PE = "P/E no calculable: utilidad por acción no positiva o no publicada"


def _f(x):
    """float o None (nunca NaN/inf en el JSON)."""
    if x is None:
        return None
    x = float(x)
    return x if math.isfinite(x) else None


def _fmt(x: float) -> str:
    return f"{x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def a_precio(nivel: Nivel, eps_ttm: float | None) -> float:
    """Unidad `precio` → el valor; unidad `pe` → valor × EPS TTM publicado más reciente (422 si no hay EPS positivo)."""
    if nivel.unidad == "precio":
        return float(nivel.valor)
    if eps_ttm is None or not (eps_ttm > 0):
        raise ValueError(MSG_PE)
    return float(nivel.valor * eps_ttm)


def validar_coherencia(entradas: list[float], salidas: list[float], precio_actual: float) -> None:
    """Entradas por debajo del precio actual y salidas por encima; el mensaje nombra el nivel (ValueError → 422)."""
    for nombre, p in zip(NOMBRES_ENTRADAS, entradas):
        if p >= precio_actual:
            raise ValueError(f"La entrada «{nombre}» ({_fmt(p)}) debe quedar por debajo del precio actual ({_fmt(precio_actual)})")
    for nombre, p in zip(NOMBRES_SALIDAS, salidas):
        if p <= precio_actual:
            raise ValueError(f"La salida «{nombre}» ({_fmt(p)}) debe quedar por encima del precio actual ({_fmt(precio_actual)})")


def _valor_a_fecha(datos: dt.DatosTicker, col: str, fecha: pd.Timestamp) -> float | None:
    """Último valor de `col` publicado con filed ≤ fecha (sin look-ahead); None si falta o es rancio."""
    if datos.ratios is None or col not in datos.ratios:
        return None
    v = cm.ultimo_publicado(np.array([np.datetime64(fecha, "ns")]), datos.ratios, col)[0]
    return _f(v)


def _corte(datos: dt.DatosTicker, fecha_corte) -> pd.Timestamp:
    return pd.Timestamp(fecha_corte) if fecha_corte is not None else datos.fecha_dato


def _percentil_nuevo(historia: pd.Series, valor: float) -> float | None:
    """Percentil del valor dentro de su historia previa MÁS el propio valor (convención de nb04); None si hay < 52 datos."""
    s = pd.concat([historia, pd.Series([valor])], ignore_index=True)
    return _f(cm.percentil_expansivo(s).iloc[-1])


def percentil_historia(datos: dt.DatosTicker, pe: float | None, fecha_corte=None, columna: str = "pe") -> float | None:
    """Percentil del P/E (o del P/E normalizado con columna='pe_norm') frente a la historia propia con fecha ≤ fecha_corte."""
    if datos.multiplos is None or pe is None or not (pe > 0):
        return None
    m = datos.multiplos
    hist = m.loc[m["fecha"] <= _corte(datos, fecha_corte), columna]
    return _percentil_nuevo(hist, pe)


def percentil_industria(datos: dt.DatosTicker, pe: float | None, fecha_corte=None) -> float | None:
    """Percentil del P/E frente al P/E más reciente (fecha ≤ fecha_corte) de las otras empresas de la piloto; None fuera de ella."""
    if not datos.en_piloto or pe is None or not (pe > 0):
        return None
    corte = _corte(datos, fecha_corte)
    pares = []
    for t, m in dt.multiplos_piloto().items():
        if t == datos.ticker:
            continue
        m = m[m["fecha"] <= corte]
        if len(m) and (corte - m["fecha"].iloc[-1]).days <= MAX_DESFASE_PARES and np.isfinite(m["pe"].iloc[-1]):
            pares.append(float(m["pe"].iloc[-1]))
    if len(pares) < 5:
        return None
    return float((sum(p <= pe for p in pares) + 1) / (len(pares) + 1))      # la propia empresa cuenta como ≤ sí misma


def _texto_trampa(p: float) -> str:
    pc = f"{p * 100:.0f} %"
    if p <= QUINTIL:
        return (f"Está entre el 20 % más barato de su propia historia (percentil {pc}). En la industria piloto, las empresas de ese "
                "grupo tuvieron a 3 años una utilidad promedio menor que las del grupo más caro (asociación histórica de la entrega 1; "
                "no anticipa lo que ocurrirá con esta empresa).")
    return (f"Percentil {pc} de su propia historia: queda fuera del 20 % más barato, el grupo en el que la entrega 1 midió la "
            "asociación con una caída posterior de la utilidad promedio.")


def _fundamental(datos, precio, eps, bvps) -> dict:
    out = {"pe_implicito": None, "pb_implicito": None, "percentil_historia": None, "percentil_industria": None}
    if eps and eps > 0:
        out["pe_implicito"] = precio / eps
        out["percentil_historia"] = percentil_historia(datos, out["pe_implicito"])
        out["percentil_industria"] = percentil_industria(datos, out["pe_implicito"])
    if bvps and bvps > 0:
        out["pb_implicito"] = precio / bvps
    return out


def calcular_lecturas(datos: dt.DatosTicker, pedido) -> RespuestaLecturas:
    """Orden: validar, traducir, lectura fundamental, técnica y probabilística; cada bloque falla sin tirar la respuesta."""
    adv = list(datos.advertencias)
    P = datos.precio
    eps = _valor_a_fecha(datos, "eps_ttm", datos.fecha_dato)
    bvps = _valor_a_fecha(datos, "bvps", datos.fecha_dato)
    eps3a = _valor_a_fecha(datos, "eps_prom_3a", datos.fecha_dato)
    p_ent = [a_precio(n, eps) for n in pedido.entradas]
    p_sal = [a_precio(n, eps) for n in pedido.salidas]
    validar_coherencia(p_ent, p_sal, P)
    if eps is None or eps <= 0:
        msg = MSG_PE
        if msg not in adv:
            adv.append(msg)

    niveles: list[LecturaNivel] = []
    for tipo, nombres, precios in (("entrada", NOMBRES_ENTRADAS, p_ent), ("salida", NOMBRES_SALIDAS, p_sal)):
        for nombre, p in zip(nombres, precios):
            fund = {}
            try:
                fund = _fundamental(datos, p, eps, bvps)
            except Exception:
                adv.append(f"No se pudo calcular la lectura fundamental de «{nombre}»")
                fund = {}
            ln = LecturaNivel(tipo=tipo, nombre=nombre, precio=p, pct_vs_actual=p / P - 1, **{k: _f(v) for k, v in fund.items()})
            if tipo == "entrada" and datos.en_piloto:
                try:
                    pn = percentil_historia(datos, p / eps3a if eps3a and eps3a > 0 else None, columna="pe_norm")
                    ln.percentil_pe_norm = pn
                    ln.lectura_trampa = _texto_trampa(pn) if pn is not None else None
                except Exception:
                    adv.append(f"No se pudo calcular el P/E normalizado de «{nombre}»")
            niveles.append(ln)

    suficiente = len(datos.panel) >= cm.SIGMA_VENTANA_D + 1 and np.isfinite(datos.panel["sigma252"].iloc[-1])
    if suficiente:
        _tecnica(datos, niveles[:3], adv)
        _probabilistica(datos, niveles[3:], adv)
    return RespuestaLecturas(ticker=datos.ticker, precio=P, fecha_dato=datos.fecha_dato.date().isoformat(),
                             fuente_datos=datos.fuente_datos, industria_validada=datos.en_piloto,
                             niveles=niveles, advertencias=list(dict.fromkeys(adv)))


def _tecnica(datos, entradas: list[LecturaNivel], adv: list[str]):
    try:
        pipe, meta = md.cargar_modelo()
        fila = datos.panel.iloc[-1]
        sigma = float(fila["sigma252"])
        vars_ = {v: float(fila[v]) for v in cm.VARIABLES if v != "k"}
        lo, hi = float(min(meta["k_grid"])), float(max(meta["k_grid"]))
        for ln in entradas:
            k = cm.k_de_nivel(datos.precio, ln.precio, sigma)
            if not np.isfinite(k):
                continue
            if not (lo <= k <= hi):
                adv.append(f"El nivel «{ln.nombre}» queda fuera del rango entrenado: se evaluó con el nivel más cercano que el modelo conoce")
            k = min(max(k, lo), hi)                       # k de la rejilla más cercano si se sale del rango
            prob = md.prob_toque(pipe, vars_, k)
            ic_lo, ic_hi = md.ic_prob(prob, meta)
            ln.tecnica = Tecnica(prob=prob, ic_lo=ic_lo, ic_hi=ic_hi, linea_base=md.linea_base(sigma, k, meta), k=k)
    except Exception:
        adv.append("No se pudo calcular la lectura técnica")


def _probabilistica(datos, salidas: list[LecturaNivel], adv: list[str]):
    try:
        r_acc = np.log(datos.semanal).diff().dropna()
        r_ref = np.log(datos.sector).diff().dropna()
        sim = cm.simular_salidas(r_acc, r_ref, datos.precio, [ln.precio for ln in salidas], reps=cm.SIM_REPS_RF11)
        if sim["prob"].isna().all():
            adv.append("historia semanal insuficiente para la simulación")
            return
        for ln, (_, f) in zip(salidas, sim.iterrows()):
            ln.probabilistica = Probabilistica(prob=_f(f["prob"]), ic_lo=_f(f["ic_lo"]), ic_hi=_f(f["ic_hi"]),
                                               semanas_mediana=_f(f["semanas_mediana"]))
    except Exception:
        adv.append("No se pudo calcular la lectura probabilística")


# ------------------------------------------------------------------ panel de riesgo (5 cifras)
_nulos: dict[int, float] = {}


def _nulo_caidas(n: int, reps: int = 2000) -> float:
    """Replica `nulo_caidas_fuertes` de nb03 (2000 réplicas, semilla 42); se calcula una vez por n y se guarda.
    Tasa de caídas fuertes que daría la misma receta con retornos normales i.i.d. (nulo calibrado de nb03; σ se estima, no se conoce)."""
    if n not in _nulos:
        rng = np.random.default_rng(cm.SEMILLA)
        _nulos[n] = float(np.mean([cm.tasa_caidas_fuertes(pd.Series(rng.standard_normal(n))) for _ in range(reps)]))
    return _nulos[n]


def calcular_riesgo(datos: dt.DatosTicker) -> dict:
    sem = datos.semanal.dropna()
    r = np.log(sem).diff().dropna()
    sigma = datos.panel["sigma252"].iloc[-1]
    vol = float(sigma * np.sqrt(252)) if np.isfinite(sigma) else None
    obs = esp = None
    if len(r) > cm.VENT_VOL_SEM:
        obs, esp = _f(cm.tasa_caidas_fuertes(r)), _nulo_caidas(len(r))
    r2 = delta = None
    ref = np.log(datos.spy.dropna()).diff().dropna()
    if datos.en_piloto:
        d = cm.dependencia_sector(r, ref, np.log(datos.sector.dropna()).diff().dropna())
        r2, delta = _f(d["r2_mercado_sector"]), _f(d["delta_r2_sector"])
    else:                                         # fuera de la piloto el sector es el SPY: solo R² frente al mercado
        j = pd.concat([r, ref], axis=1, keys=["r", "m"]).dropna()
        r2 = _f(np.corrcoef(j["r"], j["m"])[0, 1] ** 2) if len(j) >= 104 else None
    return {"vol_anual": vol, "p5_semanal": _f(cm.percentil_retorno(r)) if len(r) else None,
            "caida_maxima": _f(cm.max_drawdown(sem)[0]),
            "frec_caidas_fuertes": {"observada": obs, "esperada": _f(esp)},
            "r2_mercado_sector": r2, "delta_r2_sector": delta}
