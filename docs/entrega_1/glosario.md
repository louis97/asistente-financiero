# Glosario (fuente única de definiciones)

Audiencia: un compañero del curso MINE-4101 sin formación en finanzas. Cada entrada se cuenta en 1–2 líneas con un ejemplo numérico tomado de las instantáneas en `data/snapshots/` o de los resultados `data/resultados/nb03.json`, `nb04.json` y `nb04_p4.json`. Los enlaces desde los notebooks apuntan a `docs/entrega_1/glosario.md`.

El orden es alfabético (los números y letras griegas se ordenan por su nombre: Δ como "delta", σ como "sigma"). Los sinónimos ("sesión turbulenta" ≡ "semana turbulenta"; "bootstrap por empresa" ≡ "bootstrap por ticker") se referencian entre sí.

---

**10-K** · Informe anual que las empresas que cotizan en EE.UU. presentan ante la SEC. Trae los estados financieros auditados del año fiscal. Ejemplo: el 10-K de KO del cierre 2025-12-31 se publicó el 2026-02-20 (ver `tabla_trimestral`, filas `origen = q4_derivado`).

**10-Q** · Informe trimestral de los primeros tres trimestres del año fiscal (el cuarto queda cubierto por el 10-K). Trae ingresos, utilidad y balance a esa fecha de corte. Ejemplo: el 10-Q de KO con `end = 2026-04-03` se publicó el 2026-04-30 (`filed`).

**acción** · Una fracción del capital de una empresa. Si una empresa tiene 1.000 acciones y uno posee 10, posee el 1 % de la empresa. En este proyecto cada "ticker" (KO, PEP, PG, …) es una acción distinta.

**acumulado del año (YTD, *year-to-date*)** · Suma de un flujo (ingresos, utilidad, caja operativa) desde el primer día del año fiscal hasta la fecha de corte del reporte. Ejemplo: en un 10-Q con `end = 30 de junio` el YTD cubre enero–junio.

**año fiscal (y cierre fiscal distinto de diciembre)** · Período de doce meses que cada empresa escoge para contar sus resultados. La mayoría usa enero–diciembre, pero algunas no: WMT y COST cierran su año fiscal en enero. nb02 §2b.5 marca estos casos para que al sumar cuatro trimestres se respete el año fiscal, no el calendario.

**AUC (*area under the ROC curve*)** · Mide qué tan bien un puntaje separa las dos clases de una etiqueta binaria (0/1). Toma valores de 0 a 1: 0,5 es azar y 1 es separación perfecta. Ejemplo: la línea base por decil de σ252 diaria del nb04 §4.5 tiene AUC = 0,591 en la prueba 2019–2024.

**Bonferroni** · Corrección por multiplicidad: cuando se hacen k pruebas se usa un nivel de confianza de 1 − α/k en cada una, para que la tasa global de falsos positivos siga siendo α. nb04 §5.3 usa 1 − 0,05/7 ≈ 99,3 % para los 7 indicadores de P4.

**bootstrap por bloques (de fechas)** · Técnica de remuestreo que respeta la dependencia temporal: se muestrean trozos consecutivos de fechas con reemplazo y se recalcula el estimado. El IC sale de los percentiles 2,5 y 97,5 de los estimados remuestreados. Ejemplo: P1 (nb03 §4.4) construye el IC de la tasa de caídas fuertes con bloques semanales.

**bootstrap por empresa (por grupos / por ticker)** · Remuestreo con reemplazo del listado de empresas (en vez de filas o bloques de tiempo). Se usa cuando una empresa aporta varias filas y lo que varía entre empresas es lo que domina el IC. Ejemplo: P2 (nb04 §2.6) remuestra las 21 empresas (menos las excluidas por falta de EPS); "bootstrap por empresa" y "bootstrap por ticker" son el mismo concepto.

