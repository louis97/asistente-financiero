# Glosario (fuente única de definiciones)

Cada entrada se cuenta en 1–2 líneas con un ejemplo numérico tomado de las instantáneas en `data/snapshots/` o de los resultados `data/resultados/nb03.json`, `nb04.json` y `nb04_p4.json`. Los enlaces desde los notebooks apuntan a `docs/entrega_1/glosario.md`.

El orden es alfabético (los números y letras griegas se ordenan por su nombre: Δ como "delta", σ como "sigma"). Los sinónimos ("sesión turbulenta" ≡ "semana turbulenta"; "bootstrap por empresa" ≡ "bootstrap por ticker") se referencian entre sí.

---

**10-K** · Informe anual que las empresas que cotizan en EE.UU. presentan ante la SEC. Trae los estados financieros auditados del año fiscal. Ejemplo: el 10-K de KO del cierre 2025-12-31 se publicó el 2026-02-20 (ver `tabla_trimestral`, filas `origen = q4_derivado`).

**10-Q** · Informe trimestral de los primeros tres trimestres del año fiscal (el cuarto queda cubierto por el 10-K). Trae ingresos, utilidad y balance a esa fecha de corte. Ejemplo: el 10-Q de KO con `end = 2026-04-03` se publicó el 2026-04-30 (`filed`).

**acción** · Una fracción del capital de una empresa. Si una empresa tiene 1.000 acciones y uno posee 10, posee el 1 % de la empresa. En este proyecto cada "ticker" (KO, PEP, PG, …) es una acción distinta.

**acumulado del año (YTD, *year-to-date*)** · Suma de un flujo (ingresos, utilidad, caja operativa) desde el primer día del año fiscal hasta la fecha de corte del reporte. Ejemplo: en un 10-Q con `end = 30 de junio` el YTD cubre enero–junio.

**año fiscal (y cierre fiscal distinto de diciembre)** · Período de doce meses que cada empresa escoge para contar sus resultados. La mayoría usa enero–diciembre, pero algunas no: WMT y COST cierran su año fiscal en enero. nb02 §2b (chequeo 5) marca estos casos para que al sumar cuatro trimestres se respete el año fiscal, no el calendario.

**asociación (lenguaje de)** · Convención del proyecto: las conclusiones se escriben como asociaciones ("A y B tienden a ir juntos"), nunca como causas ("A causa B"). Las técnicas usadas aquí observan patrones; no manipulan ni aíslan variables.

**AUC (*area under the ROC curve*)** · Mide qué tan bien un puntaje separa las dos clases de una etiqueta binaria (0/1). Toma valores de 0 a 1: 0,5 es azar y 1 es separación perfecta. Ejemplo: la línea base por decil de σ252 diaria del nb04 §4.5 tiene AUC = 0,591 en la prueba 2019–2024.

**Bonferroni** · Corrección por multiplicidad: cuando se hacen k pruebas se usa un nivel de confianza de 1 − α/k en cada una, para que la tasa global de falsos positivos siga siendo α. nb04 §5.3 usa 1 − 0,05/7 ≈ 99,3 % para los 7 indicadores de P4.

**bootstrap por bloques (de fechas)** · Técnica de remuestreo que respeta la dependencia temporal: se muestrean trozos consecutivos de fechas con reemplazo y se recalcula el estimado. El IC sale de los percentiles 2,5 y 97,5 de los estimados remuestreados. Ejemplo: P1 (nb03 §4.4) construye el IC de la tasa de caídas fuertes con bloques semanales.

**bootstrap por empresa (por grupos / por ticker)** · Remuestreo con reemplazo del listado de empresas (en vez de filas o bloques de tiempo). Se usa cuando una empresa aporta varias filas y lo que varía entre empresas es lo que domina el IC. Ejemplo: P2 (nb04 §2.6) remuestra las 21 empresas (menos las excluidas por falta de EPS); "bootstrap por empresa" y "bootstrap por ticker" son el mismo concepto.

**Brier (puntaje de Brier)** · Error cuadrático medio entre una probabilidad predicha y lo que pasó (1 si ocurrió, 0 si no). Va de 0 (perfecto) a 1; más bajo es mejor. Ejemplo: si el modelo dice 0,6 y el precio sí tocó el nivel, el error de esa observación es (1 − 0,6)² = 0,16. Se usará en la entrega 2 para el SVM y la simulación (punto 4 §4.4).

