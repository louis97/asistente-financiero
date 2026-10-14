# Punto 4. Enfoque analítico

*Asistente bursátil para el inversor value colombiano. Entrega 1, MINE-4101 Ciencia de Datos Aplicada (Universidad de los Andes). Autor: Louis Gualtero.*

Este documento traduce las tres preguntas de negocio del producto ([02_ideacion.md](02_ideacion.md)) en hipótesis que se pueden refutar con los datos, asigna a cada una la técnica que la responde y la sección del EDA donde se aborda, define el diseño experimental que evita el look-ahead y fija, para cada métrica de calidad, la regla con la que se decide si la hipótesis se apoya. El mapa completo de hipótesis está en `docs/hipotesis.md`. Todo se formula como asociación y no como causa. Lo que aquí se describe es un plan: los resultados del EDA se reportan en los notebooks `02_calidad`, `03_eda_series` y `04_eda_relaciones`, y en este documento solo se citan los que motivaron una decisión de diseño (secciones 4.3.2 y 4.3.4), con la referencia al notebook de donde salen.

## 4.1 De las preguntas de negocio a las hipótesis

El inversor value necesita responder tres preguntas para cada nivel de su plan. La primera es si el nivel es razonable para esta empresa, y la responde el eje fundamental comparativo (HF). La segunda es si compra ya o espera, y la responde el eje técnico (HT), cuyo rival es la caminata aleatoria. La tercera es qué tan probable es alcanzar el nivel y en cuánto tiempo, y la responde el eje probabilístico (HP). La caminata aleatoria (eficiencia débil, Fama, 1970) no es una hipótesis transversal. Dice que los precios pasados no predicen la dirección futura, pero no dice nada de la volatilidad ni de los fundamentales. Por eso es la línea base a vencer en el eje técnico (HT0), el supuesto que se verifica en el probabilístico (HP0) y no aplica al fundamental.

Las siete hipótesis principales se formulan con H0 y H1, una variable medible, un horizonte y una referencia. Un rechazo de H0 en una serie de tiempo debe leerse con cautela, porque las observaciones no son independientes, y por eso las pruebas que suponen i.i.d. se complementan con block bootstrap (sección 4.3). Todas las pruebas se corren por ticker y se resumen por industria. El nivel de significancia nominal es 0,05, con corrección por comparaciones múltiples (Benjamini-Hochberg) al resumir los 30 tickers.

| Pregunta | ID | H0 | H1 | Variable medible y horizonte | Referencias |
|---|---|---|---|---|---|
| ¿Compro ya o espero? | HT0 | Los log-precios semanales siguen una caminata aleatoria: raíz unitaria (ADF no rechaza) y retornos sin autocorrelación (ρ₁ = … = ρ_K = 0) | Los log-precios son estacionarios en tendencia o los retornos están autocorrelacionados | Log-precios y retornos semanales por ticker, ~15 años; K = 10 rezagos. Además, P_GBM(toque) frente a la tasa empírica de toque de la barrera | Fama (1970) |
| ¿Compro ya o espero? | HT1 | AUC_SVM − AUC_GBM ≤ 0 | AUC_SVM − AUC_GBM > 0 (y análogamente Brier_GBM − Brier_SVM > 0) | Probabilidad de que el precio toque el nivel de entrada (k·σ por debajo) en N semanas antes de la barrera superior, con N ∈ {4, 12, 26}; validación walk-forward | Kim (2003); Lo, Mamaysky y Wang (2000); López de Prado (2018) |
| ¿Compro ya o espero? | HT2 | Cada indicador tiene la misma distribución en las dos clases de la etiqueta (AUC univariada = 0,5) | La distribución difiere: RSI alto, distancia grande a la SMA/EMA o techo del canal Donchian se asocian con mayor probabilidad de retroceso (AUC ≠ 0,5, con signo esperado) | RSI(14), distancia a SMA/EMA, posición Donchian, volumen relativo y momentum 12-1 frente a la etiqueta de triple barrera, N ∈ {4, 12, 26} | Park e Irwin (2007); Jegadeesh (1990) |
| ¿Es razonable el nivel? | HF1 | El múltiplo (P/E, P/B) tiene raíz unitaria: velocidad de reversión η = 0 | El múltiplo revierte a su media histórica: η > 0 con vida media ln 2/η finita | Serie trimestral del múltiplo por empresa (EDGAR con `filed` + precio), desde ~2009; ajuste Ornstein-Uhlenbeck (AR(1)) | Dixit y Pindyck (1994) |
| ¿Es razonable el nivel? | HF2 | El múltiplo relativo (empresa ÷ mediana de la industria) tiene raíz unitaria: η = 0 | El múltiplo relativo revierte: η > 0, es decir, los descuentos frente al sector tienden a cerrarse | Serie trimestral del múltiplo relativo por empresa | Asness, Moskowitz y Pedersen (2013) |
| ¿Qué tan probable es el objetivo? | HP0 | Los retornos semanales son normales sin efectos ARCH: ACF de r² nula, ARCH-LM no rechaza y la normalidad no se rechaza | Hay colas pesadas o agrupamiento de volatilidad, y el GBM normal no es adecuado (se pasa a GARCH-t) | Retornos semanales por ticker, ventana expansiva; ACF de r y r², ARCH-LM, Jarque-Bera con QQ-plot, persistencia α + β | Cont (2001); Engle (1982) |
| ¿Qué tan probable es el objetivo? | HP3 | β del ETF sectorial = 0 en el modelo de índice único (R² = 0) | β > 0 y el ETF explica una parte importante de la varianza de la acción | R² y β de r = α + β·r_ETF + ε, móvil y por régimen; descomposición de la varianza en sistemática e idiosincrática | Sharpe (1964) |

