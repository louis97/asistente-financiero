---
title: "Asistente bursátil para el inversor value colombiano — Entrega 1"
author: "Louis Gualtero · MINE-4101 Ciencia de Datos Aplicada · Universidad de los Andes"
papersize: letter
mainfont: Arial
monofont: Arial
fontsize: 12pt
geometry: margin=1.8cm
lang: es
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - \usepackage{enumitem}
  - \setlist{nosep}
  - \setlength{\parskip}{2pt}
---

**Repositorio:** <https://github.com/louis97/asistente-financiero> · **Rama de entrega:** `main` tras la fusión del 18 de octubre · **Video:** pendiente de subir · **Trabajo individual autorizado por el profesor.**

## 1. Problema y entendimiento del negocio

El inversor value colombiano que compra acciones de EE.UU. actúa hoy como enrutador manual de datos: usa un *screener*, otra pantalla para fundamentales y otra para el gráfico, y no tiene dónde anotar sus decisiones. La evidencia cualitativa (entrevista + formulario con un participante más el autor; muestra no representativa) reporta **2 a 15 cambios de pantalla por activo** y **2 a 3 horas** para reprocesar el análisis tras cada reporte trimestral; el riesgo se mide "a ojo". El contexto crece: el volumen del Mercado Global Colombiano pasó de \$1,60 a \$3,75 billones de 2024 a 2025 (+134 %, BVC 2026) y la SFC reporta un aumento de 87 % en inversionistas desde 2023. **Alcance de la entrega 1 (industria piloto): consumo defensivo**, con 21 empresas del XLP con historia desde 2009 más el SPY (mercado) y el XLP (sector); KHC queda fuera por empezar en 2015. Los KPI del producto son tiempo por activo < 5 min, 1 cambio de pantalla, latencia tras reporte ≤ 1 día y 100 % de decisiones documentadas; la línea base definitiva sale de la sesión con el inversor (pendiente al 2026-10-16).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/01_negocio.md>

## 2. Ideación y mockup

El producto entrega, para cada ticker, **seis niveles definidos por el usuario** (tres de entrada y tres de salida), cada uno en precio y en múltiplo, con tres lecturas: fundamental (percentil propio y de la industria del P/E, del P/E normalizado y de los ratios de calidad), técnica (probabilidad de un SVM lineal frente a la línea base por decil de volatilidad, con N = 60 días hábiles) y probabilística (simulación por remuestreo de bloques de semanas de la acción y del XLP al mismo tiempo). Un panel de riesgo descriptivo muestra cinco cifras directas (volatilidad anualizada, percentil 5 semanal, caída máxima, frecuencia de caídas fuertes y dependencia del sector). Los niveles por múltiplo se recalculan cuando la SEC publica un nuevo reporte. Para tickers fuera del piloto, el panel se marca "industria no validada" y las probabilidades llevan advertencia. La **validación con el stakeholder está pendiente** (sesión programada para el 2026-10-16, sin resultados que reportar).

![Mockup del dashboard (valores ilustrativos). La columna "Técnica (SVM, solo entradas)" muestra probabilidades de tocar el nivel en 60 días hábiles de 21 %, 42 % y 71 % frente a su línea base por decil de volatilidad diaria de 16 %, 35 % y 66 %. La columna "Probabilística (solo salidas)" muestra la probabilidad de alcanzar cada nivel de salida en el horizonte (3 años) por simulación con retornos históricos: 81 %, 62 % y 37 %. El panel de riesgo trae 5 cifras descriptivas (volatilidad, peor semana típica, frecuencia de caídas fuertes, caída máxima y dependencia del sector). El recuadro "Desempeño histórico del modelo técnico (SVM)" aparece marcado "se calcula en la entrega 2".](assets/mockup.png){width=100%}

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/02_ideacion.md>

## 3. Aspectos éticos y legales

Los tres riesgos altos: **regulación de la asesoría** (Ley 964 de 2005 y Decreto 2555 de 2010): el producto no recomienda compra ni venta, no perfila al usuario y lleva en cada pantalla la leyenda del art. 2.40.1.1.3. **Transparencia**: SVM lineal con coeficientes legibles, probabilidad siempre junto a su línea base y su desempeño histórico, lista explícita de técnicas no cubiertas en clase. **Look-ahead y data snooping**: fecha `filed` de los reportes, ventana expansiva, corte cronológico con espacio y 15 pruebas declaradas antes de ejecutar (Bonferroni en P4, Holm como sensibilidad). También: anonimización del participante (Ley 1581 de 2012), términos de yfinance, SEC EDGAR y Damodaran, sesgo de supervivencia de 21 emisores vigentes y marca "industria no validada" fuera del piloto. **Técnicas no cubiertas en clase (15 en total)**: bootstrap por bloques de fechas, nulo calibrado por simulación, ΔAUC con regresión logística, errores estándar agrupados por empresa, Brier y calibración, análisis de potencia (MDE), EPS TTM a partir de 10-Q, SVM, simulación por bloques, Bonferroni, Holm, VIF, prueba F de modelos anidados, Mann-Whitney y clustermap; detalle y justificación en 03_etica_legal.md §3.3 (fuente única).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/03_etica_legal.md>