**BVPS (*book value per share*, valor en libros por acción)** · `patrimonio ÷ acciones`. Es el patrimonio contable que corresponde a cada acción. Ejemplo: KO 2026-04-03 tiene `bvps = 7,80` USD por acción (`ratios_ttm`).

**caída máxima (drawdown)** · La peor pérdida acumulada desde un máximo histórico de la serie hasta el siguiente mínimo. Se expresa como fracción. Ejemplo: en nb03 §1 cada ticker tiene su `drawdown` máximo observado. Un drawdown de −0,30 significa que el precio llegó a estar un 30 % por debajo de su máximo anterior.

**calibración (diagrama de calibración)** · Compara la probabilidad que promete un modelo con la frecuencia con la que el evento ocurrió, por tramos de probabilidad. Un modelo calibrado que dice 60 % acierta cerca de 6 de cada 10 veces: los puntos quedan sobre la diagonal. Se usará en la entrega 2 (punto 4 §4.4).

**canal Donchian** · Franja entre el máximo y el mínimo de los últimos N períodos. Se usa como indicador `donchian20`, que mide la posición del cierre dentro de ese canal (0 toca el mínimo, 1 toca el máximo). nb04 §5.

**censura** · Observación que no se puede resolver porque falta parte del futuro: la etiqueta "¿toca el nivel en 60 días?" queda vacía para los últimos 60 días hábiles de la muestra. Regla del proyecto: una métrica se calcula solo sobre la población donde está definida; las filas censuradas no se mezclan con las completas.

**chi-cuadrado (tabla de contingencia)** · Prueba estadística para una tabla de dos variables categóricas: compara los conteos observados con los esperados bajo independencia. Se acompaña de la **V de Cramér** para medir la fuerza de la relación. nb03 §5 usa chi-cuadrado para P6 (semanal y diaria).

**clustermap** · Mapa de calor que ordena filas y columnas de una matriz (por ejemplo, de correlaciones) agrupando lo parecido con un dendrograma. Ejemplo: nb04 §6.6 muestra el clustermap de los 21 retornos semanales de la industria.

**comisionista (sociedad comisionista de bolsa)** · Entidad vigilada por la SFC que ejecuta órdenes de compra y venta de valores por cuenta del inversor. En Colombia es la vía por la que una persona natural accede al mercado de valores (local o internacional, a través del Mercado Global Colombiano).

**contado (spot)** · Compra o venta de un valor para liquidación inmediata al precio del día, en vez de a plazo o con un derivado. En este proyecto se asume que el inversor opera siempre al contado.

**data snooping** · Probar muchas combinaciones de parámetros, variables o reglas sobre los mismos datos y reportar la mejor: infla el desempeño aparente y aumenta la probabilidad de un falso positivo. Se mitiga con una lista fija de pruebas declaradas antes de ejecutar, umbrales fijos y validación cronológica (ver también **sobreajuste**; [punto 3](03_etica_legal.md) §3.1).

**decil** · Grupo que resulta de partir una variable en diez partes iguales por sus percentiles 10, 20, …, 90. El decil 1 es el 10 % más bajo y el 10 el 10 % más alto. nb04 §4.5 arma los deciles de σ252 diaria.

**decisión de negocio (regla accionable / efecto real, pero de magnitud incierta / no accionable)** · Se fija un umbral práctico antes de ver los datos. Después se mira el IC estimado: accionable si el límite inferior supera el umbral; "efecto real, pero de magnitud incierta" si se rechaza H0 pero el IC cruza el umbral; no accionable en los demás casos.

**decisión estadística ("se rechaza H0" / "no se rechaza H0")** · Convención del proyecto: solo se usan estas dos frases. Nunca "se acepta H0" ni "la hipótesis queda apoyada". La decisión sale del IC frente al valor del nulo (α = 0,05).

**ΔAUC** · Diferencia entre el AUC de un modelo que agrega un indicador y el AUC de la línea base (sin ese indicador). Mide cuánto aporta el indicador. P4 fija el umbral en 0,01. Ejemplo: `rsi14` tiene ΔAUC = −0,008 (no accionable; nb04_p4.json).

**Δlog(P/E normalizado)** · Cambio del logaritmo del P/E normalizado en un horizonte (3 años). Se descompone en `Δlog(precio) − Δlog(EPS promedio)`: separa cuánto del cambio vino del precio y cuánto de las utilidades. La suma es exacta porque el log convierte el cociente en una resta.