**BVPS (*book value per share*, valor en libros por acción)** · `patrimonio ÷ acciones`. Es el patrimonio contable que corresponde a cada acción. Ejemplo: KO 2026-04-03 tiene `bvps = 7,80` USD por acción (`ratios_ttm`).

**canal Donchian** · Franja entre el máximo y el mínimo de los últimos N períodos. Se usa como indicador `donchian20`, que mide la posición del cierre dentro de ese canal (0 toca el mínimo, 1 toca el máximo). nb04 §5.

**caída máxima (drawdown)** · La peor pérdida acumulada desde un máximo histórico de la serie hasta el siguiente mínimo. Se expresa como fracción. Ejemplo: en nb03 §1 cada ticker tiene su `drawdown` máximo observado. Un drawdown de −0,30 significa que el precio llegó a estar un 30 % por debajo de su máximo anterior.

**censura** · Observación que no se puede resolver porque falta parte del futuro: la etiqueta "¿toca el nivel en 60 días?" queda vacía para los últimos 60 días hábiles de la muestra. Lección T3 del curso: una métrica se calcula solo sobre la población donde está definida; las filas censuradas no se mezclan con las completas.

**chi-cuadrado (tabla de contingencia)** · Prueba del curso para una tabla de dos variables categóricas: compara los conteos observados con los esperados bajo independencia. Se acompaña de la **V de Cramér** para medir la fuerza de la relación. nb03 §5 usa chi-cuadrado para P6 (semanal y diaria).

**clustermap** · Mapa de calor que ordena filas y columnas de una matriz (por ejemplo, de correlaciones) agrupando lo parecido con un dendrograma. Ejemplo: nb04 §6.6 muestra el clustermap de los 21 retornos semanales de la industria.

**decil** · Grupo que resulta de partir una variable en diez partes iguales por sus percentiles 10, 20, …, 90. El decil 1 es el 10 % más bajo y el 10 el 10 % más alto. nb04 §4.5 arma los deciles de σ252 diaria.

**decisión de negocio (regla accionable / efecto real, pero de magnitud incierta / no accionable)** · Se fija un umbral práctico antes de ver los datos. Después se mira el IC estimado: accionable si el límite inferior supera el umbral; "efecto real, pero de magnitud incierta" si se rechaza H0 pero el IC cruza el umbral; no accionable en los demás casos.

**decisión estadística ("se rechaza H0" / "no se rechaza H0")** · Convención del curso: solo se usan estas dos frases. Nunca "se acepta H0" ni "la hipótesis queda apoyada". La decisión sale del IC frente al valor del nulo (el α del curso es 0,05).

**deuda/patrimonio** · Cuánta deuda financiera tiene la empresa frente a su patrimonio. Si el patrimonio vale 100 y la deuda de largo plazo 60, la razón vale 0,60. Ejemplo: KO 2026-04-03, `deuda_patrimonio = 1,16` (`ratios_ttm`).

**día hábil** · Día en que la bolsa opera (lunes a viernes, sin feriados de EE.UU.). nb04 §4 usa días hábiles para contar horizontes diarios; N = 60 días es un trimestre bursátil.

**distancia a la media (`dist_sma20`, `dist_sma50`, `dist_sma200`)** · `precio ÷ media móvil − 1`. Mide qué tan por encima o por debajo de su promedio reciente está el precio. 0 significa "sobre la media"; 0,10 significa "10 % por encima de su media de 20 días". nb04 §5.

**drawdown** · Ver "caída máxima".

**ΔAUC** · Diferencia entre el AUC de un modelo que agrega un indicador y el AUC de la línea base (sin ese indicador). Mide cuánto aporta el indicador. P4 fija el umbral en 0,01. Ejemplo: `rsi14` tiene ΔAUC = −0,008 (no accionable; nb04_p4.json).

**ΔR²** · Diferencia entre el R² de una regresión con una variable extra y el R² de la regresión sin ella. Mide la mejora de ajuste. ΔR² nunca es negativo si se agregan regresores (`sumas de cuadrados anidadas`), por eso se usa como medida de aporte en P5.