## 4. Enfoque analítico

Seis preguntas de negocio con **una hipótesis cada una** y la plantilla de inferencia (umbral práctico fijado antes → H0/H1 y α = 0,05 → prueba con sus supuestos verificados → estimación con IC95 por bootstrap antes del p-value → efecto con IC → decisión estadística ["se rechaza H0" o "no se rechaza H0"] y decisión de negocio [accionable si el límite inferior del IC supera el umbral]).

| Preg. | Qué pregunta | Prueba y variable | Umbral |
|---|---|---|---|
| P1 | ¿Las caídas semanales > 2σ pasan más de lo que diría una normal? | Tasa semanal con `z < −2`; IC por bloques de fechas | 1,5 × nulo ≈ 3,8 % |
| P2 | ¿Las acciones baratas suben su P/E normalizado más que las caras a 3 años? | Δlog(P/E normalizado), quintil barato − caro por fecha; IC por empresa | +0,03 anualizado en log |
| P3 | ¿El quintil barato gana al XLP a 3 años? | Exceso sobre XLP; IC por empresa | +0,05 anualizado en log |
| P4 | ¿Algún indicador técnico mejora la AUC sobre la línea base por decil de σ? | ΔAUC regresión logística (7 indicadores); IC por bloques, Bonferroni al ≈ 99,3 % | +0,01 |
| P5 | ¿El XLP agrega poder explicativo al SPY (semanal)? | ΔR² del modelo anidado por empresa; IC por empresa | +0,05 |
| P6 | ¿La turbulencia se agrupa? | P(T\|T) diaria y semanal; IC por bloques; dos controles de dirección | 0,30 |

**Diseño experimental.** Etiqueta de entrada diaria "toca el nivel a k·σ252 en N días hábiles" (N elegido con el entrenamiento); todas las variables en t usan datos ≤ t (ventana expansiva, `shift(1)`, fecha `filed`); el P/E normaliza con el promedio de 12 trimestres publicados; una observación por empresa y trimestre calendario; las ventanas de 3 años sin resultado completo se excluyen. **Métricas del modelo (lecturas técnica y probabilística)**: AUC, Brier y calibración frente a la línea base por decil de σ252 diaria, por subperíodo.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/04_enfoque_analitico.md>

## 5. Recolección y diccionario de datos

Tres fuentes gratuitas con instantáneas fechadas en `data/snapshots/`: **yfinance** (precios semanales y diarios desde 2009-01, 21 344 filas semanales × 23 tickers; precios con y sin ajuste por dividendos), **SEC EDGAR** (hechos XBRL de los 10-K y 10-Q con fecha `filed`) y **Damodaran** (múltiplos y márgenes por industria). El **P/E usa el EPS de los últimos 12 meses (TTM) construido con los 10-Q y los 10-K**: el proveedor publica cifras acumuladas (semestral, 9 meses) y Q4 se infiere del anual; el pipeline lo reconstruye y lo actualiza con cada reporte nuevo, controlando la escala XBRL y las acciones implícitas (nb01 §4 y nb02 §2b). Universo del piloto: 21 empresas + SPY + XLP; KHC excluida (datos desde 2015). Cobertura TTM: 1.308 trimestres válidos sobre 1.434 (91,2 %); STZ queda fuera por falta de `acciones` y HSY solo hasta 2015. **Calidad**: 0 nulos en los precios semanales ajustados y 0 duplicados; los saltos > 5σ corresponden a movimientos reales (nb02 §3). Las 9 dimensiones de calidad (completitud, consistencia, conformidad, relevancia, precisión, procesabilidad, disponibilidad, temporalidad, credibilidad) y los 5 niveles (atributo, registro, columna, tabla, varias tablas) se auditan en nb02; cada decisión lleva una línea "Justificación:".

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/05_diccionario_datos.md> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/01_recoleccion.ipynb> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/02_calidad.ipynb>

## 6. Entendimiento de los datos (EDA)

Las técnicas de EDA aplicadas en sus cuatro combinaciones (univariada × multivariada × gráfica × no gráfica): descriptivos robustos, histogramas con KDE, QQ-plot, volatilidad móvil, caída máxima, chi-cuadrado con V de Cramér, Spearman, VIF, PCA, prueba F de modelos anidados y clustermap. Cada prueba lleva su matriz de supuestos (supuesto → por qué importa → verificación ejecutada → resultado → qué se hace si falla); con observaciones dependientes la decisión sale del IC por bootstrap (por bloques de fechas o por empresa). Resultado por hipótesis (cifras de `data/resultados/nb03.json`, `nb04.json` y `nb04_p4.json`):