Las hipótesis secundarias reciben un análisis más ligero y se enuncian brevemente. HT3: la relación indicador → etiqueta es estable entre regímenes de mercado (HT2 repetida por régimen; Ang y Timmermann, 2012). HT4: la volatilidad semanal se agrupa, por lo que las barreras deben escalarse con σ (ARCH-LM y persistencia del GARCH; Engle, 1982; Bollerslev, 1986). HF3: estar barata frente a la historia y la industria, con calidad (ROIC o ROE sobre la industria), se asocia con mejores retornos a 12 meses (retorno posterior por quintil con `filed`; Fama y French, 1992; Piotroski, 2000), con muestra pequeña y carácter exploratorio. HF4: menor distancia al default de Merton se asocia con mayor drawdown o VaR posterior (Merton, 1974). HF5: los ratios calculados desde EDGAR son consistentes con yfinance, con Damodaran y con el 10-K, lo cual valida la fuente. HP1: el GBM normal subestima las colas y GARCH-t describe mejor el riesgo (Cont, 2001; Kupiec, 1995; Christoffersen, 1998). HP2: las probabilidades del Monte Carlo están calibradas frente a niveles históricos (Glasserman, 2004; López de Prado, 2018). HP1 y HP2 se preparan en esta entrega y su prueba completa requiere simular o entrenar.

## 4.2 Matriz hipótesis × técnica × sección del EDA

Cada técnica de la tabla responde a al menos una hipótesis, y ninguna se lista sin una pregunta que la justifique. Los niveles 1 a 3 son los del EDA de series de tiempo (punto 6): el nivel 1 analiza cada serie, el nivel 2 relaciona indicadores con la etiqueta y el nivel 3 estudia las relaciones entre activos y el análisis multivariado. Las hipótesis marcadas como "preparada" solo se resuelven del todo al entrenar o simular el modelo en la entrega final.

