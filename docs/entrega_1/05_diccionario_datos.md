# Diccionario de datos (punto 5.3)

Describe las instantáneas de `data/snapshots/` que se descargan en [`notebooks/01_recoleccion.ipynb`](../../notebooks/01_recoleccion.ipynb) y los campos derivados que calculan [`notebooks/03_eda_univariado.ipynb`](../../notebooks/03_eda_univariado.ipynb) y [`notebooks/04_eda_multivariado.ipynb`](../../notebooks/04_eda_multivariado.ipynb). Todas las definiciones de términos se consultan en el [glosario](glosario.md).

**Universo.** 21 empresas de consumo defensivo con historia desde 2009 y en el XLP (KO, PEP, PG, WMT, COST, CL, MDLZ, KMB, GIS, MO, PM, HSY, KR, SYY, ADM, CLX, CHD, MKC, STZ, CAG, TSN), más dos ETF usados como referencia: el SPY (mercado) y el XLP (sector). KHC queda excluida porque sus precios empiezan en 2015. Los dos ETF viven solo en las tablas de precios; los demás snapshots guardan únicamente las 21 empresas.

**Cómo leer la columna "Significado del 0 o del vacío" (lección T2 del curso).** Un cero y un vacío (`NaN`) casi nunca significan lo mismo. En este proyecto el vacío quiere decir "no hay dato, no se pudo calcular o aún no se conoce" y nunca se rellena con 0. Un cero solo se interpreta como cantidad cuando la fila lo dice.

**Unidades.** USD son dólares corrientes; "adimensional" es una razón sin unidad; "fracción" es 0,05 = 5 %. Las columnas `uso` nombran las hipótesis P1–P6 definidas en [`04_enfoque_analitico.md`](04_enfoque_analitico.md) §4.1–§4.5.

**Regla de temporalidad (fecha de publicación).** Toda columna `filed_<campo>` guarda la primera fecha en que ese dato fue público; una fila de ratios solo se puede usar en una decisión en `t` si `filed ≤ t`. Esta regla se audita en nb02 §3 y evita el look-ahead en todas las uniones de precios con fundamentales.

---

## 1. Precios semanales (`data/snapshots/precios_semanales.parquet`)

Serie de tiempo semanal construida por yfinance con el cierre del viernes. 21 344 filas (23 tickers × ≈ 920 semanas desde 2009-01-05). El `close` ya viene ajustado por dividendos y splits.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `fecha` | yfinance | fecha | día | desde 2009-01-05 | Vacío: no ocurre |  Lunes que abre la semana. Llave de tiempo. Se une con `filed` de EDGAR en el panel multivariado | P2–P5 |
| `ticker` | config | texto | símbolo | 21 empresas + SPY + XLP | Vacío: no ocurre | Llave de empresa. SPY y XLP solo aparecen aquí y en `precios_diarios` | — |
| `close` | yfinance | real | USD por acción, ajustado | > 0 | 0: no debería ocurrir; sería error de la fuente. Vacío: no hubo cotización y la fila se descarta |  Precio ajustado de cierre. Base de retornos, múltiplos y de la etiqueta de entrada | todas las hipótesis |
| `volume` | yfinance | real | acciones | ≥ 0 | 0: dato no confiable; se trata como "sin dato". Vacío: igual que 0 |  Volumen negociado en la semana. Alimenta `vol_rel20` | P4 |

## 2. Precios semanales sin ajuste por dividendos (`precios_semanales_sd.parquet`)

Igual estructura y filas que `precios_semanales`, con el `close` ajustado solo por splits (no por dividendos). Se usa en nb01 §4.3 para calcular los múltiplos semanales (`close × acciones / utilidad_neta_ttm`), porque el P/E se calcula con el precio que vieron los inversores el día del cierre, no con el precio reinvertido. Mismos campos que la tabla 1.

## 3. Precios diarios (`precios_diarios.parquet`)

Serie de tiempo diaria con el mismo universo (23 tickers). 102 902 filas (desde 2009-01-02). Mismas 4 columnas que `precios_semanales`. Se usa en nb03 §5 (P6 sesiones turbulentas) y en nb04 §4 y §5 (etiqueta diaria, indicadores técnicos, P4).

## 4. Splits (`splits.parquet`)