**ΔR²** · Diferencia entre el R² de una regresión con una variable extra y el R² de la regresión sin ella. Mide la mejora de ajuste. ΔR² nunca es negativo si se agregan regresores (`sumas de cuadrados anidadas`), por eso se usa como medida de aporte en P5.

**deuda/patrimonio** · Cuánta deuda financiera tiene la empresa frente a su patrimonio. Si el patrimonio vale 100 y la deuda de largo plazo 60, la razón vale 0,60. Ejemplo: KO 2026-04-03, `deuda_patrimonio = 1,16` (`ratios_ttm`).

**día hábil** · Día en que la bolsa opera (lunes a viernes, sin feriados de EE.UU.). nb04 §4 usa días hábiles para contar horizontes diarios; N = 60 días es un trimestre bursátil.

**distancia a la media (`dist_sma20`, `dist_sma50`, `dist_sma200`)** · `precio ÷ media móvil − 1`. Mide qué tan por encima o por debajo de su promedio reciente está el precio. 0 significa "sobre la media"; 0,10 significa "10 % por encima de su media de 20 días". nb04 §5.

**drawdown** · Ver "caída máxima".

**enfoque value** · Estrategia de compra que busca empresas cuyo precio en bolsa queda por debajo de una valoración razonable (por su historia o por su industria), con horizonte largo. Es el enfoque del usuario del producto; se contrapone al enfoque de crecimiento, que paga múltiplos altos a cambio de utilidades que se esperan mayores en el futuro.

**EPS (*earnings per share*, utilidad por acción)** · `utilidad neta ÷ acciones diluidas`. Es la utilidad que corresponde a cada acción. Ejemplo: KO 2026-04-03, `eps_ttm = 3,18` USD por acción (`ratios_ttm`).

**EPS TTM (de los últimos 12 meses)** · `utilidad_neta_ttm ÷ acciones del último trimestre`. El numerador es la suma de la utilidad neta de los cuatro trimestres más recientes ya publicados; el denominador es el `acciones` del cierre del último trimestre (nb01 §4.3). Ejemplo: KO 2026-04-03 con `eps_ttm = 3,18` USD por acción.

**estacionariedad** · Propiedad de una serie temporal cuyos momentos (media y variabilidad) no cambian con el tiempo. Los precios no son estacionarios (crecen y la variabilidad cambia por épocas); los retornos sí lo son de forma aproximada. Las pruebas aquí aplicadas suponen estacionariedad (ver [punto 4](04_enfoque_analitico.md) §4.0).

**ETF (*exchange-traded fund*)** · Fondo que agrupa muchas acciones y se compra como una sola. Replica una canasta (un índice). En el proyecto se usan dos: el SPY y el XLP.

**ETF sectorial (XLP)** · ETF que agrupa las empresas de consumo defensivo de EE.UU. (Consumer Staples Select Sector SPDR Fund). nb03 y nb04 lo usan como "la industria" para P3 y P5.

**etiqueta de entrada ("toca el nivel")** · Variable binaria del nb04 §4: vale 1 si el precio cae a `close × exp(−k · σ252 · √N)` dentro de los siguientes N días hábiles, y 0 si en esos N días sube a `close × exp(k · σ252 · √N)` o se agota el tiempo. k = 1 y N = 60 en nb04. Las últimas N observaciones quedan censuradas.

**exceso sobre el XLP** · Para P3, retorno logarítmico de la empresa menos retorno logarítmico del XLP sobre el mismo horizonte: `log(P_T/P_0) − log(XLP_T/XLP_0)`. Un exceso positivo significa que la empresa superó al sector; uno negativo, que quedó por debajo.

**filed (fecha de publicación)** · Fecha en que un reporte de EDGAR se hizo público. Es la primera fecha en que un inversor pudo usar esa información. Toda unión con precios se hace por `filed` para evitar look-ahead. Ejemplo: `tabla_trimestral` fila 2023Q1 de KO tiene `filed = 2023-04-26` (26 días después del cierre del trimestre).

**frecuencia diaria y semanal** · Dos resoluciones de precios: `precios_diarios` tiene una fila por día hábil; `precios_semanales` una fila por lunes de la semana. nb03 maneja P1 en semanal y P6 en diaria y semanal.

**fuerza relativa (a 14 días)** · Nombre común del **RSI** (ver más abajo). Mide la fuerza de las variaciones positivas frente a las negativas en las últimas 14 sesiones.

**fundamentales (análisis fundamental)** · Estudio del valor de una empresa a partir de sus estados financieros: ingresos, utilidad, patrimonio, deuda y los **ratios** y **múltiplos** derivados de ellos. Se contrapone al análisis técnico, que mira solo precios y volúmenes.

