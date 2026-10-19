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

**Repositorio:** <https://github.com/louis97/asistente-financiero> · **Rama de entrega:** `main` tras la fusión del 18 de octubre · **Video:** <https://youtu.be/NGZdh3TD46E> · **Trabajo individual autorizado por el profesor.**

*Convención. Las referencias del tipo "nb04 §2.7" remiten al notebook 04, sección 2.7, del repositorio.*

## 1. Problema y entendimiento del negocio

El inversor value colombiano que compra acciones de EE.UU. (una acción es una fracción del capital de una empresa; "value" significa que paga poco por cada dólar de utilidad) actúa hoy como enrutador manual de datos: usa un *screener* para filtrar empresas, otra pantalla para los fundamentales (ratios como el P/E, precio sobre utilidad por acción) y otra para la gráfica, y no anota sus decisiones. La evidencia cualitativa (entrevista y formulario con un participante, más el autor; muestra no representativa) reporta **2 a 15 cambios de pantalla por activo** y **2 a 3 horas** para reprocesar el análisis tras cada reporte trimestral, y el riesgo se mide "a ojo". El contexto crece: el volumen del Mercado Global Colombiano pasó de \$1,60 a \$3,75 billones de 2024 a 2025 (+134 %, BVC 2026) y la SFC reporta un aumento de 87 % en inversionistas desde 2023. **El alcance de la entrega 1 es una industria piloto, consumo defensivo** (alimentos, bebidas, aseo personal y del hogar, y tabaco: bienes que se compran en cualquier fase del ciclo), con 21 empresas del XLP (el ETF sectorial, un fondo que cotiza como una acción y agrupa a las empresas del sector) con historia desde 2009, más el SPY (ETF del mercado) y el XLP. KHC queda fuera porque sus precios empiezan en 2015. Los KPI del producto son tiempo por activo menor que 5 minutos, un cambio de pantalla, latencia tras un reporte de un día o menos y 100 % de decisiones documentadas; la línea base de los KPI 1, 2 y 5 queda **sin obtener** (la validación del 2026-10-18 fue asíncrona y el participante no respondió el formulario; §7).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/01_negocio.md>

## 2. Ideación y mockup

El producto entrega, para cada ticker, **seis niveles definidos por el usuario** (tres de entrada y tres de salida), en precio y en múltiplo. Cada nivel trae tres lecturas: **fundamental** (percentil histórico y de la industria del P/E, del P/E normalizado y de los ratios de calidad; el percentil responde "entre los valores pasados, ¿en qué puesto queda el de hoy?"), **técnica** por SVM lineal (*support vector machine*: un modelo que aprende a separar casos positivos de negativos y entrega una probabilidad) con horizonte de 60 días hábiles frente a su línea base por decil de volatilidad (solo entradas) y **probabilística** por simulación que remuestrea bloques de semanas de la acción y del XLP a la vez para construir futuros alternativos con la historia reciente (solo salidas). Un panel de riesgo descriptivo muestra cinco cifras: volatilidad anualizada (σ, dispersión típica del retorno), percentil 5 semanal, caída máxima histórica, frecuencia de caídas fuertes y dependencia del sector. Los niveles por múltiplo se recalculan cuando la SEC publica un reporte nuevo; para tickers fuera del piloto, el panel se marca "industria no validada" y las probabilidades llevan advertencia. El **mockup v2** incorpora el feedback del inversor del 2026-10-18 (sesión asíncrona por mensajería): una franja "Cómo leer esta pantalla" con 8 definiciones de una línea, P/E y P/B en columnas separadas, una columna "% vs. precio actual" y un panel de riesgo más espaciado; el "veredicto" que pidió el participante no se incorpora porque choca con la regla de no recomendar.

