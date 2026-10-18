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
  - \setlength{\parskip}{1pt}
  - \usepackage{array}
  - \usepackage{tabularx}
  - \usepackage{titling}
  - \setlength{\droptitle}{-4em}
  - \usepackage{float}
  - \usepackage{caption}
  - \captionsetup[figure]{font=footnotesize,labelfont=bf,justification=justified}
  - \floatplacement{figure}{H}
---

**Repositorio:** <https://github.com/louis97/asistente-financiero> · **Rama de entrega:** `main` tras la fusión del 18 de octubre · **Video:** pendiente de subir · **Trabajo individual autorizado por el profesor.**

*Convención. Las referencias del tipo "nb04 §2.7" remiten al notebook 04, sección 2.7, del repositorio.*

## 1. Problema y entendimiento del negocio

El inversor value colombiano que compra acciones de EE.UU. (una acción es una fracción del capital de una empresa; "value" significa que paga poco por cada dólar de utilidad) actúa hoy como enrutador manual de datos: usa un *screener* para filtrar empresas, otra pantalla para los fundamentales (ratios como el P/E, precio sobre utilidad por acción) y otra para la gráfica, y no anota sus decisiones. La evidencia cualitativa (entrevista y formulario con un participante, más el autor; muestra no representativa) reporta **2 a 15 cambios de pantalla por activo** y **2 a 3 horas** para reprocesar el análisis tras cada reporte trimestral, y el riesgo se mide "a ojo". El contexto crece: el volumen del Mercado Global Colombiano pasó de \$1,60 a \$3,75 billones de 2024 a 2025 (+134 %, BVC 2026) y la SFC reporta un aumento de 87 % en inversionistas desde 2023. **El alcance de la entrega 1 es una industria piloto, consumo defensivo**, con 21 empresas del XLP (el ETF sectorial, un fondo que cotiza como una acción y agrupa a las empresas del sector) con historia desde 2009, más el SPY (ETF del mercado) y el XLP. KHC queda fuera porque sus precios empiezan en 2015. Los KPI del producto son tiempo por activo menor que 5 minutos, un cambio de pantalla, latencia tras un reporte de un día o menos y 100 % de decisiones documentadas; la línea base definitiva sale de la sesión con el inversor (pendiente al 2026-10-16).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/01_negocio.md>

## 2. Ideación y mockup

El producto entrega, para cada ticker, **seis niveles definidos por el usuario** (tres de entrada y tres de salida), en precio y en múltiplo. Cada nivel trae tres lecturas: **fundamental** (percentil histórico y de la industria del P/E, del P/E normalizado y de los ratios de calidad; el percentil responde "entre los valores pasados, ¿en qué puesto queda el de hoy?"), **técnica** por SVM lineal con horizonte de 60 días hábiles frente a su línea base por decil de volatilidad (solo entradas) y **probabilística** por simulación que remuestrea bloques de semanas de la acción y del XLP a la vez (solo salidas). Un panel de riesgo descriptivo muestra cinco cifras: volatilidad anualizada (σ, dispersión típica del retorno), percentil 5 semanal, caída máxima histórica, frecuencia de caídas fuertes y dependencia del sector. Los niveles por múltiplo se recalculan cuando la SEC publica un reporte nuevo; para tickers fuera del piloto, el panel se marca "industria no validada" y las probabilidades llevan advertencia. La **validación con el stakeholder está pendiente**: la sesión está programada para el 2026-10-16.

![Mockup del dashboard (valores ilustrativos). La columna "Técnica (SVM, solo entradas)" muestra la probabilidad de tocar cada nivel en 60 días hábiles (21 %, 42 % y 71 %) frente a la línea base por decil de volatilidad diaria (16 %, 35 % y 66 %). La "Probabilística (solo salidas)" muestra la probabilidad de alcanzar cada salida en el horizonte por simulación con retornos históricos (81 %, 62 % y 37 %). El panel de riesgo trae las cinco cifras descriptivas y el recuadro "Desempeño histórico del modelo técnico (SVM)" aparece marcado "se calcula en la entrega 2".](assets/mockup.png){width=75%}

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/02_ideacion.md>

## 3. Aspectos éticos y legales