Tabla auxiliar para auditar la trazabilidad del precio ajustado. 126 filas; 19 tickers tienen al menos un split histórico.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | yfinance | texto | símbolo | 19 empresas con splits | Vacío: no ocurre | Empresa del evento | — |
| `fecha` | yfinance | fecha | día | 1960 a hoy | Vacío: no ocurre | Día del split | — |
| `ratio` | yfinance | real | adimensional | > 0 | 0: no ocurre | Factor del split (p. ej., 2,0 para un 2:1 que duplica el número de acciones y divide el precio por 2) | — |

Uso: control del precio ajustado en nb01 §1.2 y lectura de contexto en nb02 §1. No alimenta directamente a las 15 pruebas.

## 5. Foto de identidad de yfinance (`info_yf.parquet`)

Foto del día del endpoint `info` de yfinance para las 21 empresas. 21 filas. Se usa como fuente de triangulación de identidad y de los ratios (nb02 §4–§5).

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | yfinance | texto | símbolo | 21 empresas | Vacío: no ocurre | Llave | — |
| `sector` | yfinance | texto | categoría | "Consumer Defensive" en todas | Vacío: triangulación falla, se marca | Sector reportado por yfinance (triangulación con XLP) | — |
| `industry` | yfinance | texto | categoría | sub-industria dentro de consumo defensivo | Vacío: triangulación falla | Sub-industria (grocery, packaged foods, tobacco, etc.) | — |
| `trailingPE` | yfinance | real | veces | > 0 | Vacío: EPS ≤ 0 o sin dato | P/E "actual" reportado por yfinance (contraste con el `eps_ttm` calculado) | — |
| `trailingEps` | yfinance | real | USD por acción | cualquier signo | Vacío: no reportado | EPS TTM reportado por yfinance (triangulación con el calculado desde `tabla_trimestral`; nb01 §4.3 y nb02 §2b (chequeo 3)) | — |
| `priceToBook` | yfinance | real | veces | > 0 | Vacío: BVPS ≤ 0 o sin dato | P/B reportado por yfinance | — |
| `returnOnEquity` | yfinance | real | fracción | puede ser negativa | Vacío: no reportado | ROE reportado por yfinance (triangulación) | — |
| `marketCap` | yfinance | real | USD | > 0 | Vacío: no reportado | Capitalización (precio × acciones) | — |
| `sharesOutstanding` | yfinance | real | acciones | > 0 | Vacío: no reportado | Acciones en circulación | — |

Uso: nb02 §4 (triangulación de ratios: `eps_ttm` ≈ `trailingEps`, `bvps` × `priceToBook` ≈ `close`), nb02 §5 (identidad e industria). No alimenta directamente las decisiones de P1–P6.

## 6. Hechos EDGAR crudos (`edgar_hechos.parquet`)

Capa cruda extraída del endpoint `companyfacts` de la SEC EDGAR para las 21 empresas. 72 682 filas (promedio ≈ 3 460 hechos por empresa, con conceptos repetidos en varios reportes y unidades).

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `concepto` | EDGAR XBRL | texto | etiqueta XBRL | nombres us-gaap (p. ej., `Revenues`, `NetIncomeLoss`) | Vacío: no ocurre | Nombre del concepto reportado. Los sinónimos (p. ej., `Revenues` ≡ `RevenueFromContractWithCustomerExcludingAssessedTax`) se mapean en nb01 §3.1 | — |
| `unidad` | EDGAR | texto | USD, shares, pure | USD, shares, pure | Vacío: no ocurre | Unidad declarada | — |
| `start` | EDGAR | fecha | día | 2006–hoy | Vacío: hecho puntual (saldo), no hecho de flujo | Inicio del período que cubre el hecho (flujo) | — |
| `end` | EDGAR | fecha | día | 2006–hoy | Vacío: no ocurre | Cierre del período (flujo) o fecha del saldo (balance) | — |
| `val` | EDGAR | real | USD, shares o adim. | según la unidad | 0: valor real cero (p. ej., deuda_lp = 0 en empresas sin deuda financiera); vacío: no se reportó | Valor del hecho | — |
| `form` | EDGAR | texto | tipo de reporte | 10-K, 10-Q, 10-K/A, 10-Q/A | Vacío: no ocurre | Formulario que lo publicó. Las enmiendas (`/A`) se filtran en nb01 §3 porque se usa la primera publicación | — |
| `fp` | EDGAR | texto | período fiscal | FY, Q1, Q2, Q3, Q4 | Vacío: no ocurre | Período del año fiscal al que corresponde el hecho | — |
| `filed` | EDGAR | fecha | día | posterior a `end` | Vacío: no ocurre |  Fecha en que el reporte se hizo público. Llave para evitar look-ahead | todas las hipótesis |
| `ticker` | config | texto | símbolo | 21 empresas | Vacío: no ocurre | Empresa | — |