![Mockup v2 del dashboard (valores ilustrativos). La franja "Cómo leer esta pantalla" define 8 términos (P/E, P/B, percentil, industria piloto, **SVM**, lectura técnica, lectura probabilística, línea base) en una línea cada uno; la columna "Prob. de tocar en 60 días" muestra 21 %, 42 % y 71 % (modelo SVM, se entrena en la entrega 2) frente a la línea base por decil de volatilidad diaria (16 %, 35 % y 66 %), y la "Prob. de alcanzar la salida" muestra 81 %, 62 % y 37 % por simulación con la historia. Las notas 1 a 3 bajo la tabla llevan la lectura "¿suele ser temporal?". El panel de riesgo trae 5 cifras descriptivas; el recuadro "Desempeño histórico del modelo técnico (SVM)" aparece marcado "se calcula en la entrega 2". La marca del precio actual sobre el gráfico ("entre Valoración histórica \$67.20 y Salida negativo \$75.60") es descriptiva, sin veredicto.](assets/mockup.png){width=75%}

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/02_ideacion.md>

## 3. Aspectos éticos y legales

Tres riesgos quedan altos tras mitigar. **Regulación de la asesoría** (Ley 964 de 2005 y Decreto 2555 de 2010): la asesoría de inversión está reservada a entidades vigiladas por la SFC, y el producto evita entrar a ese perímetro porque no recomienda compra ni venta, no perfila al usuario y lleva en cada pantalla la leyenda del artículo 2.40.1.1.3. **Transparencia y explicabilidad** de la probabilidad del modelo técnico: se usa un SVM lineal con coeficientes legibles, la probabilidad siempre aparece junto a su línea base y a su desempeño histórico, y se publica la lista explícita de técnicas no cubiertas en clase. **Look-ahead y data snooping** (que el análisis vea datos del futuro, o que se pruebe de todo hasta encontrar algo): se usa la fecha `filed` (día en que la SEC publica el reporte), una ventana expansiva (solo datos hasta t) y 15 pruebas declaradas antes de ejecutar (Bonferroni en P4 y Holm como sensibilidad). También se cuida la anonimización del participante (Ley 1581 de 2012), los términos de uso de yfinance, SEC EDGAR y Damodaran, el sesgo de supervivencia de 21 emisores vigentes y la marca "industria no validada" fuera del piloto. **Técnicas no cubiertas en clase (15 en total):** bootstrap por bloques de fechas, nulo calibrado por simulación, ΔAUC con regresión logística, errores estándar agrupados por empresa, Brier y calibración, análisis de potencia (MDE), EPS TTM (utilidad por acción de los últimos 12 meses) a partir de 10-Q, SVM, simulación por bloques, Bonferroni, Holm, VIF, prueba F de modelos anidados, Mann-Whitney y clustermap; el detalle con la justificación de cada técnica está en el documento enlazado abajo.

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/03_etica_legal.md>

## 4. Enfoque analítico

El trabajo responde a **seis preguntas de negocio con una hipótesis cada una**. Cada hipótesis sigue la misma secuencia: umbral práctico fijado antes, H0/H1 y α = 0,05, prueba con su matriz de supuestos, estimación con intervalo de confianza al 95 % (IC95: rango en el que cae el estimado el 95 % de las veces si se repitiera el experimento, construido por bootstrap, un remuestreo que no supone una forma teórica), y dos decisiones. La **estadística** es "se rechaza H0" si el IC95 no incluye el valor nulo y "no se rechaza H0" si lo incluye. La **de negocio** es "accionable" si el límite inferior del IC95 supera el umbral, "efecto real, magnitud incierta" si se rechaza H0 pero el IC95 cruza el umbral, y "no accionable" en los demás casos. Lenguaje de asociación, nunca de causa.

La tabla reúne cada pregunta con lo que **decide en la herramienta** —qué pieza del producto depende de la respuesta—, el umbral, el estimado con IC95 y las dos decisiones. Un umbral de 0,03 **anualizado en log** equivale a cerca de 9 % acumulado en tres años; "anualizado en log" es el cambio porcentual promedio por año, medido con logaritmos para que los años se puedan sumar.