Tres riesgos quedan altos tras mitigar. **Regulación de la asesoría** (Ley 964 de 2005 y Decreto 2555 de 2010): la asesoría de inversión está reservada a entidades vigiladas por la SFC, y el producto evita entrar a ese perímetro porque no recomienda compra ni venta, no perfila al usuario y lleva en cada pantalla la leyenda del artículo 2.40.1.1.3. **Transparencia y explicabilidad** del score: se usa un SVM lineal con coeficientes legibles, la probabilidad siempre aparece junto a su línea base y a su desempeño histórico, y se publica la lista explícita de técnicas no cubiertas en clase. **Look-ahead y data snooping** (que el análisis vea datos del futuro, o que se pruebe de todo hasta encontrar algo): se usa la fecha `filed` (día en que la SEC publica el reporte), una ventana expansiva (solo datos hasta t) y 15 pruebas declaradas antes de ejecutar (Bonferroni en P4 y Holm como sensibilidad). También se cuida la anonimización del participante (Ley 1581 de 2012), los términos de uso de yfinance, SEC EDGAR y Damodaran, el sesgo de supervivencia de 21 emisores vigentes y la marca "industria no validada" fuera del piloto. **Técnicas no cubiertas en clase (15 en total):** bootstrap por bloques de fechas, nulo calibrado por simulación, ΔAUC con regresión logística, errores estándar agrupados por empresa, Brier y calibración, análisis de potencia (MDE), EPS TTM (utilidad por acción de los últimos 12 meses) a partir de 10-Q, SVM, simulación por bloques, Bonferroni, Holm, VIF, prueba F de modelos anidados, Mann-Whitney y clustermap; el detalle con la justificación de cada técnica está en el documento enlazado abajo.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/03_etica_legal.md>

## 4. Enfoque analítico

El trabajo responde a **seis preguntas de negocio con una hipótesis cada una**. Cada hipótesis sigue la misma secuencia: umbral práctico fijado antes, H0/H1 y α = 0,05, prueba con su matriz de supuestos, estimación con intervalo de confianza al 95 % (IC95: rango en el que cae el estimado el 95 % de las veces si se repitiera el experimento, construido por bootstrap, un remuestreo que no supone una forma teórica), y dos decisiones. La **estadística** es "se rechaza H0" si el IC95 no incluye el valor nulo y "no se rechaza H0" si lo incluye. La **de negocio** es "accionable" si el límite inferior del IC95 supera el umbral, "efecto real, magnitud incierta" si se rechaza H0 pero el IC95 cruza el umbral, y "no accionable" en los demás casos. Lenguaje de asociación, nunca de causa.

La tabla reúne cada pregunta con lo que **decide en la herramienta** —qué pieza del producto depende de la respuesta—, el umbral, el estimado con IC95 y las dos decisiones. Un umbral de 0,03 anualizado en log equivale a cerca de 9 % acumulado en tres años.

\begin{tabularx}{\linewidth}{@{}p{0.5cm} X X p{1.6cm} X p{2.0cm}@{}}
\hline
\textbf{P.} & \textbf{Pregunta} & \textbf{Decide en la herramienta} & \textbf{Umbral} & \textbf{Estimado · IC95} & \textbf{Decisión} \\
\hline
P1 & ¿Caídas semanales fuertes más que una normal igual? & Panel de riesgo: frec.\ de caídas fuertes. & 3,83 \% sem. & 3,08 \% · [2,46; 3,92] \% & no rechaza · no acc. \\
P2 & ¿El quintil barato sube su P/E norm.\ más que el caro a 3 años? & Lectura fundam.\ de entradas: percentil del P/E norm. & +0,03 anual.\ log & +0,153 · [+0,091; +0,221] & rechaza · acc. \\
P3 & ¿El quintil barato gana al XLP a 3 años? & Exceso sobre XLP no entra como señal. & +0,05 anual.\ log & +0,006 · [−0,032; +0,049] & no rechaza · no acc. \\
P4 & ¿Algún indicador técnico mejora la AUC base? & Lectura técnica: SVM solo con variables de magnitud. & +0,01 ΔAUC (×7) & 7 IC95 cruzan 0; mom\_12\_1 −0,018 · [−0,055; +0,019] & no rechaza (×7) · no acc. \\
P5 & ¿XLP agrega ΔR² al SPY semanal? & Panel de riesgo (dep.\ del sector) y simulación acción + XLP. & +0,05 ΔR² & 0,225 · [+0,175; +0,291] & rechaza · acc.\ (confirm.) \\
P6 & ¿La turbulencia se agrupa? & Lectura probabilística: simulación por bloques de semanas. & 0,30 & P(T\textbar T) diaria 0,305 · [0,275; 0,340] & rechaza · magnitud incierta \\
\hline
\end{tabularx}

La lectura de P2 incluye una **advertencia descriptiva de posible deterioro de utilidades** (compatible con trampa de valor); los niveles de P6 se expresan en **k · σ252 diaria** (volatilidad del último año); y P5 justifica analizar una industria a la vez.