Uso: insumo crudo de la [tabla anual](#7-tabla-anual-tabla_anualparquet) y de la [tabla trimestral](#9-tabla-trimestral-tabla_trimestralparquet). No se consulta directamente en nb03/nb04.

## 7. Tabla anual (`tabla_anual.parquet`)

Hechos anuales (10-K) de las 21 empresas, ya procesados: un valor por empresa y año fiscal, con la fecha `filed` de cada concepto. 414 filas (≈ 20 años por empresa).

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | config | texto | símbolo | 21 empresas | Vacío: no ocurre | Empresa | — |
| `end` | EDGAR | fecha | día | cierre del año fiscal | Vacío: no ocurre | Fecha de corte del año fiscal (puede ser distinta de 31-dic) | — |
| `ingresos` | EDGAR | real | USD | ≥ 0 | 0: sin ventas (no ocurre). Vacío: concepto no reportado | Ventas del año. Denominador del margen operativo | — |
| `filed_ingresos` | EDGAR | fecha | día | ≥ `end` | Vacío: no ocurre | Primera publicación del año (regla de temporalidad: solo se puede usar si `filed ≤ t`) | — |
| `utilidad_operativa` | EDGAR | real | USD | cualquier signo | 0: equilibrio. Vacío: concepto no reportado (ADM y CLX no reportan `OperatingIncomeLoss`; nb02 §2) | Utilidad antes de intereses e impuestos. Base del margen operativo | — |
| `filed_utilidad_operativa` | EDGAR | fecha | día | ≥ `end` | Vacío cuando la utilidad operativa está vacía | Fecha de publicación | — |
| `utilidad_neta` | EDGAR | real | USD | cualquier signo | 0: equilibrio. Negativo: pérdida. Vacío: no reportado | Utilidad del año. Base de ROE y EPS | — |
| `filed_utilidad_neta` | EDGAR | fecha | día | ≥ `end` | Vacío cuando la utilidad está vacía | Fecha de publicación | — |
| `patrimonio` | EDGAR | real | USD | cualquier signo (ocasional < 0 por recompras) | Vacío: no reportado | Patrimonio contable al cierre. Base de ROE, BVPS y deuda/patrimonio | — |
| `filed_patrimonio` | EDGAR | fecha | día | ≥ `end` | Vacío cuando el patrimonio está vacío | Fecha de publicación. Si `patrimonio` incluye intereses minoritarios (`StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest`), el ratio ROE queda como aproximación (nb02 §2 chequeo 3) | — |
| `deuda_lp` | EDGAR | real | USD | ≥ 0 | 0: sin deuda financiera. Vacío: no reportado (puede ser 0 real o no reportado; no se distingue) | Deuda financiera de largo plazo. Base de `deuda_patrimonio` | — |
| `filed_deuda_lp` | EDGAR | fecha | día | ≥ `end` | Vacío cuando la deuda está vacía | Fecha de publicación | — |
| `acciones` | EDGAR | real | acciones | > 0 | Vacío: no reportado | Promedio ponderado de acciones diluidas | — |
| `filed_acciones` | EDGAR | fecha | día | ≥ `end` | Vacío cuando las acciones están vacías | Fecha de publicación | — |
| `eps_reportado` | EDGAR | real | USD por acción | cualquier signo | Vacío: no reportado | EPS que la empresa reportó directamente (si existe) | — |
| `filed_eps_reportado` | EDGAR | fecha | día | ≥ `end` | Vacío cuando el EPS reportado está vacío | Fecha de publicación | — |
| `acciones_implicitas` | derivado | real | acciones | > 0 | Vacío: no se pudo calcular | Acciones implícitas = `utilidad_neta ÷ eps_reportado`, usada en nb01 §4.3 cuando faltan las acciones reportadas | — |

Uso: insumo de [ratios anuales](#8-ratios-anuales-ratios_anualesparquet) y de la tabla trimestral (nb01 §4.2 reconcilia los flujos trimestrales con los totales anuales). El EPS anual se calcula como `utilidad_neta ÷ acciones`.

## 8. Ratios anuales (`ratios_anuales.parquet`)

Los 5 ratios anuales con su `filed` por campo. 414 filas. Toda división usa `_div` del nb01: si el denominador vale 0, el resultado queda vacío (no infinito ni cero).

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | config | texto | símbolo | 21 empresas | Vacío: no ocurre | Llave de empresa | — |
| `end` | EDGAR | fecha | día | cierre fiscal | Vacío: no ocurre | Fecha de corte del año fiscal | — |
| `eps` | EDGAR | real | USD por acción | cualquier signo | 0: utilidad nula. Vacío: falta utilidad o acciones | Fórmula: `utilidad_neta ÷ acciones` | Base del P/E anual |
| `filed_eps` | derivado | fecha | día | ≥ `end` | Vacío: insumo faltante | El más tardío entre `filed_utilidad_neta` y `filed_acciones` | Primera fecha utilizable del EPS anual (regla de temporalidad: `filed` ≤ fecha de decisión) |
| `bvps` | EDGAR | real | USD por acción | cualquier signo | 0: patrimonio nulo. Vacío: insumo faltante | Fórmula: `patrimonio ÷ acciones` | Base del P/B anual |
| `filed_bvps` | derivado | fecha | día | ≥ `end` | Vacío: insumo faltante | El más tardío de los insumos | Fecha de la primera publicación (regla de temporalidad) |
| `roe` | EDGAR | real | fracción | típico −1 a 1 | 0: utilidad nula. Vacío: patrimonio 0 o insumo faltante. Negativo si hay pérdida | Fórmula: `utilidad_neta ÷ patrimonio` | Rentabilidad del patrimonio (contexto de P2, nb04 §2.10) |
| `filed_roe` | derivado | fecha | día | ≥ `end` | Vacío: insumo faltante | El más tardío de los insumos | Fecha de la primera publicación (regla de temporalidad) |
| `margen_operativo` | EDGAR | real | fracción | < 1 | 0: equilibrio. Vacío: concepto no reportado (ADM y CLX) o ingresos vacíos | Fórmula: `utilidad_operativa ÷ ingresos` | Rentabilidad del negocio (contexto de P2, nb04 §2.10) |
| `filed_margen_operativo` | derivado | fecha | día | ≥ `end` | Vacío: insumo faltante | El más tardío de los insumos | Fecha de la primera publicación (regla de temporalidad) |
| `deuda_patrimonio` | EDGAR | real | adimensional | ≥ 0 (o < 0 si patrimonio < 0) | 0: sin deuda de largo plazo. Vacío: insumo faltante | Fórmula: `deuda_lp ÷ patrimonio` | Apalancamiento (contexto de P2, nb04 §2.10) |
| `filed_deuda_patrimonio` | derivado | fecha | día | ≥ `end` | Vacío: insumo faltante | El más tardío de los insumos | Fecha de la primera publicación (regla de temporalidad) |

Uso: contexto de P2 y P3 (nb04 §2.10). Los múltiplos semanales (P/E actual y P/E normalizado) usan la versión TTM, no la anual.

## 9. Tabla trimestral (`tabla_trimestral.parquet`)

Serie trimestral de los 7 conceptos que alimentan el TTM. 9 968 filas (21 empresas × 7 conceptos × ≈ 68 trimestres). Es la fuente principal del P/E normalizado y del `roe_ttm`.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | config | texto | símbolo | 21 empresas | Vacío: no ocurre | Empresa | — |
| `concepto` | derivado | texto | categoría | `ingresos`, `utilidad_operativa`, `utilidad_neta`, `patrimonio`, `deuda_lp`, `acciones`, `eps_reportado` | Vacío: no ocurre | Nombre del concepto trimestral | — |
| `start` | EDGAR | fecha | día | inicio del trimestre | Vacío: hecho de saldo (balance, no flujo) | Inicio del período para los flujos (ingresos, utilidades); vacío para los saldos (patrimonio, deuda) | — |
| `end` | EDGAR | fecha | día | cierre del trimestre | Vacío: no ocurre | Fecha de corte del trimestre (o del saldo) | — |
| `val` | EDGAR / derivado | real | USD o acciones | según el concepto | 0: valor real cero. Vacío: no ocurre (una fila sin valor se descarta antes de guardar) | Valor del concepto en ese trimestre | — |
| `filed` | EDGAR | fecha | día | ≥ `end` | Vacío: no ocurre | Primera fecha en que ese trimestre fue público. Para `q4_derivado` toma el `filed` del 10-K; para `promedio_anual` toma el `filed` del 10-K del año | — |
| `form` | EDGAR | texto | tipo de reporte | 10-K o 10-Q | Vacío: no ocurre | Formulario que lo publicó | — |
| `origen` | derivado | texto | categoría | ver abajo | Vacío: no ocurre | Cómo se construyó el valor del trimestre | — |
| `escala_corregida` | derivado | booleano | — | True/False | True si en nb01 §4.1 se detectó un salto de escala y se corrigió (p. ej., un reporte en miles frente a los vecinos en millones) | Trazabilidad del chequeo de escala XBRL | — |
| `escala_sin_vecinos` | derivado | booleano | — | True/False | True si no había vecinos para contrastar (primer trimestre reportado o único de ese concepto) | Marca que el valor pasó sin chequeo (nb02 §2b (chequeo 9)) | — |

**Reglas de la columna `origen`** (nb01 §4.1–§4.2):

- `reportado`: valor publicado directamente en el 10-Q o en el 10-K del trimestre. Se exige una duración de 80 a 120 días para flujos trimestrales.
- `resta_ytd`: para empresas que solo reportan acumulado del año, el trimestre se obtiene como `YTD_actual − YTD_anterior` (se usan 2 filas en este snapshot; es excepcional en el universo).
- `q4_derivado`: el 10-Q no se publica para Q4; el valor del cuarto trimestre se obtiene como `anual − suma de los 3 primeros trimestres del mismo año fiscal`, con la fecha `filed` del 10-K.
- `promedio_anual`: las acciones del cierre del año se toman del 10-K cuando faltan en el 10-Q del Q4.
- `saldo`: patrimonio y deuda al cierre del trimestre (son saldos de balance, no flujos). No se agregan en el tiempo.

Uso: calidad en nb02 §2b (los 11 problemas de los 10-Q se auditan sobre esta tabla) y construcción de `ratios_ttm` en nb01 §4.3.

## 10. Ratios TTM (`ratios_ttm.parquet`)

Serie trimestral con el TTM de cada flujo, los saldos vigentes y los 5 ratios TTM. 1 434 filas (21 empresas × ≈ 68 trimestres). Es la **fuente principal del múltiplo semanal** del nb04.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `ticker` | config | texto | símbolo | 21 empresas | Vacío: no ocurre | Empresa | — |
| `end` | derivado | fecha | día | cierre del trimestre más reciente | Vacío: no ocurre | Trimestre al que corresponde el TTM | — |
| `utilidad_neta_ttm` | derivado | real | USD | cualquier signo | 0: resultado nulo. Vacío: falta uno de los 4 trimestres consecutivos | Suma de la utilidad neta de los 4 trimestres más recientes | — |
| `filed_utilidad_neta_ttm` | derivado | fecha | día | ≥ `end` | Vacío si el TTM está vacío | Fecha de publicación del último de sus 4 trimestres (nb02 §2b (chequeo 1)) | — |
| `ingresos_ttm` | derivado | real | USD | ≥ 0 | 0: sin ventas (no ocurre). Vacío: falta un trimestre | Suma de ingresos de 4 trimestres | — |
| `filed_ingresos_ttm` | derivado | fecha | día | ≥ `end` | Vacío si el TTM está vacío | fecha de la primera publicación (regla de temporalidad) | — |
| `utilidad_operativa_ttm` | derivado | real | USD | cualquier signo | 0: equilibrio. Vacío: concepto no reportado (ADM y CLX) o falta un trimestre | Suma de la utilidad operativa de 4 trimestres | — |
| `filed_utilidad_operativa_ttm` | derivado | fecha | día | ≥ `end` | Vacío si el TTM está vacío | fecha de la primera publicación (regla de temporalidad) | — |
| `patrimonio` | derivado | real | USD | cualquier signo | Vacío: no reportado al cierre | Último saldo publicado del patrimonio | — |
| `filed_patrimonio` | derivado | fecha | día | ≥ `end` | Vacío cuando el patrimonio está vacío | Primera publicación del saldo | — |
| `deuda_lp` | derivado | real | USD | ≥ 0 | 0: sin deuda de largo plazo. Vacío: no reportado | Último saldo publicado de la deuda de largo plazo | — |
| `filed_deuda_lp` | derivado | fecha | día | ≥ `end` | Vacío cuando la deuda está vacía | Primera publicación del saldo | — |
| `acciones` | derivado | real | acciones | > 0 | Vacío: no reportado | Acciones del último trimestre (fuente única) | — |
| `filed_acciones` | derivado | fecha | día | ≥ `end` | Vacío cuando las acciones están vacías | fecha de la primera publicación (regla de temporalidad) | — |
| `acciones_implicitas` | derivado | real | acciones | > 0 | Vacío: no se pudo calcular | Alternativa calculada como `utilidad_neta ÷ eps_reportado` cuando faltan las acciones (mecanismo alternativo cuando `WeightedAverageNumberOfDilutedSharesOutstanding` falta; nb01 §4.3) | — |
| `eps_ttm` | derivado | real | USD por acción | cualquier signo | 0: utilidad TTM nula. Vacío: falta uno de los insumos |  `utilidad_neta_ttm ÷ acciones`. Base del **P/E actual** del múltiplo semanal | P2 §2.4, P3 |
| `filed_eps_ttm` | derivado | fecha | día | ≥ `end` | Vacío cuando el EPS TTM está vacío | fecha de la primera publicación: el más tardío de `filed_utilidad_neta_ttm` y `filed_acciones`) | — |
| `bvps` | derivado | real | USD por acción | cualquier signo | Vacío: patrimonio o acciones faltantes | `patrimonio ÷ acciones`. Base del P/B semanal | — |
| `filed_bvps` | derivado | fecha | día | ≥ `end` | Vacío cuando el BVPS está vacío | fecha de la primera publicación (regla de temporalidad) | — |
| `roe_ttm` | derivado | real | fracción | típico −1 a 1 | 0: utilidad nula. Vacío: patrimonio 0 o insumo faltante |  `utilidad_neta_ttm ÷ patrimonio`. Rentabilidad del patrimonio | contexto P2 |
| `filed_roe_ttm` | derivado | fecha | día | ≥ `end` | Vacío cuando `roe_ttm` está vacío | fecha de la primera publicación (regla de temporalidad) | — |
| `margen_operativo_ttm` | derivado | real | fracción | < 1 | 0: equilibrio. Vacío: concepto no reportado (ADM, CLX) o ingresos faltantes |  `utilidad_operativa_ttm ÷ ingresos_ttm`. Contexto de | P2 |
| `filed_margen_operativo_ttm` | derivado | fecha | día | ≥ `end` | Vacío cuando el margen está vacío | fecha de la primera publicación (regla de temporalidad) | — |
| `deuda_patrimonio` | derivado | real | adimensional | ≥ 0 (negativo si patrimonio < 0) | 0: sin deuda. Vacío: insumo faltante |  `deuda_lp ÷ patrimonio`. Contexto de | P2 |
| `filed_deuda_patrimonio` | derivado | fecha | día | ≥ `end` | Vacío cuando la razón está vacía | fecha de la primera publicación (regla de temporalidad) | — |
| `eps_prom_3a` | derivado | real | USD por acción | cualquier signo | Vacío: faltan trimestres o acciones |  **EPS promedio normalizado a 3 años** = suma de utilidad neta de los 12 trimestres más recientes ya publicados ÷ 3 ÷ acciones del último trimestre. Es anual (nb01 §4.3). Base del **P/E normalizado** | P2 y P3 |
| `filed_eps_prom_3a` | derivado | fecha | día | ≥ `end` | Vacío cuando `eps_prom_3a` está vacío | fecha de la primera publicación: el más tardío entre los 12 `filed` de utilidad neta y el `filed` de acciones | — |

**Antigüedad máxima del TTM.** Un valor TTM se considera "rancio" cuando han pasado más de 548 días (≈ 18 meses) desde `end` sin un trimestre nuevo publicado. En ese caso el múltiplo semanal usa el último TTM disponible pero se marca como potencialmente desactualizado (nb01 §4.3; nb02 §2b (chequeo 1)).

**Aproximaciones XBRL.** `patrimonio` toma `StockholdersEquity`; si falta, cae a `StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest` (incluye intereses minoritarios): el ROE y el BVPS quedan como aproximación. `utilidad_neta` cae de `NetIncomeLoss` a `ProfitLoss` cuando falta; también se marca como aproximación (nb02 §2b (chequeo 3)).

## 11. Múltiplo semanal (derivado en nb04 §1)

Panel que une `precios_semanales_sd` con `ratios_ttm` por `ticker` y la última fila con `filed ≤ fecha`. No se guarda como instantánea; se construye en nb04 §1.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `fecha` | `precios_semanales_sd` | fecha | día | lunes de la semana | Vacío: no ocurre | Fecha del múltiplo | — |
| `ticker` | `precios_semanales_sd` | texto | símbolo | 21 empresas (SPY y XLP no entran) | Vacío: no ocurre | Empresa | — |
| `close` | `precios_semanales_sd` | real | USD por acción | > 0 | Vacío: no ocurre | Precio sin ajuste por dividendos (nb01 §4.3) | — |
| `eps_ttm` | `ratios_ttm` | real | USD por acción | cualquier signo | 0 o negativo: P/E actual queda vacío (no "barato"). Vacío: sin dato publicado | Último EPS TTM con `filed ≤ fecha` | — |
| `eps_prom_3a` | `ratios_ttm` | real | USD por acción | cualquier signo | 0 o negativo: P/E normalizado vacío. Vacío: sin dato publicado | Último `eps_prom_3a` con `filed ≤ fecha` | — |
| `pe_actual` | derivado | real | veces | > 0 | Vacío: `eps_ttm ≤ 0` o sin dato |  `close ÷ eps_ttm`. Múltiplo "actual". Ejemplo KO 2026-10-12: 92,00 / 3,18 ≈ 29. Uso: contexto de | P2 |
| `pe_norm` | derivado | real | veces | > 0 | Vacío: `eps_prom_3a ≤ 0` o sin dato | `close ÷ eps_prom_3a`. **Múltiplo principal de P2 y P3**. Ejemplo KO 2026-10-12: 92,00 / 2,73 ≈ 33,8 | — |
| `pb` | derivado | real | veces | > 0 | Vacío: `bvps ≤ 0` o sin dato |  `close ÷ bvps`. Contexto de | P2 |
| `pct_norm` | derivado | real | fracción | 0 a 1 | Vacío: menos de 52 semanas de historia (regla fijada en nb04 §1) | **Percentil expansivo** del `pe_norm` de la empresa dentro de su propia historia hasta `fecha`. Alimenta los quintiles por fecha de P2 §2.3 | P2, P3 |

## 12. Indicadores diarios (derivados en nb04 §5)

Siete indicadores técnicos calculados por ticker sobre `precios_diarios`. Todos miran solo hacia atrás (nb04 §5 incluye una celda demostrativa que recalcula `rsi14` con la serie truncada en `t` y confirma look-ahead = 0). El calentamiento de cada ventana queda vacío.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `rsi14` | `close` | real | puntos | 0 a 100 | 0: todas las variaciones recientes fueron negativas (sobreventa extrema). 100: todas positivas. Vacío: menos de 14 sesiones |  **RSI** con suavizado exponencial de 14 sesiones | P4 |
| `dist_sma20` | `close` | real | fracción | típico −0,3 a 0,5 | 0: precio sobre la SMA de 20 sesiones. Vacío: menos de 20 sesiones |  `close ÷ SMA20 − 1` | P4 |
| `dist_sma50` | `close` | real | fracción | típico −0,3 a 0,5 | 0: precio sobre la SMA de 50 sesiones. Vacío: menos de 50 sesiones |  `close ÷ SMA50 − 1` | P4 |
| `dist_sma200` | `close` | real | fracción | típico −0,3 a 0,5 | 0: precio sobre la SMA de 200 sesiones. Vacío: menos de 200 sesiones |  `close ÷ SMA200 − 1` | P4 |
| `vol_rel20` | `volume` | real | adimensional | > 0 | 0: no ocurre; volumen 0 se trata como vacío. Vacío: menos de 20 sesiones o volumen 0 |  `volume ÷ promedio de volumen de 20 sesiones`. 1 ≈ volumen típico | P4 |
| `donchian20` | `close` | real | adimensional | 0 a 1 | 0: cierre en el mínimo del canal. 1: en el máximo. Vacío: menos de 20 sesiones o canal sin amplitud |  Posición del cierre dentro del canal Donchian de 20 sesiones | P4 |
| `mom_12_1` | `close` | real | fracción | típico −0,5 a 1,5 | 0: precio de hace 21 sesiones igual al de hace 252. Vacío: menos de 252 sesiones |  `close_{t−21} ÷ close_{t−252} − 1`. Momentum "12−1" | P4 |

## 13. Variables de magnitud y etiqueta diaria (nb04 §4)

Panel diario que une `precios_diarios` con la volatilidad hacia atrás y la etiqueta de triple barrera solo-largo. Base de P4.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción | Uso (P1–P6) |
|---|---|---|---|---|---|---|---|
| `r` | `close` | real | fracción | típico −0,2 a 0,2 | 0: precio sin cambio. Vacío: primera sesión del ticker | `log(close_t ÷ close_{t−1})`. Log-retorno diario | — |
| `abs_r` | derivado | real | fracción | ≥ 0 | 0: sesión sin movimiento. Vacío: `r` vacío | `abs(r)`. Magnitud del retorno diario. Línea base de magnitud del modelo A (nb04 §5) | P4 |
| `sigma20` | `r` | real | fracción | > 0 | Vacío: menos de 20 sesiones previas | Desviación estándar de los últimos 20 retornos diarios (`shift(1)` previo) | — |
| `sigma252` | `r` | real | fracción | > 0 | Vacío: menos de 252 sesiones previas | **σ252 diaria**. Desviación estándar de los últimos 252 retornos (`shift(1)` previo). Umbral de la etiqueta de entrada | — |
| `sigma20_sigma252` | derivado | real | adimensional | > 0 | Vacío: alguna σ faltante | `sigma20 ÷ sigma252`. Aceleración o calma relativa | — |
| `y` | derivado | binario | 0 o 1 | {0, 1} | 1: en los siguientes N = 60 días hábiles el precio tocó `close × (1 − k·σ252)` antes que `close × (1 + k·σ252)` o antes del tiempo. 0: salida por arriba o por tiempo. Vacío: censura (menos de N sesiones futuras) o falta σ252. k = 1 (nb04 §4). **Nunca es 0 por falta de dato** | Etiqueta de entrada "toca el nivel". Variable objetivo del SVM (fuera del alcance de la entrega 1) y de los ΔAUC de P4 (nb04_p4.json) | — |

## 14. Tabla por industria Damodaran (`damodaran_pe.parquet` y `damodaran_margenes.parquet`)

Tablas de referencia por industria publicadas por Aswath Damodaran (NYU Stern). 96 filas cada una (una por industria). Se descargan en nb01 §2 y se consultan como comparación externa; no alimentan directamente las decisiones de P1–P6, pero sirven de "corte de realidad" en nb02 §4 para los ratios TTM (triangulación).

**Columnas de `damodaran_pe` relevantes:** `industry_name`, `number_of_firms`, `current_pe`, `trailing_pe`, `forward_pe`, `expected_growth_next_5_years`, `peg_ratio`. **De `damodaran_margenes`:** `industry_name`, `gross_margin`, `net_margin`, `pre_tax_unadjusted_operating_margin`, `ebitda_sales`, `r_d_sales`, `sg_a_sales`. Todas las fracciones son adimensionales; los vacíos son no reportados. Uso: contraste del margen operativo y del P/E del grupo consumo defensivo frente a sus 20 empresas.

---

## Referencias cruzadas

- Las decisiones de limpieza y los 11 problemas del TTM viven en nb02 §2b con su dimensión, nivel y justificación.
- La construcción de la tabla trimestral y del TTM, con los chequeos de escala, está en nb01 §4.1–§4.3.
- Los umbrales y constantes que leen los notebooks (horizontes, k·σ, nivel Bonferroni, …) viven en [`04_enfoque_analitico.md`](04_enfoque_analitico.md) §4.5.
- Las técnicas estadísticas que consumen estos campos están descritas en [`04_enfoque_analitico.md`](04_enfoque_analitico.md) §4.2 (matriz pregunta × técnica).
- Toda definición de término técnico se consulta en el [glosario](glosario.md).