\begin{tabularx}{\linewidth}{@{}p{0.5cm} X X p{1.2cm} X p{2.6cm}@{}}
\hline
\textbf{P.} & \textbf{Pregunta} & \textbf{Decide en la herramienta} & \textbf{Umbral} & \textbf{Estimado · IC95} & \textbf{Decisión} \\
\hline
P1 & ¿Caídas semanales fuertes más que una normal igual? & Panel de riesgo: frec.\ de caídas fuertes. & 3,83 \% sem. & 3,08 \% · [2,46; 3,92] \% & no se rechaza H0 · no acc. \\
P2 & ¿El quintil barato sube su P/E norm.\ más que el caro a 3 años? & Lectura fundam.\ de entradas: percentil del P/E norm. & +0,03 anual.\ log & +0,153 · [+0,091; +0,221] & se rechaza H0 · acc. \\
P3 & ¿El quintil barato gana al XLP a 3 años? & Exceso sobre XLP no entra como señal. & +0,05 anual.\ log & +0,006 · [−0,032; +0,049] & no se rechaza H0 · no acc. \\
P4 & ¿Indicador técnico mejora (lineal) la AUC del modelo A de magnitud? & Lect. técnica: SVM solo magnitud; RBF en entrega 2. & +0,01 ΔAUC (×7) & 7 IC95 cruzan 0; dist\_sma50 −0,024 · [−0,066; +0,026] & no se rechaza H0 (×7) · no acc. \\
P5 & ¿XLP agrega ΔR² al SPY semanal? & Panel de riesgo (dep.\ del sector) y simulación acción + XLP. & +0,05 ΔR² & 0,225 · [+0,175; +0,291] & se rechaza H0 · acc.\ (confirm.) \\
P6 & ¿La turbulencia se agrupa? & Lectura probabilística: simulación por bloques de semanas. & 0,30 & P(T\textbar T) diaria 0,305 · [0,275; 0,340] & se rechaza H0 · magnitud incierta \\
\hline
\end{tabularx}

\footnotesize{Abreviaturas de la columna "Decisión": `acc.` = accionable (el límite inferior del IC95 supera el umbral); `no acc.` = no accionable; `(confirm.)` = confirmatoria (la propiedad se usó también para elegir la industria piloto; §7).}\normalsize

La lectura de P2 incluye una **advertencia descriptiva de posible deterioro de utilidades** (trampa de valor afirmada como asociación, Figura 2); los niveles de P6 se expresan en **k · σ252 diaria** (volatilidad del último año); y P5 justifica analizar una industria a la vez.

**Qué mide P1.** Una caída fuerte es una semana en que la acción cae más de 2 veces su volatilidad semanal típica del último año (`z < −2`, donde `z` es el retorno sobre su σ reciente). Si los retornos siguieran una distribución normal (campana de Gauss) con esa volatilidad conocida, pasaría en el 2,3 % de las semanas (≈ 1 de cada 44, ≈ 1,2 al año); como la volatilidad se estima con el pasado y no se conoce, la tasa comparable, calibrada por simulación con la misma receta, es ≈ 2,55 % (≈ 1 de cada 39, ≈ 1,3 al año). El umbral práctico de 3,83 % (≈ 1 de cada 26, ≈ 2 al año) duplicaría esa frecuencia y agotaría más seguido el presupuesto de pérdida fijado con la volatilidad histórica. El estimado es 3,08 % (≈ 1 de cada 32, ≈ 1,6 al año; IC95 1,3–2,0 al año): el panel no infla la "frecuencia de caídas fuertes" artificialmente.

