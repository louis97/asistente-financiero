# Punto 4. Enfoque analítico

*Asistente bursátil para el inversor value colombiano. Entrega 1, MINE-4101 Ciencia de Datos Aplicada (Universidad de los Andes). Autor: Louis Gualtero.*

Este documento es la **fuente única** de las hipótesis del proyecto. Para cada pregunta de negocio del [punto 2](02_ideacion.md), define una sola hipótesis con la plantilla de inferencia (ver pasos abajo), su variable medible, su horizonte, su umbral práctico fijado antes de ver el resultado, la prueba estadística y la decisión. También recoge el diseño experimental que evita el [look-ahead](glosario.md) y las métricas con las que se juzga la calidad del modelo. **No se repiten aquí las cifras de los resultados;** esos viven en los notebooks [03](../../notebooks/03_eda_univariado.ipynb) y [04](../../notebooks/04_eda_multivariado.ipynb) y en el [punto 7](07_conclusiones.md).

**Plantilla de inferencia** (se aplica a cada hipótesis):

1. **Paso 0 — Umbral práctico:** una diferencia mínima que **cambiaría una decisión**, fijada antes de la prueba.
2. **[H0 / H1](glosario.md) y α:** se escribe la hipótesis nula explícita, la alternativa y el nivel de significancia (α = 0,05).
3. **Prueba y supuestos verificados:** la prueba estadística y la matriz de supuestos (supuesto → por qué importa → verificación ejecutada → resultado con cifras → qué se hace si falla).
4. **Estimación con [intervalo de confianza](glosario.md) antes del p-value:** el estimado puntual y su IC bilateral al 95 % por bootstrap ([por bloques de fechas](glosario.md) o [por empresa](glosario.md), según la estructura).
5. **Efecto con IC:** el tamaño del efecto reportado con su rango.
6. **Dos decisiones:**
   - **Estadística:** se escribe "se rechaza H0" si el IC95 bilateral no incluye el valor nulo; en caso contrario, "no se rechaza H0". Este IC95 bilateral equivale a una prueba unilateral al 2,5 % (porque el intervalo bilateral deja 2,5 % en cada cola). Nunca se dice "se acepta H0".
   - **De negocio:** el efecto es **accionable** si el **límite inferior del IC** supera el umbral práctico; si se rechaza H0 pero el IC **cruza** el umbral, el efecto se reporta como "**efecto real, pero de magnitud incierta**"; en los demás casos, "**no accionable**".
7. **Implicación para el inversor y limitaciones.**

**Lenguaje de asociación**, nunca de causa. Las observaciones de series de tiempo no son independientes, y eso lo arregla el bootstrap por bloques (o por empresa) en el paso 4, no un cambio de la prueba.

## §4.0 Por qué trabajamos con retornos y cada rama en su frecuencia

El inversor habla de precios, pero las técnicas aquí aplicadas suponen datos "parecidos entre sí" (que la media y la variabilidad sean estables) e independientes. Los precios de una acción crecen y la variabilidad cambia por épocas, de modo que las fórmulas se calculan pero sus resultados mienten. **La solución es trabajar con los [retornos](glosario.md)** (`r_t = ln(P_t / P_{t−1})`), que tienen cinco propiedades que los hacen aptos para estas pruebas. (Evidencia: [notebook 03 §0](../../notebooks/03_eda_univariado.ipynb).)

1. **[Estacionariedad](glosario.md) aproximada.** Los retornos oscilan alrededor de cero con una variabilidad comparable a lo largo del tiempo; los precios no (crecen).
2. **Independencia relativa.** La **dirección** de un retorno no se predice casi con la anterior (la autocorrelación de `r_t` es cercana a cero), pero la **magnitud** sí: días volátiles tienden a seguir a días volátiles. Esto se nombra como "agrupamiento de la [volatilidad](glosario.md)" en Cont (2001).
3. **Escala homogénea.** Un retorno de 0,02 significa lo mismo (una subida de 2 %) para KO en 2010 y para WMT en 2020. Un cambio de precio en dólares, no.
4. **Suma de los [log-retornos](glosario.md).** El rendimiento acumulado se obtiene sumando log-retornos; esto permite anualizar y descomponer sin preocuparse por el orden multiplicativo.
5. **Distribución estable pero de colas pesadas.** Los retornos tienen más casos extremos que una normal; las pruebas de este proyecto se escogen para que esto no las rompa (proporciones y medianas por bootstrap antes que medias por t).

**Frecuencia de cada rama**:

- **Técnica (preguntas P4 y la lectura técnica del producto):** **diaria.** La volatilidad se mide mejor con cierres diarios y la etiqueta "¿toca el nivel?" se evalúa día a día dentro de `N` [días hábiles](glosario.md).
- **Riesgo, sector y valoración (P1, P5 y las dos preguntas P2 y P3):** **semanal** (y para P2 y P3 además, con una observación por empresa por **trimestre calendario**). El inversor value toma decisiones semanales y los reportes son trimestrales; esta frecuencia reduce el ruido diario sin esconder las semanas malas.
- **Turbulencia (P6):** **principal diaria** (en sesiones bursátiles) y **semanal como robustez** (porque la simulación es semanal).

**Fuentes citadas:**
- Hyndman, R. J., y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.). OTexts. https://otexts.com/fpp3/
- Cont, R. (2001). Empirical properties of asset returns: stylized facts and statistical issues. *Quantitative Finance*, 1(2), 223-236. https://doi.org/10.1080/713665670
- Campbell, J. Y., Lo, A. W., y MacKinlay, A. C. (1997). *The Econometrics of Financial Markets*. Princeton University Press (libro).
- Tsay, R. S. (2010). *Analysis of Financial Time Series* (3.ª ed.). Wiley (libro).

## §4.1 Preguntas de negocio e hipótesis

Son **6 preguntas de negocio** con **una hipótesis cada una**. Juntas suman **15 pruebas estadísticas** (una por hipótesis principal, siete por indicador en P4, dos frecuencias en P6 y dos controles de dirección). **13 pruebas llevan decisión de negocio** (todas las anteriores menos los dos controles de dirección). La lista se fijó **antes de ejecutar** y no se agrega ni se quita ninguna al ver los datos.

### P1 — ¿Cuánto me puede doler? (riesgo, semanal)