| Hipótesis | Técnica estadística | Visualización | ML o simulación | Dónde se aborda | Estado esperado en la Entrega 1 |
|---|---|---|---|---|---|
| HT0 | ADF y KPSS sobre log-precios y sobre cada indicador; Ljung-Box sobre retornos | Series de precio y retorno, ACF de r, curva de calibración de P_GBM frente a la tasa empírica de toque | Probabilidad GBM como línea base | `03_eda_series` (nivel 1) y `04_eda_relaciones` (nivel 2, calibración) | Respondida |
| HT1 | Intervalo bootstrap para ΔAUC y ΔBrier | Curvas ROC y diagrama de calibración (SVM frente a GBM) | SVM lineal y RBF con escalado; walk-forward con purga y embargo; coeficientes y SHAP | Diseño en 4.3; chequeo exploratorio opcional en `04_eda_relaciones` | Preparada (línea base GBM y etiquetas listas) |
| HT2 | AUC univariada, información mutua, Mann-Whitney con block bootstrap, Spearman y VIF para redundancias | Boxplots por clase, heatmap de correlaciones | Etiqueta de triple barrera para k ∈ {1, 2}σ y N ∈ {4, 12, 26} | `04_eda_relaciones` (nivel 2) | Respondida |
| HT3 (secundaria) | HT2 repetida por régimen | Boxplots y balance de clases por régimen | — | `04_eda_relaciones` (nivel 3) | Respondida de forma ligera |
| HT4 (secundaria) | ARCH-LM, persistencia α + β del GARCH(1,1) | ACF de r², volatilidad móvil | EWMA y GARCH(1,1) con ventana expansiva | `03_eda_series` (nivel 1) | Respondida |
| HF1 | ADF sobre el múltiplo; ajuste OU (η, nivel m, vida media) | Series de múltiplos con su media y percentiles | — | `03_eda_series` (nivel 1) | Respondida |
| HF2 | ADF y ajuste OU sobre el múltiplo relativo | Percentiles en la historia y en la industria a lo largo del tiempo | — | `04_eda_relaciones` (nivel 3) | Respondida |
| HF3 (secundaria) | Retorno posterior por quintil con `filed`, Spearman, bootstrap | Barras por quintil | — | `04_eda_relaciones` (nivel 3), exploratorio | Exploratoria |
| HF4 (secundaria) | Correlación entre d₂ y el drawdown o VaR posterior | Merton d₂ en el tiempo por industria | Distancia al default de Merton | `04_eda_relaciones` (nivel 3) | Exploratoria |
| HF5 (secundaria) | Diferencias relativas por ratio; coincidencia con el 10-K en 2 o 3 empresas | Tabla de auditoría | — | `02_calidad` | Respondida |
| HP0 | ACF de r y r², Ljung-Box, ARCH-LM, Jarque-Bera, ajuste normal y t | QQ-plot (acompaña siempre a Jarque-Bera), histogramas | GARCH(1,1) con ventana expansiva | `03_eda_series` (nivel 1) | Respondida |
| HP1 (secundaria) | Jarque-Bera con QQ-plot, normal frente a t; Kupiec y Christoffersen (backtesting, de recorte) | QQ-plot | GARCH-t | `03_eda_series` (nivel 1) | Parcial; backtesting preparado |
| HP2 (secundaria) | Brier y calibración por niveles ±k·σ | Diagrama de calibración | Monte Carlo walk-forward | Entrega final | Preparada |
| HP3 | R² y β móvil del modelo de índice único; descomposición de la varianza | Clustermap de correlaciones, β móvil, retornos acumulados por industria | Modelo de índice único | `04_eda_relaciones` (nivel 3) | Respondida |

Tres técnicas del EDA no responden a una hipótesis de forma directa y se justifican como apoyo. La descomposición STL del precio mensual y el PCA de los indicadores técnicos informan la redundancia y el comportamiento de las variables que alimentan HT1 y HT2, y la tabla de auditoría de `02_calidad` valida los datos que usan todas las hipótesis. Quedan fuera de esta entrega el exponente de Hurst y, si falta tiempo, el backtesting de VaR y HF3 y HF4.

## 4.3 Diseño experimental

### 4.3.1 La etiqueta

La etiqueta es una triple barrera solo-largo (López de Prado, 2018) construida sobre las series semanales de precio ajustado. Para cada semana t se fijan tres barreras. La barrera inferior es el nivel de entrada, ubicado k·σ_t por debajo del precio, y la barrera superior marca el escape hacia arriba, ubicada k·σ_t por encima. La barrera vertical es el horizonte de N semanas. La etiqueta vale 1 si el precio toca la barrera inferior antes que la superior y dentro del horizonte, y 0 si primero toca la superior o se agota el tiempo. Como σ_t es una volatilidad semanal estimada solo con datos hasta t, las barreras se adaptan al régimen de volatilidad, lo que es coherente con HT4. La escala exacta de σ_t al horizonte N queda documentada en el notebook junto con la tabla de decisión.