| Preg. | Estimado | IC95 | Umbral | Decisión estadística | Decisión de negocio |
|---|---|---|---|---|---|
| P1 | 3,08 % semanal | [2,46 %; 3,92 %] | 3,83 % | no se rechaza H0 | no accionable |
| P2 | +0,153 anualizado en log | [+0,091; +0,221] | +0,03 | se rechaza H0 | accionable |
| P3 | +0,006 anualizado en log | [−0,032; +0,049] | +0,05 | no se rechaza H0 | no accionable |
| P4 | ΔAUC de −0,018 a +0,004 (7 ind.) | todos cruzan 0 | +0,01 | no se rechaza H0 (×7) | no accionable (×7) |
| P5 | ΔR² mediano 0,225 | [+0,175; +0,291] | +0,05 | se rechaza H0 | accionable (confirmatoria) |
| P6 diaria | P(T\|T) = 0,305 | [0,275; 0,340] | 0,30 | se rechaza H0 | efecto real, pero magnitud incierta |

![P2: Δlog(P/E normalizado) a 3 años por quintil del P/E normalizado. El quintil **barato (Q1)** sube su múltiplo con una diferencia **+0,153 anualizada en log** frente al **caro (Q5)**; IC95 por empresa [+0,091; +0,221] excluye el nulo y supera el umbral de 0,03. Lectura de **trampa de valor compatible, no afirmada**: en la descomposición, el precio aporta +0,15 (IC95 excluye 0) y el EPS promedio −0,15 (IC95 cruza 0). nb04 §2.7–§2.8.](assets/nb04_p2_descomposicion.png){width=60%}

![P4: ΔAUC por indicador técnico sobre la línea base por decil de σ252. Los 7 IC95 bilaterales (Bonferroni al ≈ 99,3 %) cruzan 0; el más fuerte en valor absoluto es `mom_12_1` (ΔAUC −0,018, IC [−0,055; +0,019]) y el más estrecho es `vol_rel20` (ΔAUC −0,001, IC [−0,011; +0,010]). La línea base da **AUC 0,591** en la prueba con N = 60. Consecuencia: `variables_svm = {|r_t|, σ20/σ252, σ252}` (solo magnitud). nb04 §5.3.](assets/nb04_p4_zonas.png){width=60%}

**Multiplicidad**. Holm al 0,05 sobre las 13 pruebas con decisión de negocio deja rechazando a las 4 que ya rechazaban (P2, P5, P6 diaria, P6 semanal); ninguna decisión cambia (nb04 §8).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/notebooks/03_eda_univariado.ipynb> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/04_eda_multivariado.ipynb>

## 7. Conclusiones iniciales e insights

**Hallazgos (asociaciones, no causas).** (1) En consumo defensivo, las caídas semanales fuertes no son más frecuentes que las que daría una normal medida igual (P1); (2) el quintil barato por P/E normalizado sube más su múltiplo que el caro a 3 años; la descomposición es **compatible con trampa de valor**, no la afirma (P2); (3) el quintil barato **no gana al XLP** a 3 años (P3); (4) **ningún indicador técnico mejora la AUC** sobre la línea base por decil de σ (P4); (5) el XLP agrega ΔR² mediano 0,225 al SPY (P5, confirmatoria: la industria se eligió viendo este ΔR²); (6) la turbulencia se agrupa, pero su magnitud es incierta (P6).

**Insights para el diseño.** La lectura fundamental del nivel "barata frente a su historia" muestra el percentil del P/E normalizado con la advertencia de posible deterioro; el exceso sobre el XLP **no entra como señal**; los niveles se miden en k·σ252 diaria y la etiqueta usa **N = 60 días hábiles**; la simulación remuestrea **bloques de semanas** de la acción y del XLP al mismo tiempo; `variables_svm = {|r_t|, σ20/σ252, σ252}` (solo magnitud), evaluadas contra la línea base **AUC 0,591**.

**Limitaciones (honestas y cuantificadas).** Industria piloto única (21 empresas); sesgo de supervivencia; historia desde 2009 limita el P/E normalizado a 3 años (no 5–10); EPS TTM con 91,2 % de cobertura; ventanas de 3 años solapadas intra-empresa (de ahí el IC por empresa); P5 confirmatoria; fuga de selección en P4 (mitigada evaluando el SVM en un tramo posterior). **Acciones próximas**: entrenar el SVM con corte cronológico; implementar la simulación por bloques; validar con el stakeholder y registrar los KPI; replicar el pipeline en una segunda industria.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/07_conclusiones.md>