**Δlog(P/E normalizado)** · Cambio del logaritmo del P/E normalizado en un horizonte (3 años). Se descompone en `Δlog(precio) − Δlog(EPS promedio)`: separa cuánto del cambio vino del precio y cuánto de las utilidades. La suma es exacta porque el log convierte el cociente en una resta.

**EPS (*earnings per share*, utilidad por acción)** · `utilidad neta ÷ acciones diluidas`. Es la utilidad que corresponde a cada acción. Ejemplo: KO 2026-04-03, `eps_ttm = 3,18` USD por acción (`ratios_ttm`).

**EPS TTM (de los últimos 12 meses)** · Suma del EPS de los cuatro trimestres más recientes ya publicados. Resume la utilidad del último año, actualizándose cada trimestre. nb01 §4.3. Ejemplo: KO 2026-04-03 con `eps_ttm = 3,18` suma los cuatro trimestres 2025Q3 → 2026Q1.

**ETF (*exchange-traded fund*)** · Fondo que agrupa muchas acciones y se compra como una sola. Replica una canasta (un índice). En el proyecto se usan dos: el SPY y el XLP.

**ETF sectorial (XLP)** · ETF que agrupa las empresas de consumo defensivo de EE.UU. (Consumer Staples Select Sector SPDR Fund). nb03 y nb04 lo usan como "la industria" para P3 y P5.

**etiqueta de entrada ("toca el nivel")** · Variable binaria del nb04 §4: vale 1 si el precio cae a `close × (1 − k·σ252)` dentro de los siguientes N días hábiles, y 0 si en esos N días sube a `close × (1 + k·σ252)` o se agota el tiempo. k = 1 y N = 60 en nb04. Las últimas N observaciones quedan censuradas.

**exceso sobre el XLP** · Para P3, retorno logarítmico de la empresa menos retorno logarítmico del XLP sobre el mismo horizonte: `log(P_T/P_0) − log(XLP_T/XLP_0)`. Un exceso positivo significa que la empresa superó al sector; uno negativo, que quedó por debajo.

**filed (fecha de publicación)** · Fecha en que un reporte de EDGAR se hizo público. Es la primera fecha en que un inversor pudo usar esa información. Toda unión con precios se hace por `filed` para evitar look-ahead (lección T6). Ejemplo: `tabla_trimestral` fila 2023Q1 de KO tiene `filed = 2023-04-26` (26 días después del cierre del trimestre).

**frecuencia diaria y semanal** · Dos resoluciones de precios: `precios_diarios` tiene una fila por día hábil; `precios_semanales` una fila por lunes de la semana. nb03 maneja P1 en semanal y P6 en diaria y semanal.

**H0 / H1** · H0 es la hipótesis nula (el "no hay efecto" o el valor de referencia). H1 es la hipótesis alternativa. Se escribe la dirección de H1 antes de ver los datos y no se cambia. Ejemplo P1: H0 `p ≤ 2,55 %`, H1 `p > 2,55 %` (nb03 §4.2).

**Holm** · Corrección por multiplicidad "paso a paso": ordena los p-values de k pruebas y las compara con α/k, α/(k−1), …, α. Es menos conservadora que Bonferroni. Se reporta como sensibilidad sobre las 13 pruebas con decisión de negocio (nb04 §8).

**horizonte de valor (3 años)** · Ventana de evaluación de P2 y P3: se compara el P/E normalizado o el exceso sobre el XLP entre `t` y `t + 3 años`. 3 años es el horizonte típico que declara el inversor value en la ideación.

**indicador técnico** · Variable derivada solo de precios y volumen históricos (sin información fundamental). nb04 §5 estudia siete: `rsi14`, `dist_sma20`, `dist_sma50`, `dist_sma200`, `vol_rel20`, `donchian20`, `mom_12_1`. Todos miran solo hacia atrás.