Los valores de k y N no se fijan a priori sino que se eligen en el EDA (`04_eda_relaciones`, nivel 2) entre k ∈ {1, 2}σ y N ∈ {4, 12, 26} semanas. La decisión se apoya en el balance de clases (que la clase positiva no sea demasiado rara), en la autocorrelación de la etiqueta y en el número de ventanas independientes, y en la literatura. No se usa el desempeño fuera de muestra del SVM para elegirlos, porque eso sería data snooping (Bailey et al., 2017). Como comparación se calculan dos etiquetas más: retorno > 0 y retorno > retorno del ETF sectorial.

Las últimas N semanas de cada serie no tienen la etiqueta resuelta (censura por la derecha). Se excluyen de entrenamiento y evaluación, y no se tratan como clase 0.

### 4.3.2 Variables del modelo

El SVM usa solo información de precios disponible en t, en tres grupos. El primero son los indicadores técnicos que quedaron tras el filtro de redundancia (VIF < 10) de `04_eda_relaciones`: `rsi14`, `dist_sma20`, `vol_rel20`, `donchian20` y `mom_12_1`. El segundo es la volatilidad condicional σ_t de la acción (EWMA y GARCH-t con ventana expansiva). El tercero son rasgos de régimen calculados hacia atrás: el drawdown acumulado del SPY desde su máximo y su volatilidad reciente. Los fundamentales no entran al modelo para que la lectura técnica sea independiente de la fundamental.

Los rasgos de volatilidad y régimen se incluyen por evidencia del EDA y no por suposición. Ningún indicador técnico separó las clases por sí solo (AUC univariada entre 0,496 y 0,514, HT2 no concluyente). En cambio, la tasa observada de la etiqueta baja de 20,6 % en el decil 1 de σ a 7,8 % en el decil 10, y la relación cambia entre regímenes (HT3). Esto concuerda con el agrupamiento de la volatilidad (Engle, 1982; Bollerslev, 1986; HT4 apoyada) y con la dependencia de los retornos del régimen de mercado (Ang y Timmermann, 2012). Los regímenes que el EDA definió con fechas (2008-09, COVID, 2022) se fijaron ex post y no se usan como variable, porque eso sería look-ahead. Se sustituyen por las medidas hacia atrás descritas arriba, cada una con una prueba de que su valor en t no cambia si se trunca la serie después de t.

Como σ_t entra al modelo, la línea base también la usa (4.3.4). Así, HT1 mide si los indicadores técnicos y el régimen aportan algo más allá de la volatilidad, y no solo si el SVM redescubre que σ importa.

### 4.3.3 Validación walk-forward con purga y embargo

Los datos se dividen en el tiempo, nunca al azar. La validación es walk-forward con ventana expansiva: el modelo se entrena con todo lo observado hasta una fecha y se evalúa en el bloque siguiente, y el procedimiento se repite avanzando el bloque. Como cada etiqueta usa información de las N semanas siguientes, dos observaciones vecinas comparten ventana y la muestra efectiva es mucho menor que el número de filas. Por eso se aplican dos controles de López de Prado (2018). La purga elimina del entrenamiento toda observación cuya ventana de etiqueta [t, t + N] se solape con el bloque de prueba. El embargo descarta además una franja de semanas inmediatamente posterior al bloque de prueba (al menos N). Con varios tickers en el mismo modelo, la purga y el embargo se aplican por fecha para todos los tickers, porque los retornos de la misma semana están correlacionados entre acciones. Los hiperparámetros del SVM (C y, para el RBF, γ) se eligen con una validación temporal anidada dentro del tramo de entrenamiento. Se reserva un tramo final que no se usa para elegir k, N ni hiperparámetros, y se evalúa una sola vez.

### 4.3.4 Líneas base