**H0 / H1** · H0 es la hipótesis nula (el "no hay efecto" o el valor de referencia). H1 es la hipótesis alternativa. Se escribe la dirección de H1 antes de ver los datos y no se cambia. Ejemplo P1: H0 `p ≤ 2,55 %`, H1 `p > 2,55 %` (nb03 §4.2).

**Holm** · Corrección por multiplicidad "paso a paso": ordena los p-values de k pruebas y las compara con α/k, α/(k−1), …, α. Es menos conservadora que Bonferroni. El proyecto la reporta como sensibilidad sobre las 13 pruebas con decisión de negocio, aplicada sobre el p bilateral equivalente `2·p` de cada prueba frente a α = 0,05 (nb04 §8).

**horizonte de valor (3 años)** · Ventana de evaluación de P2 y P3: se compara el P/E normalizado o el exceso sobre el XLP entre `t` y `t + 3 años`. 3 años es el horizonte típico que declara el inversor value en la ideación.

**IC** · Alias de "intervalo de confianza". Ver abajo.

**indicador técnico** · Variable derivada solo de precios y volumen históricos (sin información fundamental). nb04 §5 estudia siete: `rsi14`, `dist_sma20`, `dist_sma50`, `dist_sma200`, `vol_rel20`, `donchian20`, `mom_12_1`. Todos miran solo hacia atrás.

**industria piloto (consumo defensivo)** · Las 21 empresas de consumo defensivo con historia desde 2009 y en el XLP (KO, PEP, PG, WMT, COST, CL, MDLZ, KMB, GIS, MO, PM, HSY, KR, SYY, ADM, CLX, CHD, MKC, STZ, CAG, TSN). KHC queda fuera porque sus precios comienzan en 2015. Se analiza esta industria para la entrega 1; el producto se diseñó para cualquier industria.

**instantánea (snapshot)** · Archivo con fecha congelada que fija la versión exacta de los datos usada en el análisis. Garantiza que correr el proyecto con la misma instantánea reproduce las mismas cifras aunque la fuente cambie. Las del proyecto viven en `data/snapshots/` (fecha de corte: 2026-10-15).

**intervalo de confianza (IC)** · Rango de valores plausibles para un parámetro, con un nivel de confianza fijado (95 % en el proyecto). Ejemplo P1: IC = [0,0246; 0,0392] para la tasa de caídas fuertes (nb03.json). "El 95 %" se refiere al procedimiento, no a la probabilidad del parámetro.

**línea base por decil de σ** · Puntaje que ordena las observaciones por su decil de σ252 diaria y toma el decil como predictor. Es la **base del SVM** (sobre todas las filas): el SVM de la entrega 2 debe superarla por al menos ΔAUC = 0,03 para ser accionable (`04_enfoque_analitico.md` §4.4). Ejemplo: su AUC en la prueba es 0,591 (`nb04_p4.json`). *Nota.* En P4 cada indicador no se compara contra esta base, sino contra el **modelo A** (regresión logística con `|r_t|`, `σ20/σ252` y `σ252`) sobre la submuestra sin solapamiento (AUC 0,577); P4 mide el aporte **lineal** de cada indicador frente al modelo A.

**log-retorno** · `log(P_t / P_{t−1})`. Es el retorno expresado en logaritmo natural. Se suma a través del tiempo: el log-retorno de dos períodos es la suma de los dos log-retornos. Base de P1, P5 y la volatilidad.

**look-ahead** · Error de usar información del futuro al tomar una decisión en `t`. En este proyecto se evita con `shift(1)`, ventanas expansivas y la fecha `filed`. La etiqueta es lo único que mira al futuro.

**Mann-Whitney (prueba U)** · Prueba no paramétrica que compara dos muestras independientes por su mediana (en realidad, por su rango). No supone normalidad. Se complementa con bootstrap porque las observaciones no son independientes.

**margen operativo** · `utilidad operativa ÷ ingresos`. Qué fracción de las ventas queda después de los costos y gastos del negocio (antes de intereses e impuestos). Ejemplo: KO 2026-04-03, `margen_operativo_ttm = 0,29` (29 %).

**MDE (diferencia mínima detectable) / potencia** · El MDE es el efecto más pequeño que una prueba podría detectar con la potencia pedida (80 % en este proyecto) dado el tamaño muestral y la varianza observada. Si el umbral de negocio queda por debajo del MDE, la prueba está "corta": no sabría distinguir un efecto accionable del nulo. nb04 §2.5 y §3.3 lo calculan antes de estimar.