**P1 en palabras simples.** Una caída fuerte es una semana en que la acción cae más de 2 veces su volatilidad semanal típica del último año (`z < −2`, donde `z` es el retorno sobre su σ reciente). Si los retornos siguieran una distribución normal (campana de Gauss) con esa volatilidad conocida, pasaría en el 2,3 % de las semanas; como la volatilidad se estima con el pasado y no se conoce, la tasa comparable, calibrada por simulación con la misma receta, es ≈ 2,55 %. P1 pregunta si en consumo defensivo pasa más que eso: si no, el panel no infla la "frecuencia de caídas fuertes" artificialmente.

**P/E normalizado en palabras simples.** El P/E es precio sobre utilidad por acción (EPS). El P/E normalizado es precio dividido por el **EPS promedio de los últimos 3 años** (utilidad neta de los 12 trimestres ya publicados ÷ 3 ÷ acciones). Promediar 3 años evita que un solo año excepcional —malo o bueno— haga parecer barata o cara una acción. "Barata frente a su historia" se opera como el quintil con el P/E normalizado más bajo de la industria en esa fecha.

**Diseño experimental.** La **etiqueta** vale 1 si el precio toca, dentro de los próximos **N = 60 días hábiles**, un nivel ubicado a **`k = 1` volatilidad diaria por √N por debajo** del precio actual (el nivel superior es simétrico hacia arriba; vale 0 si primero toca el superior o se agota el tiempo). Toda variable en `t` usa solo datos ≤ `t` (ventana expansiva, `shift(1)` y fecha `filed`); los percentiles del P/E normalizado son expansivos. En P2 y P3 se toma una observación por empresa y trimestre calendario, y las ventanas de 3 años sin resultado completo se excluyen (censura).

**Validación cronológica.** Entrenamiento y prueba se separan con un **corte cronológico en 2018-12-31** —ajuste 2009-2018, prueba 2019+— con un **espacio de al menos N = 60 días hábiles** entre ambos para que ninguna etiqueta del entrenamiento mire a la prueba. La estabilidad se verifica por **subperíodos** (2009-2012, 2013-2019, 2020-2021 y 2022+). La **línea base** es la tasa de toque por decil de volatilidad del último año (σ252): se parten los días del entrenamiento en 10 grupos por σ252 y la predicción para un día nuevo es la tasa de su grupo; da **AUC 0,591 en la prueba** (nb04 §4.5).

**Métricas y qué queda para la entrega 2.** Las métricas del SVM son AUC (probabilidad de ordenar correctamente un día que sí tocó frente a otro que no; 0,5 es azar), Brier (error cuadrático medio entre la probabilidad predicha y la realidad; menor es mejor) y calibración (si el modelo dice 30 %, ¿pasa cerca del 30 % de las veces?), por subperíodo. **La entrega 1 deja listas** la etiqueta, la línea base y la selección de variables (P4); **el SVM y su desempeño se calculan en la entrega 2**.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/04_enfoque_analitico.md>

## 5. Recolección y diccionario de datos

Tres fuentes gratuitas alimentan el análisis, guardadas como instantáneas fechadas en `data/snapshots/`. De **yfinance** se descargan los precios semanales y diarios desde 2009-01 (21 344 filas semanales × 23 tickers; con y sin ajuste por dividendos, para separar el retorno total del múltiplo que vio el inversor). De **SEC EDGAR** se extraen los hechos XBRL de los 10-K (anual) y 10-Q (trimestral) con la fecha `filed`. De **Damodaran** se toman los múltiplos y márgenes por industria como contexto. El **P/E usa el EPS TTM**, construido a partir de los 10-Q y los 10-K: la autoridad publica cifras acumuladas (semestral y de nueve meses) y el cuarto trimestre se infiere del anual; el pipeline lo reconstruye y lo actualiza con cada publicación nueva, controlando la escala XBRL y las acciones implícitas (nb01 §4 y nb02 §2b). El universo son 21 empresas más el SPY y el XLP; KHC queda fuera por su historia desde 2015. La **cobertura TTM** es de 1.308 trimestres válidos sobre 1.434 (91,2 %); STZ queda fuera por falta de `acciones` y HSY solo tiene datos hasta 2015. En calidad, los precios semanales ajustados cierran con **0 nulos y 0 duplicados**; los saltos mayores que 5σ corresponden a movimientos reales (nb02 §3). Las 9 dimensiones de calidad (completitud, consistencia, conformidad, relevancia, precisión, procesabilidad, disponibilidad, temporalidad, credibilidad) y los 5 niveles (atributo, registro, columna, tabla, varias tablas) se auditan en nb02, y cada decisión lleva una línea de justificación.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/05_diccionario_datos.md> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/01_recoleccion.ipynb> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/02_calidad.ipynb>

## 6. Entendimiento de los datos (EDA)