**industria piloto (consumo defensivo)** · Las 21 empresas de consumo defensivo con historia desde 2009 y en el XLP (KO, PEP, PG, WMT, COST, CL, MDLZ, KMB, GIS, MO, PM, HSY, KR, SYY, ADM, CLX, CHD, MKC, STZ, CAG, TSN). KHC queda fuera porque sus precios comienzan en 2015. Se analiza esta industria para la entrega 1; el producto se diseñó para cualquier industria.

**intervalo de confianza (IC)** · Rango de valores plausibles para un parámetro, con un nivel de confianza fijado (95 % en el proyecto). Ejemplo P1: IC = [0,0246; 0,0392] para la tasa de caídas fuertes (nb03.json). "El 95 %" se refiere al procedimiento, no a la probabilidad del parámetro.

**línea base por decil de σ** · Puntaje que ordena las observaciones por su decil de σ252 diaria y toma el decil como predictor. Es la referencia contra la que se compara cada indicador en P4. Ejemplo: su AUC en la prueba es 0,591 (`nb04_p4.json`).

**log-retorno** · `log(P_t / P_{t−1})`. Es el retorno expresado en logaritmo natural. Se suma a través del tiempo: el log-retorno de dos períodos es la suma de los dos log-retornos. Base de P1, P5 y la volatilidad.

**look-ahead** · Error de usar información del futuro al tomar una decisión en `t`. En este proyecto se evita con `shift(1)`, ventanas expansivas y la fecha `filed`. La etiqueta es lo único que mira al futuro. Lección T6.

**Mann-Whitney (prueba U)** · Prueba del curso que compara dos muestras independientes por su mediana (en realidad, por su rango). No supone normalidad. Se complementa con bootstrap porque las observaciones no son independientes.

**margen operativo** · `utilidad operativa ÷ ingresos`. Qué fracción de las ventas queda después de los costos y gastos del negocio (antes de intereses e impuestos). Ejemplo: KO 2026-04-03, `margen_operativo_ttm = 0,29` (29 %).

**MDE (diferencia mínima detectable) / potencia** · El MDE es el efecto más pequeño que una prueba podría detectar con la potencia pedida (80 % en el curso) dado el tamaño muestral y la varianza observada. Si el umbral de negocio queda por debajo del MDE, la prueba está "corta": no sabría distinguir un efecto accionable del nulo. nb04 §2.5 y §3.3 lo calculan antes de estimar.

**media móvil** · Promedio del precio de los últimos n períodos. La "simple" (SMA) le da el mismo peso a cada observación. Es la base de los indicadores `dist_sma20`, `dist_sma50`, `dist_sma200`.

**momentum 12-1 (`mom_12_1`)** · `precio_{t−21} / precio_{t−252} − 1`. Mide el retorno de los últimos 12 meses, saltándose el último mes para separar el efecto "momentum" del "reversión de corto plazo". nb04 §5.

**N = 60 días (horizonte de la etiqueta)** · Cuántos días hábiles hacia adelante mira la etiqueta de P4 para decidir si el precio "toca el nivel". N = 60 (≈ 3 meses bursátiles) se eligió en nb04 §4.3 maximizando AUC entre los candidatos cuya tasa de toque cae en 10–40 %.

**nivel de entrada** · Precio por debajo del precio actual que el usuario fijaría como oportunidad de compra. En el producto son 3 niveles de entrada por acción.

**nivel de salida** · Precio por encima del precio actual que el usuario fijaría como oportunidad de venta. En el producto son 3 niveles de salida por acción, todos por encima del precio actual.

**nulo calibrado por simulación** · Valor de referencia que se calcula remuestreando los retornos observados bajo "no hay efecto". Fija el nulo con los mismos datos y preserva la cola. nb03 §4.1 lo usa para P1: calibra la tasa esperada de caídas fuertes bajo caminata aleatoria. Resultado: 2,55 %.