Las cuatro líneas base son obligatorias y se evalúan con exactamente los mismos bloques, purgas y embargos que el SVM. La primera es la probabilidad GBM con la σ_t del mismo instante, que da la probabilidad teórica de tocar la barrera inferior antes que la superior en N semanas. Se usa con la deriva estimada solo con datos ≤ t, porque el EDA mostró que con μ = 0 sobreestima la tasa de toque en 9,5 pp y con deriva pasada solo en 0,8 pp (`04_eda_relaciones`, §3). Se complementa con la tasa empírica de toque por decil de σ_t, calculada con datos ≤ t: como σ_t es una variable del SVM, esta línea base mide cuánto aporta el modelo más allá de la volatilidad. La segunda es predecir siempre la clase mayoritaria. La tercera es la regresión logística con las mismas variables, que mide cuánto aporta el SVM frente a un modelo lineal simple. La cuarta es el momentum 12-1 (Jegadeesh, 1990) usado como puntaje de un solo indicador, que mide si un indicador clásico basta.

### 4.3.5 Cómo se evita el look-ahead y la fuga de información

La pregunta de control, por la lección T6 de la guía, es si el inversor tiene este dato hoy. La etiqueta es lo único que mira al futuro; todo lo demás se calcula con información disponible en t.

| Riesgo | Dónde aparece | Control |
|---|---|---|
| Fundamentales publicados después | Ratios y múltiplos con EDGAR | Se usa la fecha `filed` y no la de cierre del período; un valor solo existe desde que se publicó |
| Estadísticos de toda la muestra | Escalado, percentiles, medias de los múltiplos, parámetros OU, GARCH | Se calculan con ventana expansiva hasta t; el escalador se ajusta solo con el entrenamiento de cada bloque |
| Solape de ventanas de etiqueta | Entrenamiento y prueba contiguos | Purga y embargo (4.3.3) |
| Elegir k, N o hiperparámetros mirando la prueba | Selección de modelo | k y N se eligen en el EDA con balance de clases y literatura; los hiperparámetros con validación anidada; tramo final intocado |
| Etiquetas sin resolver | Últimas N semanas | Se excluyen (censura, T3) |
| Ventanas incompletas | Inicio de la serie (SMA200, GARCH) | Se descartan hasta completar la ventana |
| Mediana de industria | Múltiplo relativo | Se calcula con los pares disponibles en t, con datos ≤ t |
| Supervivencia | Universo de 30 empresas que existen hoy (Brown et al., 1992) | No se elimina: se documenta como limitación y los resultados se leen como condicionados a empresas sobrevivientes |

Esta lista es una especificación de diseño y no una afirmación de que los controles ya se hayan ejecutado; su cumplimiento se prueba con series sintéticas en los módulos de `src/` y se reporta en los notebooks.

## 4.4 Métricas de calidad y reglas de decisión

Cada métrica tiene una línea base y una regla escrita antes de ver los resultados. Los umbrales numéricos (0,05 de significancia, 50 % de los tickers, 0,30 de R², 0,95 de DSR) son convenciones fijadas a priori para este proyecto y no valores tomados de la literatura; si los datos muestran que son inadecuados se ajustan y el cambio se documenta. Todos los intervalos de confianza se estiman con block bootstrap (Politis y Romano, 1994), con bloques de al menos N semanas para respetar la dependencia de las ventanas de la etiqueta. Cada hipótesis termina en uno de cuatro estados: apoyada, no apoyada, no concluyente (el intervalo incluye el valor nulo) o preparada (solo se dejó lista la línea base).