El EDA combina las cuatro vistas (univariada y multivariada, cada una gráfica y no gráfica): descriptivos robustos, histogramas con KDE, QQ-plot, volatilidad móvil, caída máxima, chi-cuadrado con V de Cramér, Spearman, VIF (mide colinealidad), PCA, prueba F de modelos anidados y clustermap. Cada prueba lleva su matriz de supuestos (supuesto → por qué importa → verificación → resultado → qué se hace si falla); con observaciones dependientes la decisión sale del IC95 por bootstrap, no del p-value clásico. Los resultados por hipótesis están en la tabla de la sección 4 y salen de `data/resultados/nb03.json`, `nb04.json` y `nb04_p4.json`.

\begin{figure}[H]
\centering
\begin{minipage}[t]{0.48\textwidth}
\centering
\includegraphics[width=\linewidth]{assets/nb04_p2_descomposicion.png}
\captionof*{figure}{\footnotesize \textbf{Figura 2. P2:} Δlog(P/E normalizado) a 3 años por quintil. El quintil \textbf{barato (Q1)} sube su múltiplo con \textbf{+0,153 anualizada en log} frente al \textbf{caro (Q5)}; IC95 por empresa [+0,091; +0,221]. \textbf{Compatible con trampa de valor, no la afirma}: precio +0,15 (IC95 excluye 0) y EPS promedio −0,15 (IC95 cruza 0). nb04 §2.7--§2.8.}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\centering
\includegraphics[width=\linewidth]{assets/nb04_p4_zonas.png}
\captionof*{figure}{\footnotesize \textbf{Figura 3. P4:} ΔAUC por indicador técnico sobre la línea base por decil de σ252. Los siete IC95 bilaterales (Bonferroni ≈ 99,3 \%) cruzan 0; mayor en valor absoluto \texttt{mom\_12\_1} (ΔAUC −0,018, IC [−0,055; +0,019]) y más estrecho \texttt{vol\_rel20} (ΔAUC −0,001, IC [−0,011; +0,010]). Línea base \textbf{AUC 0,591} con N = 60. \texttt{variables\_svm = \{|r\_t|, σ20/σ252, σ252\}} (solo magnitud). nb04 §5.3.}
\end{minipage}
\end{figure}

**Dos lecturas requieren contexto.** En **P2**, la descomposición compatible con trampa de valor no se afirma porque el IC95 del EPS cruza 0. En **P4**, los siete indicadores técnicos no mejoran la AUC sobre la línea base por decil de σ, por eso las variables del SVM quedan solo de magnitud. Como control de multiplicidad, Holm al 0,05 sobre las 13 pruebas con decisión de negocio deja rechazando a las cuatro que ya rechazaban (P2, P5, P6 diaria y P6 semanal); ninguna decisión cambia (nb04 §8).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/notebooks/03_eda_univariado.ipynb> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/04_eda_multivariado.ipynb>

## 7. Conclusiones iniciales e insights

**Hallazgos (asociaciones, no causas).** En consumo defensivo las caídas semanales fuertes no son más frecuentes que las que daría una normal medida igual (P1); el quintil barato por P/E normalizado sube más su múltiplo que el caro a 3 años, con una descomposición compatible con trampa de valor (P2); el quintil barato no gana al XLP a 3 años (P3); ningún indicador técnico mejora la AUC sobre la línea base por decil de σ (P4); el XLP agrega ΔR² mediano 0,225 al SPY (P5, confirmatoria); y la turbulencia se agrupa, aunque su magnitud es incierta (P6). **Insights para el diseño.** La lectura fundamental del nivel "barata frente a su historia" muestra el percentil del P/E normalizado como lectura principal, con advertencia descriptiva de posible deterioro de utilidades; el exceso sobre el XLP no entra como señal, solo como contexto; los niveles se miden en k · σ252 diaria con etiqueta a N = 60 días hábiles; la simulación remuestrea bloques de semanas de la acción y del XLP al mismo tiempo; las variables del SVM son `{|r_t|, σ20/σ252, σ252}` (solo magnitud), evaluadas contra la línea base AUC 0,591. **Limitaciones:** una sola industria piloto (21 empresas); sesgo de supervivencia (pesa más a 3 años); historia desde 2009 (P/E normalizado a 3 años, no 5-10); EPS TTM con 91,2 % de cobertura; ventanas de 3 años solapadas intra-empresa (de ahí el IC por empresa); P5 confirmatoria; P4 con fuga de selección, mitigada en la entrega 2. **Acciones próximas:** entrenar el SVM con corte cronológico, implementar la simulación por bloques, validar con el inversor y registrar los KPI, y replicar el pipeline en una segunda industria. Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/07_conclusiones.md>