**p bilateral equivalente** · Cuando una prueba se reporta por el IC, el p-value se calcula bilateralmente a partir de las réplicas del bootstrap, aunque H1 sea unilateral. Es solo informativo (la decisión viene del IC). nb04 §3.5.

**p bootstrap** · Fracción de las réplicas del bootstrap cuya estimación quedó al menos tan lejos del nulo como la observada. Ejemplo: P1 tiene `p_boot = 0,049` (nb03.json); P2 tiene `p_boot ≈ 0,001` (nb04.json).

**P/B (*price-to-book*)** · `precio ÷ BVPS`. Múltiplo que compara el precio con el patrimonio contable por acción. P/B = 1 significa "pago el patrimonio exactamente". nb04 §1.

**P/E (*price-to-earnings*)** · `precio ÷ EPS`. Múltiplo que indica cuántas unidades de precio se pagan por cada unidad de utilidad. El P/E "actual" usa el EPS TTM. Ejemplo: KO 2026-10-12 con `close = 92,00` USD y `eps_ttm = 3,18` tiene P/E actual ≈ 29.

**P/E normalizado** · `precio ÷ EPS promedio de los últimos 3 años` (12 trimestres ya publicados; variable `eps_prom_3a` del `ratios_ttm`). Un solo año excepcional puede hacer que una acción parezca barata sin serlo; promediar varios años evita esa ilusión. Ejemplo: KO 2026-10-12 con `eps_prom_3a = 2,73` tiene P/E normalizado ≈ 33,8, por encima del P/E actual. Referencias: Graham y Dodd (1934), *Security Analysis*, McGraw-Hill; Campbell y Shiller (1998), *Journal of Portfolio Management*, 24(2), 11–26, DOI 10.3905/jpm.24.2.11.

**PCA (análisis de componentes principales)** · Técnica no supervisada que proyecta variables correlacionadas en pocos ejes ortogonales ordenados por varianza explicada. En nb04 §6.6 el PC1 de los 21 retornos semanales se interpreta como "el movimiento común de la industria".

**percentil** · Valor por debajo del cual queda cierta fracción de la muestra. El percentil 5 es el valor que deja el 5 % más bajo por debajo. nb03 §2.

**percentil 5 (del retorno)** · Valor del percentil 5 de la distribución de retornos. Si el p5 del retorno semanal de KO es −4 %, significa que una de cada 20 semanas KO cae al menos 4 %.

**percentil expansivo** · Percentil de un valor dentro de su propia historia hasta `t`: usa todas las observaciones de la misma empresa anteriores a `t`. Se calcula con ventana expansiva (`shift(1)` previo) para evitar look-ahead. nb04 §1.

**prueba F de modelos anidados** · Compara el R² de dos regresiones donde una incluye a la otra (anidadas). Dice si las variables extra aportan información significativa. nb04 §6.3 (P5).

**Q4 derivado** · El cuarto trimestre no se reporta como 10-Q; se obtiene restando al 10-K anual los tres trimestres anteriores del mismo año fiscal. El `filed` queda en la fecha del 10-K (nb01 §4.1; `origen = q4_derivado` en `tabla_trimestral`).

**quintil** · Grupo que resulta de partir una variable en cinco partes iguales por sus percentiles 20, 40, 60, 80. En el proyecto se usa "quintil barato" (percentil ≤ 20 %) y "quintil caro" (percentil > 80 %). nb04 §2.3.

**quintil por fecha** · Clasificación en quintiles que se recalcula en cada fecha trimestral y usa solo las empresas con dato en esa fecha. Evita el look-ahead (no se usa la distribución futura).

**R²** · Fracción de la variación de la variable respuesta que explica una regresión. Va de 0 a 1. nb04 §6.3 (P5).