| Hipótesis o ámbito | Métrica | Línea base | Regla de decisión |
|---|---|---|---|
| HT0 (caminata aleatoria) | ADF y KPSS sobre log-precios; Ljung-Box sobre retornos | — | Se apoya como línea base en un ticker si ADF no rechaza la raíz unitaria, KPSS rechaza la estacionariedad y Ljung-Box no rechaza al 5 %. Se apoya en general si esto ocurre en más de la mitad de los tickers de cada industria |
| HT0 (calibración de P_GBM) | Regresión logística de la etiqueta sobre logit(P_GBM): intercepto y pendiente | — | P_GBM está calibrada si el IC 95 % del intercepto incluye 0 y el de la pendiente incluye 1. Si no, el GBM es una línea base sesgada y se reporta el sesgo |
| HT1 | ΔAUC = AUC_SVM − AUC_GBM y ΔBrier = Brier_GBM − Brier_SVM, con IC bootstrap al 95 % | GBM | Se apoya si ΔAUC > 0 con IC que excluye 0 y ΔBrier > 0 con IC que excluye 0. Es no concluyente si algún IC incluye 0 y no apoyada si el IC de ΔAUC queda por debajo de 0. Se reporta además frente a la logística y al momentum 12-1 |
| HT1 (utilidad frente al azar) | Balanced accuracy, precision y recall del umbral de decisión, calibración | Clase mayoritaria | El SVM solo se considera útil si su balanced accuracy supera la del clasificador de clase mayoritaria (0,5 por construcción) con IC que excluye ese valor |
| HT2 | AUC univariada por indicador y Mann-Whitney con block bootstrap; información mutua | AUC = 0,5 | El indicador se asocia con la etiqueta si el IC bootstrap de la AUC excluye 0,5 y el p-valor ajustado (Benjamini-Hochberg) es menor que 0,05 en el sentido esperado. Una |AUC − 0,5| menor que 0,05 se reporta como asociación débil |
| HT3 (secundaria) | AUC univariada por régimen | AUC = 0,5 | La relación es estable si el signo de la asociación se mantiene en la mayoría de los regímenes con muestra suficiente |
| HF1 y HF2 | ADF sobre el múltiplo y sobre el múltiplo relativo; η y vida media ln 2/η del ajuste OU | Raíz unitaria (η = 0) | Revierte en una empresa si ADF rechaza al 5 % y η > 0 con vida media menor que la mitad de la historia disponible. Se apoya en general si ocurre en más de la mitad de las empresas de cada industria. Con unos 60 trimestres la potencia de ADF es baja, y se informa |
| HP0 | ACF de r y r², ARCH-LM, QQ-plot, persistencia α + β | GBM normal | El GBM normal es adecuado si ARCH-LM y Ljung-Box sobre r² no rechazan y el QQ-plot no muestra desviaciones en las colas. Si ARCH-LM rechaza en más de la mitad de los tickers, se pasa a GARCH-t. Jarque-Bera se reporta pero no decide por sí solo con n grande |
| HP1 (secundaria) | Kupiec y Christoffersen sobre las violaciones del VaR | GBM normal | El modelo es adecuado si no se rechaza la cobertura ni la independencia de las violaciones al 5 % |
| HP3 | R² y β (con IC 95 %) del modelo de índice único; parte sistemática de la varianza | R² = 0 | Se apoya si el IC de β excluye 0 y el R² mediano de cada industria es al menos 0,30. Se reporta por ticker y por régimen |
| Financieras (netas de 10 pb por operación) | Mejora del precio de entrada frente a comprar de inmediato, retorno, volatilidad, max drawdown y Deflated Sharpe Ratio (Bailey y López de Prado, 2014) | Comprar de inmediato | La mejora de entrada es positiva si el IC bootstrap de la diferencia media neta de costos excluye 0. Hay evidencia de valor si el DSR es al menos 0,95, que corrige por el número de configuraciones probadas |
| Por régimen de mercado | Todas las métricas anteriores en 2008-09, expansión, 2020, 2022 y el período reciente (Ang y Timmermann, 2012) | Mismas líneas base | HT1 se declara robusta solo si el signo de ΔAUC se mantiene en la mayoría de los regímenes; si depende de uno solo, se reporta como específica de ese régimen |

La métrica ΔAUC es una métrica del modelo y no un KPI de negocio del punto 1. Las métricas financieras no pueden evaluarse del todo en esta entrega, porque el SVM final es de la entrega siguiente; aquí se deja definido el procedimiento y, si sobra tiempo, se hace un chequeo exploratorio con un SVM lineal walk-forward, reportado como tal. Las explicaciones del modelo se obtienen con los coeficientes del SVM lineal y con SHAP (Lundberg y Lee, 2017).

## Referencias