**media móvil** · Promedio del precio de los últimos n períodos. La "simple" (SMA) le da el mismo peso a cada observación. Es la base de los indicadores `dist_sma20`, `dist_sma50`, `dist_sma200`.

**momentum 12-1 (`mom_12_1`)** · `precio_{t−21} / precio_{t−252} − 1`. Mide el retorno de los últimos 12 meses, saltándose el último mes para separar el efecto "momentum" del "reversión de corto plazo". nb04 §5.

**múltiplo** · Razón entre el precio de una acción y una magnitud contable por acción (utilidades, patrimonio, ventas). Se usa para comparar precios entre empresas y a lo largo del tiempo. Los dos múltiplos del producto son el **P/E** y el **P/B**. Ejemplo: KO con precio 92 USD y `eps_ttm = 3,18` tiene un P/E (TTM) ≈ 29.

**N = 60 días (horizonte de la etiqueta)** · Cuántos días hábiles hacia adelante mira la etiqueta de P4 para decidir si el precio "toca el nivel". N = 60 (≈ 3 meses bursátiles) se eligió en nb04 §4.3 maximizando AUC entre los candidatos cuya tasa de toque cae en 10–40 %.

**nivel de entrada** · Precio por debajo del precio actual que el usuario fijaría como oportunidad de compra. En el producto son 3 niveles de entrada por acción.

**nivel de salida** · Precio por encima del precio actual que el usuario fijaría como oportunidad de venta. En el producto son 3 niveles de salida por acción, todos por encima del precio actual.

**nulo calibrado por simulación** · Valor de referencia que se calcula simulando retornos normales i.i.d. con la **misma receta** de σ estimada que se aplica a los datos observados. Con σ estimada (no conocida) la tasa de caídas con `z < −2` supera Φ(−2) = 2,275 %; el nulo calibrado da la referencia justa aplicando la misma receta. nb03 §4.1 lo usa para P1 (función `nulo_caidas_fuertes`). Resultado: 2,55 %.

**p bilateral equivalente** · Cuando una prueba se reporta por el IC, el p-value se calcula bilateralmente a partir de las réplicas del bootstrap, aunque H1 sea unilateral. Es solo informativo (la decisión viene del IC). nb04 §3.5.

**p bootstrap** · Fracción de las réplicas del bootstrap cuya estimación quedó al menos tan lejos del nulo como la observada. Ejemplo: P1 tiene `p_boot = 0,049` (nb03.json); P2 tiene `p_boot ≈ 0,001` (nb04.json).

**P/B (*price-to-book*)** · `precio ÷ BVPS`. Múltiplo que compara el precio con el patrimonio contable por acción. P/B = 1 significa "pago el patrimonio exactamente". nb04 §1.

**PCA (análisis de componentes principales)** · Técnica no supervisada que proyecta variables correlacionadas en pocos ejes ortogonales ordenados por varianza explicada. En nb04 §6.6 el PC1 de los 21 retornos semanales se interpreta como "el movimiento común de la industria".

**P/E "actual"** · P/E calculado con el EPS de los últimos 12 meses ya publicados (**EPS TTM**). Es el P/E que se actualiza con cada reporte trimestral. Ejemplo: KO 2026-10-12 con `close = 92,00` y `eps_ttm = 3,18` tiene P/E actual ≈ 29. Se contrapone al **P/E normalizado**.

**P/E normalizado** · `precio ÷ EPS promedio de los últimos 3 años` (12 trimestres ya publicados; variable `eps_prom_3a` del `ratios_ttm`). Un paso intermedio evita el redondeo: `eps_prom_3a ≈ 2,725` da P/E normalizado ≈ 33,8 (`92,00 / 2,725`). Un solo año excepcional puede hacer que una acción parezca barata sin serlo; promediar varios años evita esa ilusión. Ejemplo: KO 2026-10-12 con `eps_prom_3a ≈ 2,725` tiene P/E normalizado ≈ 33,8, por encima del P/E actual. Referencias: Graham y Dodd (1934), *Security Analysis*, McGraw-Hill; Campbell y Shiller (1998), *Journal of Portfolio Management*, 24(2), 11–26, DOI 10.3905/jpm.24.2.11.