**Qué es el P/E normalizado.** El P/E es precio sobre utilidad por acción (EPS). El P/E normalizado es precio dividido por el **EPS promedio de los últimos 3 años** (utilidad neta de los 12 trimestres ya publicados ÷ 3 ÷ acciones). Promediar 3 años evita que un solo año excepcional —malo o bueno— haga parecer barata o cara una acción. "Barata frente a su historia" se opera como el quintil con el P/E normalizado más bajo de la industria en esa fecha.

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
\captionof*{figure}{\footnotesize \textbf{Figura 2. P2:} Δlog(P/E normalizado) a 3 años, barato (Q1) vs caro (Q5): \textbf{+0,153 anualizado} (IC95 por empresa [+0,091; +0,221]). \textbf{Trampa de valor como asociación}: la diferencia barato − caro reparte +0,46 (log, 3 años) en Δlog(precio) +0,014 (IC95 [−0,115; +0,155], cruza 0) y Δlog(EPS prom 3a) −0,444 (IC95 [−0,693; −0,210], excluye 0). nb04 §2.7--§2.8.}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\centering
\includegraphics[width=\linewidth]{assets/nb04_p4_zonas.png}
\captionof*{figure}{\footnotesize \textbf{Figura 3. P4:} ΔAUC por indicador frente al modelo A de magnitud (AUC 0,577 submuestra). Los 7 IC95 (Bonferroni ≈ 99,3 \%) cruzan 0; mayor en v.\,abs. \texttt{dist\_sma50} (−0,024, [−0,066; +0,026]); más estrecho \texttt{vol\_rel20} (−0,001, [−0,011; +0,010]). Base del SVM (todas las filas): decil de σ252, \textbf{AUC 0,591} con N = 60. \texttt{variables\_svm = \{|r\_t|, σ20/σ252, σ252\}}; P4 solo mide \textbf{aporte lineal}. nb04 §5.3.}
\end{minipage}
\end{figure}

**Dos lecturas requieren contexto.** En **P2**, la descomposición de la diferencia barato − caro afirma la trampa de valor como asociación (IC en la Figura 2). En **P4**, no hay evidencia de aporte **lineal** de los 7 indicadores sobre el modelo A de magnitud; las variables del SVM quedan solo de magnitud y la entrega 2 prueba el **SVM RBF** para captar aportes no lineales. Holm al 0,05 sobre las 13 pruebas con decisión de negocio deja rechazando a las cuatro que ya rechazaban (P2, P5, P6 diaria y P6 semanal); ninguna decisión cambia (nb04 §8).

Detalle: <https://github.com/louis97/asistente-financiero/blob/main/notebooks/03_eda_univariado.ipynb> · <https://github.com/louis97/asistente-financiero/blob/main/notebooks/04_eda_multivariado.ipynb>

## 7. Conclusiones iniciales e insights

**Hallazgos (asociaciones, no causas).** Caídas semanales fuertes no más frecuentes que una normal igual (P1); quintil barato sube más su P/E normalizado que el caro a 3 años, con trampa de valor afirmada como asociación (P2, Figura 2); el barato no gana al XLP a 3 años (P3); sin evidencia de aporte **lineal** de los 7 indicadores sobre el modelo A de magnitud (P4); XLP agrega ΔR² mediano 0,225 al SPY (P5, confirmatoria); turbulencia que se agrupa con magnitud incierta (P6). **Insights:** percentil del P/E normalizado con advertencia de posible deterioro de utilidades; exceso sobre XLP solo como contexto; niveles en k · σ252 con N = 60; simulación por bloques de acción + XLP; `variables_svm = {|r_t|, σ20/σ252, σ252}` frente a base del SVM AUC 0,591. **Limitaciones:** industria piloto; supervivencia; historia desde 2009; EPS TTM 91,2 %; ventanas de 3 años solapadas (IC por empresa); P5 confirmatoria; P4 con fuga de selección y solo aporte lineal; **mockup validado con un solo inversor, asíncrona, y KPI 1, 2 y 5 sin línea base**. **Acciones próximas:** SVM (lineal y RBF para aportes no lineales), simulación por bloques, **prototipo navegable con más usuarios** y medición de KPI, segunda industria. Detalle: <https://github.com/louis97/asistente-financiero/blob/main/docs/entrega_1/07_conclusiones.md>