Los DOI de los artículos se consultaron en Crossref el 13 de octubre de 2026 (título, revista y año coinciden). Los libros y el documento de arXiv no tienen DOI de artículo. Las referencias provienen de `docs/hipotesis.md` y de la spec.

- Ang, A., y Timmermann, A. (2012). Regime changes and financial markets. *Annual Review of Financial Economics*, 4, 313-337. https://doi.org/10.1146/annurev-financial-110311-101808
- Asness, C. S., Moskowitz, T. J., y Pedersen, L. H. (2013). Value and momentum everywhere. *The Journal of Finance*, 68(3), 929-985. https://doi.org/10.1111/jofi.12021
- Bailey, D. H., y López de Prado, M. (2014). The deflated Sharpe ratio. *The Journal of Portfolio Management*, 40(5), 94-107. https://doi.org/10.3905/jpm.2014.40.5.094
- Bailey, D. H., Borwein, J., López de Prado, M., y Zhu, Q. J. (2017). The probability of backtest overfitting. *The Journal of Computational Finance*, 20(4). https://doi.org/10.21314/JCF.2016.322
- Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327. https://doi.org/10.1016/0304-4076(86)90063-1
- Brown, S. J., Goetzmann, W., Ibbotson, R. G., y Ross, S. A. (1992). Survivorship bias in performance studies. *The Review of Financial Studies*, 5(4), 553-580. https://doi.org/10.1093/rfs/5.4.553
- Christoffersen, P. F. (1998). Evaluating interval forecasts. *International Economic Review*, 39(4), 841-862. https://doi.org/10.2307/2527341
- Christoffersen, P. F. (2012). *Elements of Financial Risk Management* (2.ª ed.). Academic Press. (Libro, sin DOI de artículo.)
- Cont, R. (2001). Empirical properties of asset returns: stylized facts and statistical issues. *Quantitative Finance*, 1(2), 223-236. https://doi.org/10.1080/713665670
- Dixit, A. K., y Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press. (Libro.)
- Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987-1007. https://doi.org/10.2307/1912773
- Fama, E. F. (1970). Efficient capital markets: a review of theory and empirical work. *The Journal of Finance*, 25(2), 383-417. https://doi.org/10.1111/j.1540-6261.1970.tb00518.x
- Fama, E. F., y French, K. R. (1992). The cross-section of expected stock returns. *The Journal of Finance*, 47(2), 427-465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x
- Glasserman, P. (2004). *Monte Carlo Methods in Financial Engineering*. Springer. https://doi.org/10.1007/978-0-387-21617-1
- Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *The Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- Kim, K. (2003). Financial time series forecasting using support vector machines. *Neurocomputing*, 55(1-2), 307-319. https://doi.org/10.1016/S0925-2312(03)00372-2
- Kupiec, P. H. (1995). Techniques for verifying the accuracy of risk measurement models. *The Journal of Derivatives*, 3(2), 73-84. https://doi.org/10.3905/jod.1995.407942
- Lo, A. W., Mamaysky, H., y Wang, J. (2000). Foundations of technical analysis: computational algorithms, statistical inference, and empirical implementation. *The Journal of Finance*, 55(4), 1705-1765. https://doi.org/10.1111/0022-1082.00265
- López de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley. (Libro.)
- Lundberg, S. M., y Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems 30*. arXiv:1705.07874.
- Merton, R. C. (1974). On the pricing of corporate debt: the risk structure of interest rates. *The Journal of Finance*, 29(2), 449-470. https://doi.org/10.1111/j.1540-6261.1974.tb03058.x
- Park, C.-H., y Irwin, S. H. (2007). What do we know about the profitability of technical analysis? *Journal of Economic Surveys*, 21(4), 786-826. https://doi.org/10.1111/j.1467-6419.2007.00519.x
- Piotroski, J. D. (2000). Value investing: the use of historical financial statement information to separate winners from losers. *Journal of Accounting Research*, 38 (suplemento), 1-41. https://doi.org/10.2307/2672906
- Politis, D. N., y Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313. https://doi.org/10.1080/01621459.1994.10476870
- Sharpe, W. F. (1964). Capital asset prices: a theory of market equilibrium under conditions of risk. *The Journal of Finance*, 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x