**regresión a la media** · Fenómeno estadístico: una medición extrema con parte de azar tiende a quedar menos extrema en la siguiente medición. No es una "fuerza"; es el efecto de que el azar se promedia. Lección E4 del curso: lenguaje de asociación, no de causa.

**retorno** · Cambio relativo del precio. En este proyecto se usa el **retorno simple** `P_t / P_{t−1} − 1` para la comunicación y el **log-retorno** `log(P_t / P_{t−1})` para los cálculos (porque se suma a través del tiempo).

**retorno simple** · `P_t / P_{t−1} − 1`. 0,05 significa "subió 5 %"; −0,05 significa "cayó 5 %".

**reexpresión** · Un reporte posterior modifica cifras ya publicadas. En este proyecto se usa la **primera publicación** (fecha `filed` original) para no incorporar información que no estaba disponible en `t`. nb02 §3.

**reversión a la normal** · Cuando un múltiplo (por ejemplo, el P/E normalizado) se aleja mucho de su nivel habitual, tiende a volver a él con el tiempo. Es la lectura que motiva a P2: si está barato frente a su historia, el mercado puede corregir hacia arriba. Se explica sin modelos econométricos.

**ROE (*return on equity*, rentabilidad del patrimonio)** · `utilidad neta ÷ patrimonio`. Qué fracción del patrimonio contable se ganó en el año. Ejemplo: KO 2026-04-03, `roe_ttm = 0,41` (41 %).

**RSI (*relative strength index*)** · Indicador técnico entre 0 y 100 que mide la fuerza de las variaciones positivas frente a las negativas en una ventana (14 días en el proyecto). Valores altos (>70) sugieren sobrecompra; bajos (<30), sobreventa. nb04 §5.

**semana turbulenta** · Semana en que `|retorno| > σ252 diaria` (umbral del curso). Se usa en la variante semanal de P6 (nb03 §5). Sinónimo semanal de la "sesión turbulenta".

**sesgo de supervivencia** · Analizar solo las empresas que sobrevivieron hasta hoy puede sobreestimar los retornos: las que quebraron o fueron deslistadas quedan fuera de la muestra. Es más relevante en horizontes largos (3 años). nb02 §6.

**sesión turbulenta** · Sesión bursátil (día) en que `|retorno diario| > σ252 diaria`. P6 (diaria) estudia la probabilidad de que una sesión turbulenta venga seguida por otra (nb03 §5). Es la variante diaria de la "semana turbulenta".

**σ20 diaria** · Desviación estándar de los retornos diarios de las últimas 20 sesiones (un mes bursátil). nb04 §4.

**σ252 diaria (volatilidad anualizada)** · Desviación estándar de los retornos diarios de las últimas 252 sesiones (un año bursátil). nb03 §0 y nb04 §4.

**σ20/σ252** · Razón `σ20 diaria ÷ σ252 diaria`. Capta la aceleración o calma relativa de la volatilidad. Es una de las tres variables del "modelo A" (la línea base de magnitud) de nb04 §5.

**solapamiento de ventanas** · Dos observaciones de la misma empresa en fechas cercanas comparten parte del horizonte futuro. Hace que las observaciones no sean independientes. Se mitiga con submuestras sin solapamiento (una fila cada N días) y con IC por bloques o por empresa.

**Spearman (correlación de rangos)** · Mide asociación monótona (no lineal necesariamente): se calcula sobre los rangos de las dos variables. Robusta a atípicos. nb04 §5.8 y §6.6.

**split** · Partición de una acción en varias nuevas sin cambiar el valor total de la empresa. Un split 2:1 duplica el número de acciones y divide el precio en 2. El `close` de yfinance ya viene ajustado por splits y dividendos. Ejemplo: KO tuvo splits 2:1 el 1965-02-19, 1968-06-03, 1977-06-01, 1986-07-01, 1990-05-14, 1992-05-18, 1996-05-13, 2012-08-13 y 3:1 el 1977-06-01 (`splits.parquet`).