- **Paso 0 (umbral):** la tasa de semanas con una caída fuerte ([`z`](glosario.md) `= r / σ_{52 semanas previas} < −2`) debería ocurrir en una fracción pequeña de las semanas si los retornos fueran normales. Un [**nulo calibrado por simulación**](glosario.md) (porque la volatilidad se estima, no se conoce) da ≈ 2,55 % (≈ 1 semana de cada 39, ≈ 1,3 caídas fuertes al año). El umbral práctico es `1,5 × 2,55 % ≈ 3,8 %` (≈ 1 de cada 26, ≈ 2 al año): a esa frecuencia el [presupuesto de pérdida](glosario.md) fijado con la volatilidad histórica se agotaría más seguido.
- **H0:** la tasa de semanas con `z < −2` es igual al nulo calibrado (≈ 2,55 %). **H1:** es mayor.
- **Prueba:** proporción agregada en todas las semanas y empresas; IC95 bilateral por bootstrap por bloques de 12 semanas.
- **Supuestos verificados** (matriz completa en [nb03 §4.3](../../notebooks/03_eda_univariado.ipynb)): dependencia entre semanas (se mitiga con bloque de 12 semanas; sensibilidad a 4 y 26); QQ-plot de `z` (colas pesadas se mitigan con proporciones, no medias); σ estimada vs. σ conocida (nulo calibrado por simulación, 2,55 %); estabilidad por subperíodo (2009–2012, 2013–2019, 2020–2021, 2022+). Si falla, decide el IC por bloques, no el p-value clásico.
- **Decisiones:** se evalúa el IC95 bilateral frente al nulo (estadística) y el límite inferior del IC frente al umbral de 3,8 % (negocio). *Resultado en [03 §4](../../notebooks/03_eda_univariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### P2 — ¿El "barata frente a su historia" es temporal? (fundamental; una observación por empresa y trimestre calendario; horizonte de 3 años)

El "barata frente a su historia" se mide con el [**P/E normalizado**](glosario.md) **= precio ÷ promedio de la utilidad por acción trimestral de los últimos 12 trimestres ya publicados**. Un solo año de utilidades excepcionales puede hacer que una acción parezca barata sin serlo; promediar varios años evita esa ilusión (Graham y Dodd, 1934, recomiendan 5–10 años; Campbell y Shiller, 1998, usan 10). Aquí se usan 3 años porque los fundamentales estructurados empiezan en 2009 y se necesitan años para el [percentil](glosario.md) histórico y el [horizonte de valor](glosario.md); esta limitación se declara en el [punto 7](07_conclusiones.md).

- **Paso 0 (umbral):** una **diferencia anualizada en log** del cambio del P/E normalizado a 3 años ([`Δlog(P/E normalizado)`](glosario.md)`/3`) entre el [quintil](glosario.md) barato y el caro **mayor que 0,03** (≈ 9 % en 3 años). Esto cambiaría la lectura "barata" de [trampa de valor](glosario.md) a oportunidad.
- **H0:** el cambio medio del `log(P/E normalizado)` a 3 años es igual en el quintil más barato y en el más caro de cada fecha trimestral calendario. **H1:** el barato sube su P/E normalizado más (el "barata" es temporal).
- **Prueba:** en cada fecha trimestral calendario se ordenan las 21 empresas por su propio percentil del P/E normalizado y se forman [**quintiles balanceados por fecha**](glosario.md) con `k = round(0,2 · n)` empresas, donde `n` es el número de empresas con datos ese día. Solo se usa una fecha si tiene **≥ 15 empresas** con datos (regla fija). Se compara el quintil barato con el caro con [Welch](glosario.md) e **IC95 bilateral por [bootstrap por empresa](glosario.md)** (principal; preserva el [solapamiento de ventanas](glosario.md) de 3 años dentro de una empresa) y por fechas (sensibilidad). **Descomposición** `Δlog(P/E normalizado) = Δlog(precio) − Δlog(utilidad promedio 3 años)`, con tres lecturas fijadas antes: rebote del precio (oportunidad), subida de la utilidad promedio (normalización de utilidades) y caída de la utilidad promedio (deterioro, trampa de valor). [**Mann-Whitney**](glosario.md) como sensibilidad por colas pesadas.
- **Supuestos verificados** (matriz completa en [nb04 §2.4](../../notebooks/04_eda_multivariado.ipynb)): independencia (ventanas de 3 años solapadas intra-empresa y empresas que comparten fecha; se mitiga con bootstrap por empresa, principal, e IC por fechas, sensibilidad); [censura](glosario.md) (fechas sin 3 años futuros se excluyen y se cuentan en nb02 §6.1); [supervivencia](glosario.md) (declarada en el punto 7); colas pesadas (Mann-Whitney como sensibilidad); composición (si un extremo depende de 2–3 empresas, se repite sin la más frecuente, §2.9b); potencia (MDE impresa antes de estimar, §2.5); look-ahead (percentil expansivo y `filed_eps_prom_3a`).
- **Decisiones:** IC95 bilateral del Δlog anualizado frente a 0 (estadística) y su límite inferior frente a 0,03 (negocio); [Holm](glosario.md) sobre las 13 pruebas con decisión como sensibilidad. *Resultado en [04 §2](../../notebooks/04_eda_multivariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### P3 — Si compro barata, ¿me va mejor después? (fundamental; mismas fechas y mismo percentil que P2; horizonte de 3 años)

- **Paso 0 (umbral):** diferencia anualizada en log del [**retorno en exceso sobre el XLP**](glosario.md) a 3 años mayor que 0,05 por año. La literatura (Fama y French) sitúa la prima histórica por comprar barato entre 3 y 5 puntos por año; se exige el extremo alto.
- **H0:** el retorno medio en exceso sobre el XLP a 3 años del quintil barato es igual al del quintil caro. **H1:** el barato rinde más.
- **Prueba:** quintiles por fecha trimestral calendario con la misma regla de P2 (balanceados, k = round(0,2·n), ≥ 15 empresas por fecha); Welch con **IC95 bilateral por bootstrap por empresa** (principal) y por fechas (sensibilidad). **Descomposición del retorno total = retorno del XLP + exceso por quintil** (suma exacta en log). Regresión múltiple `exceso ~ percentil + ROE` con **errores estándar agrupados por empresa**. Sensibilidad: horizontes de 1, 2 y 4 años; el de 1 año no lleva decisión (es la exploración previa que motivó pasar al horizonte de 3 años).
- **Supuestos verificados** (matriz completa en [nb04 §3.4](../../notebooks/04_eda_multivariado.ipynb)): independencia (ventanas de 3 años solapadas intra-empresa; empresas de una misma fecha comparten el mercado — el **exceso** quita el choque común; se mitiga con bootstrap por empresa, principal, e IC por fechas, sensibilidad); colas pesadas (Mann-Whitney como sensibilidad); supervivencia (declarada en el punto 7); censura (fechas sin 3 años futuros se excluyen); look-ahead (percentil expansivo, `filed`).
- **Decisiones:** IC95 bilateral frente a 0 (estadística) y límite inferior del IC anualizado frente a 0,05 (negocio). *Resultado en [04 §3](../../notebooks/04_eda_multivariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### P4 — ¿Compro ya o espero? (técnica, diaria; 7 pruebas, una por indicador)

- **Paso 0 (umbral):** [**ΔAUC**](glosario.md) **≥ 0,01** por [indicador](glosario.md). Debajo de ese valor, agregar la variable al modelo técnico no justifica el ruido (en la exploración previa, variables sin señal **bajaron** la [AUC](glosario.md) total).
- **H0 (por indicador):** `ΔAUC = AUC(volatilidad + indicador) − AUC(solo volatilidad) = 0`. **H1:** `ΔAUC > 0`.
- **Prueba:** regresión logística con la magnitud de los retornos (`|r_t|`, [`σ20/σ252`](glosario.md) y [`σ252`](glosario.md)) como línea base de magnitud, y el mismo modelo más el indicador. Se evalúa en orden cronológico con corte 2018 (ajuste 2009–2018; prueba 2019+) y espacio de `N` días hábiles. **IC95 por bloques de fechas al nivel [Bonferroni](glosario.md) `1 − 0,05/7 ≈ 99,3 %`** (percentiles 0,36 y 99,64; 5000 réplicas), con una [submuestra sin solapamiento](glosario.md) (una fila cada `N` días hábiles por ticker; todas las filas solo como sensibilidad).
- **Elección de N (fijada antes):** candidatos `N ∈ {20, 40, 60}` días hábiles. Se eligen **solo con 2009–2018**: se descartan los `N` cuya [tasa de toque](glosario.md) quede fuera del 10–40 % en entrenamiento; entre los que quedan, gana el `N` con mayor AUC del **modelo A** (regresión logística con `|r_t|`, `σ20/σ252` y `σ252`) en una validación interna (ajuste 2009–2015; validación desde 2016 + N hasta 2018-12-31 − N). La prueba (2019+) **no se usa para elegir**. [**N = 60**](glosario.md) fue el ganador; los tres `N` se reportan como sensibilidad.
- **Supuestos verificados** (matriz completa en [nb04 §5.1](../../notebooks/04_eda_multivariado.ipynb)): independencia (etiquetas de días consecutivos se solapan; se mitiga con submuestra sin solapamiento cada N días + bootstrap por bloques de fechas; sensibilidad con todas las filas); dependencia residual con bloque = 1 fecha (σ252 y las medias móviles comparten historia entre filas vecinas; sensibilidad a 1/2/4 fechas); look-ahead (celda demostrativa comprueba `rsi14` recalculado con la serie truncada); multiplicidad (Bonferroni al nivel 1 − 0,05/7 ≈ 99,3 %); estabilidad por subperíodo; escalado (StandardScaler ajustado solo con el entrenamiento); censura (últimas N sesiones excluidas).
- **Decisiones (por indicador):** IC Bonferroni frente a 0 (estadística) y su límite inferior frente a 0,01 (negocio). *Resultado en [04 §5](../../notebooks/04_eda_multivariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### P5 — ¿Cuánto del movimiento viene del sector? (sector, semanal)

- **Paso 0 (umbral):** [**ΔR²**](glosario.md) **mediano = 0,05** entre el modelo `r ~ r_SPY + r_XLP` y el modelo `r ~ r_SPY`, con las 21 empresas de la [industria piloto](glosario.md).
- **H0:** `ΔR² = 0`. **H1:** `ΔR² > 0`. Como `ΔR² ≥ 0` por construcción, la decisión estadística es casi trivial; **la de negocio decide**.
- **Prueba:** regresión múltiple semanal por ticker; **IC95 bilateral por bootstrap por empresa** del ΔR² mediano. [Prueba F de modelos anidados](glosario.md) solo como referencia (los residuos tienen colas pesadas). [PCA](glosario.md) de los 21 retornos y [clustermap](glosario.md) para detectar subgrupos.
- **Transparencia:** P5 es confirmatoria. La industria piloto se eligió viendo su ΔR² en una exploración previa (declarado en [01 §1.5](01_negocio.md)).
- **Supuestos verificados** (matriz completa en [nb04 §6.2](../../notebooks/04_eda_multivariado.ipynb)): colinealidad SPY–XLP (se lee ΔR², no los coeficientes individuales; VIF reportado); residuos con colas pesadas (la F queda solo como referencia; decide el IC por empresa); heterocedasticidad por subperíodo (ΔR² por subperíodo); independencia (empresas remuestreadas como bloque, ventanas semanales sin solapamiento); look-ahead (regresión con datos ≤ t, retornos semanales).
- **Decisiones:** IC95 bilateral frente a 0 (estadística, por completitud) y su límite inferior frente a 0,05 (negocio). *Resultado en [04 §6](../../notebooks/04_eda_multivariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### P6 — ¿Vienen juntas las sesiones turbulentas? (técnica, principal diaria; semanal como robustez; 2 controles de dirección sin decisión de negocio)

- **Paso 0 (umbral):** **P(turbulenta | turbulenta) ≥ 30 %** frente al 20 % de base (una [sesión turbulenta](glosario.md) es la que tiene `|r|` en el 20 % superior de la propia historia previa de la acción). Un aumento de 10 puntos (50 % relativo) cambiaría la decisión de esperar.
- **H0:** `P(T | T) = P(T | calma)` (la turbulencia no se agrupa). **H1:** `P(T | T) > P(T | calma)`.
- **Prueba:** tablas 2×2 (turbulencia hoy × mañana; dirección hoy × mañana, como control sin decisión de negocio) con [V de Cramér](glosario.md). Decisión estadística: se rechaza H0 si el **IC95 bilateral por bootstrap por bloques** de la **diferencia** `P(T|T) − P(T|calma)` excluye 0 (el p-value del [chi-cuadrado](glosario.md) no es válido con dependencia). [Spearman](glosario.md) de `|z_t|` frente a `|z_{t−1}|` como confirmación. Dos frecuencias (diaria y semanal) + 2 controles de dirección = 4 pruebas; **los dos controles de dirección llevan solo [decisión estadística](glosario.md)**, sin [decisión de negocio](glosario.md).
- **Supuestos verificados** (matriz completa en [nb03 §5.4](../../notebooks/03_eda_univariado.ipynb)): independencia entre filas del chi-cuadrado (semanas vecinas comparten información; decide el IC por bloques, no el p-value); tamaño del bloque (sensibilidad a varios tamaños, §5.6); frecuencia del percentil 80 expansivo (shift(1), 504 días o 104 semanas de historia mínima); estabilidad por subperíodo; controles de dirección sin decisión de negocio.
- **Decisiones (frecuencia principal diaria y la secundaria semanal):** IC95 bilateral de la diferencia frente a 0 (estadística) y límite inferior del IC95 de `P(T|T)` frente a 30 % (negocio). *Resultado en [03 §5](../../notebooks/03_eda_univariado.ipynb) y en [07 §7.2](07_conclusiones.md).*

### Línea base y SVM (adelanto; se entrena en la entrega 2)

- [**Línea base por decil de σ**](glosario.md): con los datos del entrenamiento (≤ 2018), se ordenan todos los días por su volatilidad del último año (`σ252`) y se parten en 10 grupos iguales; para cada grupo se cuenta la fracción de días que terminó tocando. Para un día nuevo, la "predicción" es la tasa de su grupo. Es el modelo más simple que usa solo la volatilidad; el SVM tiene que superarlo para demostrar que aporta algo más.
- **SVM lineal (y RBF como comparación):** variables en escala de retornos (la magnitud `|r_t|`, `σ20/σ252` y `σ252`) más los indicadores técnicos que P4 justifique. Umbral: ΔAUC frente a la línea base por decil de σ ≥ 0,03.
- **H0 del SVM (entrega 2):** AUC del SVM = AUC de la línea base por decil de σ. **H1:** AUC del SVM > AUC de la línea base.

### Multiplicidad

Las 15 pruebas se reportan **sin corrección global**, salvo P4, que ya se corrige con Bonferroni al construir sus IC. **Como sensibilidad**, se aplica **Holm al 0,05 sobre las 13 pruebas con decisión de negocio** y se marca cuáles siguen rechazando H0. Para que Holm reciba un p-value comparable al IC bilateral, los **p bootstrap unilaterales se llevan a escala bilateral** multiplicando por 2 (`p_bilateral = 2 · p_unilateral`, truncado a 1); así la ordenación coincide con la del IC95 bilateral.

## §4.2 Matriz pregunta × técnica × sección del notebook

| Pregunta | Técnica estadística | Visualización | Simulación / ML | Sección del notebook |
|---|---|---|---|---|
| P1 | Proporción con IC95 por bloques de 12 semanas; nulo calibrado por simulación | QQ-plot de z; tasa por subperíodo | — | [03 §4](../../notebooks/03_eda_univariado.ipynb) |
| P2 | Welch e IC95 por empresa (principal) y por fechas (sensibilidad); Mann-Whitney; descomposición en log | Boxplots por quintil; curvas de descomposición | — | [04 §2](../../notebooks/04_eda_multivariado.ipynb) |
| P3 | Welch e IC95 por empresa y por fechas; descomposición retorno total = XLP + exceso; regresión con errores agrupados por empresa | Boxplots por quintil; barras de descomposición | — | [04 §3](../../notebooks/04_eda_multivariado.ipynb) |
| P4 | Regresión logística, AUC y ΔAUC con IC95 por bloques al nivel Bonferroni; Spearman y [VIF](glosario.md) para redundancia | Curvas ROC; tasa de toque por zona del indicador; mapas de calor de Spearman; PCA de los 7 indicadores | Tasa de toque por decil de σ252 como línea base | [04 §4 y §5](../../notebooks/04_eda_multivariado.ipynb) |
| P5 | Regresión múltiple por ticker; ΔR² mediano con IC95 por empresa; F de modelos anidados (referencia); VIF; análisis de potencia | ΔR² por empresa; QQ-plot de residuos; clustermap de los 21 retornos; PCA de los 21 retornos | — | [04 §6](../../notebooks/04_eda_multivariado.ipynb) |
| P6 | Chi-cuadrado con V de Cramér y residuos; IC95 por bloques de la diferencia; Spearman de magnitudes consecutivas | Tablas 2×2; Spearman de \|z_t\| frente a \|z_{t−1}\| | — | [03 §5](../../notebooks/03_eda_univariado.ipynb) |

Ninguna técnica queda suelta: toda técnica listada responde a una pregunta de negocio.

## §4.3 Diseño experimental

**Etiqueta diaria (P4 y SVM).** La [etiqueta de entrada](glosario.md) vale 1 si el precio toca el nivel inferior antes del superior y dentro del horizonte de `N` días hábiles; vale 0 si primero toca el superior o se agota el tiempo. El nivel inferior está a `k = 1` volatilidad diaria por `√N` por debajo del precio actual; el superior, simétrico hacia arriba. La volatilidad diaria es `σ_t`, estimada con la ventana hacia atrás; `√N` lleva esa volatilidad al horizonte. Las últimas `N` sesiones de cada ticker no tienen etiqueta resuelta (censura) y se excluyen.

**Elección de `k` y `N` fijada de antemano.** `k = 1` (criterio del autor: una caída típica en el horizonte). **`N` se elige solo con el entrenamiento (≤ 2018)** con la regla descrita en P4; el ganador fue `N = 60`. La prueba (2019+) no se usa para elegir.

**Muestra sin solapamiento.** En P4 se usa una fila cada `N` días hábiles por ticker (submuestra sin solapamiento) como principal; **todas las filas** se usan solo como sensibilidad.

**Corte cronológico con espacio.** El entrenamiento (≤ 2018) y la prueba (2019+) se separan por un espacio de **≥ `N` días hábiles** para que ninguna etiqueta del entrenamiento mire a la prueba.

**Variables del SVM en escala de retornos** (incluida la magnitud). Nunca niveles de precio, para que la lectura técnica y la fundamental sean independientes.

**Fuga de selección de P4 y cómo la mitiga la entrega 2.** P4 elige las variables del SVM con el tramo 2019+ (la prueba). Esto se declara como fuga; en la entrega 2, el SVM se evaluará en un tramo posterior a los datos de esta entrega o con validación cronológica sobre ≤ 2018, para que la selección y la evaluación no compartan datos.

**Sin look-ahead.** Toda variable en `t` usa datos ≤ `t` (ventana expansiva, `shift(1)` donde haga falta, cortes de deciles con las σ disponibles hasta `t`). Los ratios usan la fecha publicada del reporte, no la de cierre del período. Los percentiles del P/E normalizado son expansivos.

## §4.4 Métricas del modelo

**SVM (entrega 2):**
- **ROC-AUC:** probabilidad de que el modelo ordene correctamente un par (día que sí tocó, día que no tocó).
- **[Brier](glosario.md):** error cuadrático medio entre la probabilidad predicha y la realidad.
- **[Diagrama de calibración](glosario.md):** curva que compara la probabilidad predicha con la frecuencia observada por tramos. "De las veces que el modelo dijo 60 %, ¿cuántas sí tocaron?".
- **Comparación con la tasa de toque por decil de σ252** (línea base por decil de σ): regla ΔAUC = AUC(SVM) − AUC(línea base). **Dos decisiones:** se rechaza H0 (ΔAUC = 0) si el IC95 bilateral por bootstrap por bloques no incluye 0; el SVM es **accionable** si el límite inferior del IC supera 0,03. Métricas por subperíodo (2009–2012, 2013–2019, 2020–2021, 2022+).

**Lectura probabilística (simulación de salidas; entrega 2):**
- **Calibración de `P(alcanzar el nivel)`:** se compara, en orden cronológico y solo con información ≤ `t`, la probabilidad prometida con la frecuencia histórica con la que el precio sí llegó. Gráfico de calibración (idealmente sobre la diagonal) y **Brier**, frente a la tasa histórica de alcance como línea base.

## §4.5 Constantes del análisis

La tabla explica cada constante del análisis: qué significa, por qué ese valor y si **se fijó después de la exploración previa**. Los valores los usan los notebooks (en su primera celda de código) y vienen de aquí; no se usan números sueltos en el código.

**Estadísticas y de datos**

| Constante | Valor | Qué significa | Por qué ese valor | ¿Se fijó después de la exploración previa? |
|---|---|---|---|---|
| α | 0,05 | Probabilidad aceptada de rechazar H0 cuando es cierta | Nivel de significancia habitual (α = 0,05), fijado antes de ver datos | no |
| Nivel del IC | 95 % bilateral | Intervalo compatible con α = 0,05; su cola de 2,5 % hace que decida como una unilateral al 2,5 % | Mismo criterio que α | no |
| Réplicas de bootstrap | 1000 (5000 en P4) | Cuántas muestras simuladas se usan para el IC | 1000 da percentiles estables al 95 %; P4 usa un nivel más extremo (≈ 99,3 %) y necesita más réplicas para sus colas | no |
| Bloque del bootstrap | 12 semanas / 60 días hábiles (P1, P4, P6); por empresa en P2, P3 y P5 | Largo de cada tramo consecutivo que se remuestrea; en P2, P3 y P5 se remuestrean empresas completas | Un trimestre; en la validación los IC se estabilizan desde ese largo. En P2 y P3 las ventanas de 3 años se solapan dentro de cada empresa: remuestrear empresas completas conserva ese solapamiento | sí (se eligió viendo la estabilidad del IC) |
| Universo | 21 empresas de consumo defensivo + SPY + XLP | Empresas de la industria piloto | Más empresas mejoran el bootstrap por empresa (P3, P5); criterio: estar en el XLP y tener historia desde 2009 | **sí** (la industria se eligió viendo su ΔR² exploratorio frente al SPY; declarado en [01 §1.5](01_negocio.md)) |
| Bonferroni en P4 | 0,05 / 7 | α por indicador al probar 7 indicadores | Evita que alguno salga "significativo" solo por probar muchos | no |
| Ventana de σ | 52 semanas / 252 días | Volatilidad del último año | Un año bursátil (252 días hábiles); estable frente a 26/104 y 63/504 en la validación | sí (estabilidad verificada) |
| INICIO de la historia | 2009-01-01 | Primer dato descargado | Los fundamentales estructurados de la autoridad de EE.UU. empiezan en 2009 | no |
| Corte entrenamiento/prueba | 2018-12-31 | Hasta aquí se ajusta; después se evalúa | ~10 años para ajustar y ~7 para probar, incluido el COVID y 2022 | no |
| Validación para elegir N | ajuste 2009–2015, validación 2016–2018 | Elegir N sin mirar la prueba | Deja la prueba (2019+) intacta | no |
| Subperíodos | 2009–2012, 2013–2019, 2020–2021, 2022+ | Tramos para revisar la estabilidad | Salida de la crisis de 2008, expansión, COVID y mercado bajista de 2022 | no |
| Antigüedad máxima de un dato de utilidad por acción | 548 días (18 meses) | Más viejo que esto, el dato se considera rancio | El reporte anual sale ≤ 90 días después del cierre; el siguiente llega ~15 meses después; se dan 3 meses de margen | no |
| Historia mínima del percentil | 52 semanas | Mínimo para calcular el percentil histórico del P/E | Con menos de un año el percentil no es representativo | no |
| Historia mínima para "turbulenta" | 104 semanas / 504 días | Mínimo para estimar el percentil 80 propio | Dos años dan un percentil estable | no |
| Empresas por fecha trimestral (P2 y P3) | ≥ 15 | Mínimo para formar quintiles balanceados en esa fecha | Con menos empresas, los quintiles se vuelven inestables (uno de los quintiles podría tener 1 sola empresa) | no |
| Tamaño del quintil | `k = round(0,2 · n)` | Empresas en el quintil barato y en el caro de cada fecha | Balanceado en cada fecha, sin mirar al futuro; reemplaza una regla anterior con tramos fijos del percentil, que daban grupos de tamaño muy desigual | sí (se corrigió tras ver una primera versión con esa regla) |

**Umbrales de las hipótesis (paso 0: "¿qué diferencia cambiaría la decisión?")**

| Constante | Valor | Qué significa | Por qué ese valor | ¿Se fijó después de la exploración previa? |
|---|---|---|---|---|
| P1: caída fuerte | `z < −2` | Caída semanal mayor que 2 veces la volatilidad previa | Convención para un movimiento "fuerte"; con retornos normales ocurriría ~1 de cada 40 semanas | no |
| P1: nulo | ≈ 2,55 % (≈ 1 semana de cada 39, ≈ 1,3 al año) | Tasa esperada si los retornos fueran normales, medida de la misma forma | Simulación con `σ` estimada (no `Φ(−2) = 2,275 %`, que supone `σ` conocida) | **sí** (corrige la validez del nulo) |
| P1: umbral | 1,5 × nulo ≈ 3,8 % (≈ 1 de cada 26, ≈ 2 al año) | Caídas fuertes un 50 % más frecuentes que lo "normal" | A esa frecuencia el [presupuesto de pérdida](glosario.md) fijado con la volatilidad histórica se agotaría más seguido | no |
| P2: umbral | 0,03 anualizado en log (≈ 9 % en 3 años) | Cuánto más debe subir el P/E normalizado de las baratas que el de las caras | Normalización de ~9 % del múltiplo cambia la lectura "barata" de trampa a oportunidad | **sí** |
| Horizonte de valor (P2, P3) | 3 años | Ventana del resultado | Horizonte típico del inversor value; se fija uno solo para no elegir después el mejor | **sí** (se fijó tras ver la exploración a 1 año de P3; por eso 1 año queda a la vista como sensibilidad sin decisión) |
| Ventana del P/E normalizado | 12 trimestres (3 años) | Promedio de la utilidad por acción trimestral de los 12 trimestres más recientes ya publicados | Un año de utilidades excepcionales puede hacer que una acción parezca barata sin serlo; promediar varios años evita esa ilusión (Graham y Dodd, 1934; Campbell y Shiller, 1998) | **sí** |
| P3: umbral | 0,05 anualizado en log | Ventaja mínima del quintil barato en el retorno en exceso sobre el XLP | La prima histórica por comprar barato ronda 3–5 pp por año; se exige el extremo alto | no |
| P3: resultado medido | log-retorno a 3 años de la acción − el del XLP en la misma ventana | Lo que rindió la acción por encima de su industria | Dentro de una industria, todas las empresas comparten el choque del año; restarlo evita que la diferencia dependa de en qué año se compró | no |
| P2 y P3: grupos | [Quintiles por fecha](glosario.md) trimestral calendario, balanceados (`k = round(0,2 · n)`) | En cada fecha, las empresas se ordenan por su percentil propio del P/E normalizado | Grupos balanceados en cada fecha y sin mirar al futuro ([percentil expansivo](glosario.md) y orden con solo esa fecha) | **sí** |
| P4: umbral | ΔAUC = 0,01 por indicador | Mejora mínima para que un indicador entre al SVM | Un punto de AUC es la mejora mínima que justifica agregar una variable (en la exploración, variables sin señal bajaron la AUC total) | **sí** |
| P5: umbral | ΔR² mediano = 0,05 | El sector explica al menos 5 % más de la varianza que el mercado solo | Por debajo de eso, el sector casi no cambia la simulación | no |
| P6: "turbulenta" | `|r|` en el 20 % superior de su historia | Una de cada 5 sesiones más agitadas de cada acción | Quintil superior: regla simple y comparable entre acciones | no |
| P6: umbral | 30 % (frente al 20 % base) | Probabilidad de otra sesión turbulenta tras una turbulenta | Un aumento de 10 pp (50 % relativo) cambiaría la decisión de esperar | no |
| SVM: umbral | ΔAUC = 0,03 | Mejora mínima sobre la línea base por decil de σ | Mejoras de 0,02–0,04 sobre una buena línea base ya son valiosas | no |

**Etiqueta de la rama técnica**

| Constante | Valor | Qué significa | Por qué ese valor | ¿Se fijó después de la exploración previa? |
|---|---|---|---|---|
| k | 1 | El nivel de entrada está a 1 volatilidad diaria por `√N` bajo el precio actual | Una caída "típica" en el horizonte; da una tasa de toque que no es ni trivial ni rarísima | no |
| N (candidatos) | 20, 40, 60 días hábiles | Horizonte de espera (1, 2 o 3 meses) | El usuario pidió "1 mes o más" | no |
| N (elegido, solo con 2009–2018) | 60 | Horizonte que entra al SVM | Ganador por mayor AUC del modelo A en la validación interna; su tasa de toque está dentro del 10–40 % | no (procedimiento fijado antes; el valor se eligió solo con el entrenamiento) |
| Balance aceptable | 10–40 % de toques | Filtro para descartar horizontes | Con < 10 % hay muy pocos casos positivos; con > 40 % el nivel se toca casi siempre | no |
| Deciles de σ | 10 grupos | Grupos de la línea base por decil de σ252 | Cada decil conserva miles de observaciones y separa bien la tasa | no |

## Nota de transparencia

Varios umbrales y constantes se fijaron **después de una primera exploración** de los datos (columna "¿Se fijó después de la exploración previa?" con "sí"). En ningún caso se cambió la dirección de una H1 ni un umbral para acercarse al resultado; los cambios documentados corrigen validez (por ejemplo, el nulo de P1) o reemplazan procedimientos inestables (quintiles balanceados en lugar de la regla anterior con tramos del percentil fijos). Esta nota también vive en el [punto 7](07_conclusiones.md) como limitación.

## Referencias

- Graham, B., y Dodd, D. (1934). *Security Analysis*. McGraw-Hill (libro).
- Campbell, J. Y., y Shiller, R. J. (1998). Valuation ratios and the long-run stock market outlook. *Journal of Portfolio Management*, 24(2), 11-26. https://doi.org/10.3905/jpm.24.2.11
- Fama, E. F., y French, K. R. (1992). The cross-section of expected stock returns. *The Journal of Finance*, 47(2), 427-465. https://doi.org/10.1111/j.1540-6261.1992.tb04398.x
- Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *The Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- Politis, D. N., y Romano, J. P. (1994). The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303-1313. https://doi.org/10.1080/01621459.1994.10476870
- Cameron, A. C., Gelbach, J. B., y Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *The Review of Economics and Statistics*, 90(3), 414-427. https://doi.org/10.1162/rest.90.3.414
- Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary observations. *The Annals of Statistics*, 17(3), 1217-1241. https://doi.org/10.1214/aos/1176347265
- Efron, B., y Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall (libro).