**P/E (*price-to-earnings*)** · `precio ÷ EPS`. Múltiplo que indica cuántas unidades de precio se pagan por cada unidad de utilidad. Ejemplo: KO 2026-10-12 con `close = 92,00` USD y `eps_ttm = 3,18` tiene P/E ≈ 29.

**percentil** · Valor por debajo del cual queda cierta fracción de la muestra. El percentil 5 es el valor que deja el 5 % más bajo por debajo. nb03 §2.

**percentil 5 (del retorno)** · Valor del percentil 5 de la distribución de retornos. Si el p5 del retorno semanal de KO es −4 %, significa que una de cada 20 semanas KO cae al menos 4 %.

**percentil expansivo** · Percentil de un valor dentro de su propia historia hasta `t`: usa todas las observaciones de la misma empresa anteriores a `t`. Se calcula con ventana expansiva (`shift(1)` previo) para evitar look-ahead. nb04 §1.

**posición larga** · Comprar un activo con la expectativa de que suba. En el proyecto el inversor solo opera en largo: compra la acción y la vende más adelante. Se contrapone a la posición corta (vender prestada una acción esperando que baje).

**presupuesto de pérdida** · Pérdida semanal que el inversor acepta en una acción. Si la fija con la volatilidad histórica (p. ej., una caída de 2 σ), espera tocarla ≈ 1,3 veces al año (2,55 %); si las caídas fuertes pasaran el 3,8 % de las semanas, la tocaría ≈ 2 veces y el presupuesto se agotaría más seguido. Es el término que P1 (nb03 §4.1) compara contra el nulo calibrado.

**prueba F de modelos anidados** · Compara el R² de dos regresiones donde una incluye a la otra (anidadas). Dice si las variables extra aportan información significativa. nb04 §6.3 (P5).

**Q4 derivado** · El cuarto trimestre no se reporta como 10-Q; se obtiene restando al 10-K anual los tres trimestres anteriores del mismo año fiscal. El `filed` queda en la fecha del 10-K (nb01 §4.1; `origen = q4_derivado` en `tabla_trimestral`).

**quintil** · Grupo que resulta de partir una variable en cinco partes iguales por sus percentiles 20, 40, 60, 80. En el proyecto se usa "quintil barato" (percentil ≤ 20 %) y "quintil caro" (percentil > 80 %). nb04 §2.3.

**quintil por fecha** · Clasificación en quintiles que se recalcula en cada fecha trimestral. Reglas de nb04 §2.3: (i) una fecha entra a los quintiles solo si tiene al menos 15 empresas con `pct_norm` publicado; (ii) con n empresas vigentes, `k = round(0,2·n)` empresas de menor `pct_norm` forman el quintil barato y las k de mayor `pct_norm` el caro (quintiles balanceados); los empates se rompen por orden de llegada. Evita el look-ahead porque usa solo la distribución disponible hasta esa fecha.

**R²** · Fracción de la variación de la variable respuesta que explica una regresión. Va de 0 a 1. nb04 §6.3 (P5).

**ratio** · Razón entre dos magnitudes contables (p. ej. `ROE = utilidad ÷ patrimonio`). A diferencia del **múltiplo**, no mezcla precio con contabilidad: compara partes del negocio entre sí. Ejemplo: KO con `roe_ttm = 0,41` (41 %).

**reexpresión** · Un reporte posterior modifica cifras ya publicadas. En este proyecto se usa la **primera publicación** (fecha `filed` original) para no incorporar información que no estaba disponible en `t`. nb02 §3.

**regresión a la media** · Fenómeno estadístico: una medición extrema con parte de azar tiende a quedar menos extrema en la siguiente medición. No es una "fuerza"; es el efecto de que el azar se promedia. En el proyecto se usa lenguaje de asociación, nunca de causa.

**retorno** · Cambio relativo del precio. En este proyecto se usa el **retorno simple** `P_t / P_{t−1} − 1` para la comunicación y el **log-retorno** `log(P_t / P_{t−1})` para los cálculos (porque se suma a través del tiempo).

**retorno simple** · `P_t / P_{t−1} − 1`. 0,05 significa "subió 5 %"; −0,05 significa "cayó 5 %".

**reversión a la normal** · Cuando un múltiplo (por ejemplo, el P/E normalizado) se aleja mucho de su nivel habitual, tiende a volver a él con el tiempo. Es la lectura que motiva a P2: si está barato frente a su historia, el mercado puede corregir hacia arriba. Se explica sin modelos econométricos.