**splits (instantánea `splits.parquet`)** · Tabla con los eventos de split por ticker: `ticker`, `fecha` y `ratio`. Se descarga para auditar la trazabilidad del precio ajustado.

**SPY** · ETF que replica al S&P 500. En el proyecto representa "el mercado" en el sentido del curso: el referente de los retornos del universo accionario estadounidense. nb04 §6 (P5).

**submuestra sin solapamiento** · De la tabla diaria se toma una fila cada N días hábiles (misma fecha para todas las acciones). Reduce la dependencia entre observaciones. nb04 §5.2.

**tasa de toque** · Fracción de observaciones con etiqueta `y = 1`. Es la tasa a la que, en los datos, el precio tocó el nivel inferior antes del superior o del tiempo. nb04 §4.5.

**tercil** · Grupo que resulta de partir una variable en tres partes iguales por sus percentiles 33 y 67.

**trampa de valor** · Una acción se ve barata (P/E bajo) porque el mercado anticipa que sus utilidades van a caer. Si uno compra pensando "está barata" sin mirar las utilidades, el P/E se puede corregir hacia la media bajando el precio, no subiendo el EPS. nb04 §3.8 testea este patrón.

**TTM (últimos 12 meses, *trailing twelve months*)** · Suma de los cuatro trimestres más recientes ya publicados. Da una lectura "siempre al día" sin esperar al cierre del año fiscal. nb01 §4.3.

**V de Cramér** · Medida del tamaño del efecto de una tabla de contingencia (va de 0 a 1). Acompaña a la prueba chi-cuadrado para expresar la magnitud de la asociación en una unidad interpretable. nb03 §5.4.

**VIF (*variance inflation factor*)** · Diagnóstico de multicolinealidad en regresión múltiple: cuánto se infla la varianza del coeficiente de una variable por su correlación con las demás. VIF > 10 suele considerarse problemático. nb04 §6.3.

**volatilidad** · Dispersión de los retornos; se mide con la desviación estándar. Cuando se calcula sobre los retornos diarios de un año (252 sesiones) se habla de **volatilidad anualizada** o `σ252 diaria`.

**volatilidad móvil** · Volatilidad calculada en una ventana que se desplaza en el tiempo (por ejemplo, los últimos 20 o 252 días). Mide cómo cambia la dispersión del retorno a lo largo de la serie. nb03 §1.

**volumen relativo (`vol_rel20`)** · `volumen del día ÷ promedio de volumen de los últimos 20 días`. Un valor de 1 significa "volumen igual al promedio reciente"; 2 significa "el doble".

**Welch (prueba t de Welch)** · Variante de la prueba t de dos muestras que no asume igualdad de varianzas. nb04 §2.4 la usa como prueba de referencia en P2 (bootstrap por empresa decide).

**XLP** · ETF sectorial de consumo defensivo (Consumer Staples Select Sector SPDR Fund). Representa "la industria" en P3 y P5. nb04 §3 y §6.

**z (retorno estandarizado)** · `retorno ÷ σ hacia atrás`. Expresa un retorno en "cuántas desviaciones estándar" es, usando una σ calculada solo con información anterior a `t` (para evitar look-ahead). nb03 §4.6.

---

### Convenciones del curso usadas en todo el proyecto

- **"se rechaza H0" / "no se rechaza H0"**, nunca "se acepta H0" ni "la hipótesis queda apoyada".
- **Dos decisiones por prueba:** una estadística (IC frente al nulo) y una de negocio (límite inferior del IC frente al umbral fijado antes de ver los datos).
- **Horizontes:** P2 y P3 se evalúan a 3 años; P4 a N = 60 días hábiles.
- **Técnicas prohibidas por el filtro de MINE-4101:** no se usan ni se mencionan como herramienta las pruebas y modelos de econometría financiera no cubiertos en el curso.
