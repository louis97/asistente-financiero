---
title: "Asistente bursátil para el inversor value colombiano"
subtitle: "Entrega 1 · MINE-4101 Ciencia de Datos Aplicada · Universidad de los Andes"
author: "Louis Gualtero · trabajo individual autorizado por el profesor"
date: "Octubre 2026"
aspectratio: 169
theme: default
colortheme: default
---

## 1. Problema

- **Inversor value colombiano** que compra acciones de EE.UU.: *screener*, fundamentales y gráfico en pantallas separadas; riesgo "a ojo"; sin registro de decisiones.
- Evidencia cualitativa (un participante + autor; muestra no representativa): **2 a 15 cambios de pantalla por activo**, **2 a 3 horas** por reporte trimestral.
- Contexto: Mercado Global Colombiano **+134 %** 2024→2025 (BVC); +87 % inversionistas desde 2023 (SFC).
- KPI: tiempo < 5 min, 1 pantalla, latencia ≤ 1 día, 100 % decisiones registradas.

## 2. Producto: seis niveles, tres lecturas

- **6 niveles** definidos por el usuario (3 de entrada, 3 de salida), en precio y en múltiplo.
- **3 lecturas** por nivel: fundamental (percentiles del P/E normalizado), técnica (SVM, N = 60 días), probabilística (simulación por bloques de la acción y del XLP).
- **Panel de riesgo** descriptivo: volatilidad, percentil 5, caída máxima, caídas fuertes, dependencia del sector.
- **Alcance de la entrega 1**: industria piloto consumo defensivo (21 empresas + SPY + XLP; KHC excluida).

## 3. Mockup

![](assets/mockup.png){width=78%}

Validación con el stakeholder: **pendiente** (sesión 2026-10-16).

## 4. Ética y regulación

- **Ley 964 de 2005 y Decreto 2555 de 2010**: el producto no recomienda compra ni venta y no perfila al usuario; leyenda del art. 2.40.1.1.3 en cada pantalla.
- **Habeas Data (Ley 1581 de 2012)**: anonimización del participante y autorización verificable.
- **Transparencia**: SVM lineal con coeficientes legibles; probabilidad junto a su línea base y su desempeño histórico.
- **Sin look-ahead ni data snooping**: fecha `filed`, ventana expansiva, 15 pruebas declaradas antes, Bonferroni en P4.

## 5. Enfoque analítico (6 preguntas, 1 hipótesis cada una)

| Preg. | Qué pregunta | Umbral |
|---|---|---|
| P1 | ¿Caídas semanales > 2σ más frecuentes que una normal? | 3,8 % |
| P2 | ¿Barato > caro a 3 años en Δlog(P/E normalizado)? | +0,03 anualizado |
| P3 | ¿Barato gana al XLP a 3 años? | +0,05 anualizado |
| P4 | ¿Algún indicador técnico mejora la AUC base? | +0,01 (×7) |
| P5 | ¿XLP agrega ΔR² al SPY? | +0,05 |
| P6 | ¿La turbulencia se agrupa? | 0,30 |

Plantilla: umbral → H0/H1 → prueba y supuestos → IC95 por bootstrap → decisión estadística y de negocio.

## 6. Datos (tres fuentes gratuitas, instantánea fechada)

- **yfinance**: 21 344 filas semanales × 23 tickers desde 2009; precios ajustados y sin ajustar por dividendos.
- **SEC EDGAR**: hechos XBRL de los 10-K y 10-Q con fecha `filed`; el P/E usa el EPS TTM reconstruido con los 10-Q.
- **Damodaran**: múltiplos y márgenes por industria.
- Calidad en nb02: 9 dimensiones y 5 niveles; 0 nulos en precios ajustados, 0 duplicados; TTM válido en 1.308 de 1.434 trimestres (91,2 %).

## 7. EDA: resultados por hipótesis

| Preg. | Estimado · IC95 · Decisión |
|---|---|
| P1 | 3,08 % · [2,46; 3,92] % · **no se rechaza H0**, no accionable |
| P2 | +0,153 · [+0,091; +0,221] · **se rechaza H0**, accionable |
| P3 | +0,006 · [−0,032; +0,049] · **no se rechaza H0**, no accionable |
| P4 | 7 indicadores con IC que cruzan 0 · **no se rechaza H0** (×7) |
| P5 | ΔR² 0,225 · [+0,175; +0,291] · **se rechaza H0**, accionable (confirmatoria) |
| P6 d. | P(T\|T) 0,305 · [0,275; 0,340] · **se rechaza H0**, magnitud incierta |

## 8. P2: barato sube más, descomposición compatible con trampa de valor

![](assets/nb04_p2_descomposicion.png){width=70%}

Barato − caro: **+0,153 anualizado en log** (IC95 por empresa [+0,091; +0,221]). Precio aporta +0,15 (IC excluye 0); EPS promedio −0,15 (IC cruza 0). nb04 §2.7–§2.8.

## 9. P4: ningún indicador supera la línea base por decil de σ

![](assets/nb04_p4_zonas.png){width=65%}

7 IC95 (Bonferroni ≈ 99,3 %) cruzan 0; AUC base **0,591** con N = 60. Consecuencia: `variables_svm = {|r_t|, σ20/σ252, σ252}`. nb04 §5.3.

## 10. Conclusiones y próximos pasos

- **Insights**: niveles en k·σ252, N = 60; simulación por bloques de la acción + XLP; exceso sobre XLP **no entra como señal**; marca "industria no validada" fuera del piloto.
- **Limitaciones**: una industria piloto; supervivencia; 3 años (no 5–10); P5 confirmatoria; fuga de selección en P4.
- **Próximos pasos**: entrenar el SVM con corte cronológico, simulación por bloques, validación con el stakeholder, segunda industria.
- Repositorio: <https://github.com/louis97/asistente-financiero>. Video: pendiente de subir.