**ROE (*return on equity*, rentabilidad del patrimonio)** · `utilidad neta ÷ patrimonio`. Qué fracción del patrimonio contable se ganó en el año. Ejemplo: KO 2026-04-03, `roe_ttm = 0,41` (41 %).

**RSI (*relative strength index*, también "fuerza relativa")** · Indicador técnico entre 0 y 100 que mide la fuerza de las variaciones positivas frente a las negativas en una ventana (14 días en el proyecto). Valores altos (>70) sugieren sobrecompra; bajos (<30), sobreventa. nb04 §5.

**screener** · Herramienta web que filtra un universo grande de acciones por criterios cuantitativos (p. ej. patrimonio, utilidad, deuda) y devuelve la lista corta de las que cumplen. El inversor del producto usa un screener para elegir qué activos analizar; el asistente **no** hace screening (ver [punto 1](01_negocio.md) §1.4).

**semana turbulenta** · Semana en que `|retorno|` supera el percentil 80 de la propia historia previa de la acción (ventana expansiva, `shift(1)`). Se usa en la variante semanal de P6 (nb03 §5). Sinónimo semanal de la "sesión turbulenta".

**sesgo de supervivencia** · Analizar solo las empresas que sobrevivieron hasta hoy puede sobreestimar los retornos: las que quebraron o fueron deslistadas quedan fuera de la muestra. Es más relevante en horizontes largos (3 años). nb02 §6.

**sesión turbulenta** · Sesión bursátil (día) en que `|retorno diario|` supera el percentil 80 de la propia historia previa de la acción (ventana expansiva, `shift(1)`). P6 (diaria) estudia la probabilidad de que una sesión turbulenta venga seguida por otra (nb03 §5). Es la variante diaria de la "semana turbulenta".

**σ20 diaria** · Desviación estándar de los retornos diarios de las últimas 20 sesiones (un mes bursátil). nb04 §4.

**σ20/σ252** · Razón `σ20 diaria ÷ σ252 diaria`. Capta la aceleración o calma relativa de la volatilidad. Es una de las tres variables del modelo A (regresión logística con las tres variables de magnitud; AUC 0,577 en la prueba) de nb04 §5.

**σ252 diaria (volatilidad anualizada)** · Desviación estándar de los retornos diarios de las últimas 252 sesiones (un año bursátil). nb03 §0.3 y nb04 §4.

**sobreajuste (*overfitting*)** · Un modelo o un procedimiento aprende el ruido de los datos y no la señal; funciona bien en lo que ya vio y falla en lo nuevo. Se controla con corte cronológico, Bonferroni/Holm y validación en datos distintos a los del ajuste. Ver también **data snooping**.

**solapamiento de ventanas** · Dos observaciones de la misma empresa en fechas cercanas comparten parte del horizonte futuro. Hace que las observaciones no sean independientes. Se mitiga con submuestras sin solapamiento (una fila cada N días) y con IC por bloques o por empresa.

**Spearman (correlación de rangos)** · Mide asociación monótona (no lineal necesariamente): se calcula sobre los rangos de las dos variables. Robusta a atípicos. nb04 §5.9 (regla de redundancia de P4) y §6.6 (clustermap de los 21 retornos semanales).

**split** · Partición de una acción en varias nuevas sin cambiar el valor total de la empresa. Un split 2:1 duplica el número de acciones y divide el precio en 2. El `close` de yfinance ya viene ajustado por splits y dividendos. Ejemplo (`splits.parquet`): KO tuvo splits 2:1 el 1965-02-19, 1968-06-03, 1977-06-01, 1990-05-14, 1992-05-12, 1996-05-13 y 2012-08-13, y un split 3:1 el 1986-07-01.

**splits (instantánea `splits.parquet`)** · Tabla con los eventos de split por ticker: `ticker`, `fecha` y `ratio`. Se descarga para auditar la trazabilidad del precio ajustado.

**SPY** · ETF que replica al S&P 500. En el proyecto representa "el mercado": el referente de los retornos del universo accionario estadounidense. nb04 §6 (P5).

**submuestra sin solapamiento** · De la tabla diaria se toma una fila cada N días hábiles (misma fecha para todas las acciones). Reduce la dependencia entre observaciones consecutivas de la etiqueta. nb04 §5 construye la submuestra con N = 60 y §5.3b explora su sensibilidad al tamaño del bloque.

**tasa de toque** · Fracción de observaciones con etiqueta `y = 1`. Es la tasa a la que, en los datos, el precio tocó el nivel inferior antes del superior o del tiempo. nb04 §4.5.

**tercil** · Grupo que resulta de partir una variable en tres partes iguales por sus percentiles 33 y 67.

**trampa de valor** · Una acción se ve barata (P/E bajo) porque el mercado anticipa que sus utilidades van a caer. Si uno compra pensando "está barata" sin mirar las utilidades, el P/E se puede corregir hacia la media bajando el precio, no subiendo el EPS. nb04 §3.8 testea este patrón.

**triangulación** · Contrastar un mismo hecho con dos o más fuentes independientes para detectar errores. Ejemplos del proyecto: `eps_ttm` calculado desde `tabla_trimestral` se compara con el `trailingEps` que publica yfinance, y el sector reportado por yfinance se compara con la pertenencia al XLP (nb02 §4 y §5).

**TTM (últimos 12 meses, *trailing twelve months*)** · Suma de los cuatro trimestres más recientes ya publicados. Da una lectura "siempre al día" sin esperar al cierre del año fiscal. nb01 §4.3.

**turbulencia** · En este proyecto, la propiedad de que una sesión bursátil (o una semana) tenga `|retorno|` por encima del percentil 80 de la propia historia previa de la acción (ver **sesión turbulenta** y **semana turbulenta**). P6 estudia si las sesiones turbulentas vienen juntas (agrupamiento de la volatilidad).

**V de Cramér** · Medida del tamaño del efecto de una tabla de contingencia (va de 0 a 1). Acompaña a la prueba chi-cuadrado para expresar la magnitud de la asociación en una unidad interpretable. nb03 §5.4.

**validación cronológica** · Procedimiento de evaluación que respeta el orden temporal: el modelo se ajusta con observaciones hasta `t` y se evalúa con las posteriores (nunca al revés). Evita el look-ahead y mide un desempeño comparable al de uso real. En el proyecto el corte es 2018 (entrenamiento) frente a 2019+ (prueba) con un espacio de ≥ N días hábiles entre ambos.

**VIF (*variance inflation factor*)** · Diagnóstico de multicolinealidad en regresión múltiple: cuánto se infla la varianza del coeficiente de una variable por su correlación con las demás. VIF > 10 suele considerarse problemático. nb04 §6.3.

**volatilidad** · Dispersión de los retornos; se mide con la desviación estándar. Cuando se calcula sobre los retornos diarios de un año (252 sesiones) se habla de **volatilidad anualizada** o `σ252 diaria`.

**volatilidad móvil** · Volatilidad calculada en una ventana que se desplaza en el tiempo (por ejemplo, los últimos 20 o 252 días). Mide cómo cambia la dispersión del retorno a lo largo de la serie. nb03 §1.

**volumen relativo (`vol_rel20`)** · `volumen del día ÷ promedio de volumen de los últimos 20 días`. Un valor de 1 significa "volumen igual al promedio reciente"; 2 significa "el doble".

**Welch (prueba t de Welch)** · Variante de la prueba t de dos muestras que no asume igualdad de varianzas. nb04 §2.4 la usa como prueba de referencia en P2 (bootstrap por empresa decide).

**XBRL** · Formato estándar en el que la autoridad de EE.UU. (SEC) obliga a publicar los estados financieros: cada cifra lleva una etiqueta (p. ej. `NetIncomeLoss`) que permite leerla por software y compararla entre empresas y entre reportes. En este proyecto se usa para construir la tabla trimestral y los ratios TTM (nb01 §3).

**XLP** · ETF sectorial de consumo defensivo (Consumer Staples Select Sector SPDR Fund). Representa "la industria" en P3 y P5. nb04 §3 y §6.

**z (retorno estandarizado)** · `retorno ÷ σ hacia atrás`. Expresa un retorno en "cuántas desviaciones estándar" es, usando una σ calculada solo con información anterior a `t` (para evitar look-ahead). nb03 §4.6.

---

### Convenciones usadas en todo el proyecto

- **"se rechaza H0" / "no se rechaza H0"**, nunca "se acepta H0" ni "la hipótesis queda apoyada".
- **Dos decisiones por prueba:** una estadística (IC frente al nulo) y una de negocio (límite inferior del IC frente al umbral fijado antes de ver los datos).
- **Horizontes:** P2 y P3 se evalúan a 3 años; P4 a N = 60 días hábiles.
- **Técnicas prohibidas por el filtro de MINE-4101:** no se usan ni se mencionan como herramienta las pruebas y modelos de econometría financiera no cubiertos en el curso.
