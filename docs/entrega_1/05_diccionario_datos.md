# Diccionario de datos (punto 5.3)

Cubre precios, indicadores técnicos, conceptos de EDGAR, ratios, etiquetas y métricas de riesgo. Todo se calcula en `src/asistente/` y se descarga en `notebooks/01_recoleccion.ipynb`.

**Cómo leer la columna "Significado del 0 o del vacío" (lección T2).** Un cero y un vacío (`NaN`) casi nunca significan lo mismo. En este proyecto el vacío quiere decir "no hay dato, no se pudo calcular o aún no se conoce" y nunca se rellena con 0. Un cero solo se interpreta como cantidad cuando la fila lo dice.

Unidades: USD son dólares corrientes; "adimensional" es una razón sin unidad; "fracción" es 0.05 = 5 %. Hipótesis: IDs de `docs/hipotesis.md`.

## 1. Precios (yfinance), instantáneas `precios_semanales` y `precios_mensuales`

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `fecha` | yfinance | fecha | día | desde 2009-01-05 (semanal) o 2009-01-01 (mensual) | Vacío: no existe (la fila se descarta). Semanal: lunes que abre la semana; mensual: día 1 del mes | Llave de tiempo del panel. Se une con `filed` de EDGAR mediante `alinear_por_filed` (todas las hipótesis) |
| `ticker` | config | texto | símbolo | 30 acciones, SPY, XLK, XLP, XLF | Vacío: no ocurre | Llave de empresa. Define la industria con `config.industria_de` (HF2, HP3) |
| `close` | yfinance | real | USD por acción, ajustado por dividendos y particiones | > 0 | 0: no debería ocurrir; un 0 sería un error de la fuente. Vacío: no hubo cotización en esa barra, y la fila se elimina al descargar | Precio de cierre de la barra. Base de retornos, indicadores y etiquetas (HT0–HT4, HP0–HP3) |
| `volume` | yfinance | real | acciones | >= 0 | 0: dato no confiable o no reportado (ETF y barras parciales); no se lee como "nadie negoció". Vacío: igual que 0 para efectos de uso. Ambos se tratan como "sin dato" en `vol_rel20` | Volumen negociado en la barra. Alimenta `vol_rel20` (HT2) |
| `r` (log) | derivado | real | fracción por semana | cola gruesa; típicamente entre -0.4 y 0.4 | 0: el precio no cambió en la semana (poco frecuente en acciones líquidas). Vacío: primera barra de cada ticker, que no tiene retorno previo | `r_t = ln(close_t / close_{t-1})` (`riesgo.log_retornos`). Base de volatilidad, VaR, GARCH, GBM y prueba de caminata aleatoria (HT0, HT4, HP0–HP3) |

## 2. Indicadores técnicos (`indicadores.tabla_indicadores`), semanales

El calentamiento de cada ventana queda en vacío: no se rellena ni se arrastra el último valor.

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `rsi14` | derivado de `close` | real | puntos del índice | 0 a 100 | 0: todas las variaciones recientes fueron bajas (sobreventa extrema). 100: todas fueron altas. Vacío: menos de 14 semanas de historia, o precio sin variación en la ventana (denominador 0) | Índice de fuerza relativa con suavizado exponencial de 14 semanas. Mide sobreextensión (HT2) |
| `dist_sma20` | derivado de `close` | real | fracción | > -1; típico -0.3 a 0.5 | 0: el precio está justo sobre su media simple de 20 semanas. Vacío: menos de 20 semanas | `close / SMA20 - 1`. Distancia a la media corta (HT2) |
| `dist_sma50` | derivado de `close` | real | fracción | > -1 | 0: precio sobre la media de 50 semanas. Vacío: menos de 50 semanas | Igual que la anterior con ventana 50 (HT2) |
| `dist_ema20` | derivado de `close` | real | fracción | > -1 | 0: precio sobre la media exponencial de 20 semanas. Vacío: menos de 20 semanas | Versión exponencial de `dist_sma20`, más sensible a lo reciente (HT2) |
| `vol_rel20` | derivado de `volume` | real | adimensional | > 0 | 0: no ocurre, porque el volumen 0 se trata como "sin dato". Vacío: volumen 0 o vacío en la semana, o menos de 20 semanas de historia. 1 significa volumen igual al promedio de 20 semanas | Volumen de la semana dividido por su media móvil de 20 semanas (HT2) |
| `donchian20` | derivado de `close` | real | fracción del canal | 0 a 1 | 0: el cierre está en el mínimo de 20 semanas. 1: está en el máximo (techo del canal). Vacío: menos de 20 semanas o canal sin amplitud (máximo igual a mínimo) | Posición del cierre dentro del canal Donchian de 20 semanas (HT2) |
| `mom_12_1` | derivado de `close` | real | fracción | > -1 | 0: el precio de hace 4 semanas es igual al de hace 52. Vacío: menos de 52 semanas de historia | Momentum de 12 meses saltando el último mes: `close_{t-4} / close_{t-52} - 1` (Jegadeesh, 1990; HT2, HF3) |

## 3. Conceptos de EDGAR (`edgar.CONCEPTOS`), instantánea `edgar_hechos` y tabla anual

Fuente: SEC EDGAR `companyfacts` (us-gaap). Solo se usan periodos de 330 a 400 días (año completo). Se prueban las etiquetas alternativas en orden y se toma la primera con datos. El vacío nunca se rellena con 0.

| Campo | Fuente (etiqueta XBRL) | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `ingresos` | `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet` | real | USD | >= 0 | 0: sin ventas (no ocurre en el universo). Vacío: la empresa no reportó ese año con esas etiquetas | Ventas del año. Denominador de márgenes y `capex_ventas` (HF1, HF2) |
| `utilidad_bruta` | `GrossProfit` | real | USD | >= 0 | Vacío: concepto no aplicable (bancos no lo reportan); no es 0 | Ingresos menos costo de ventas. Margen bruto (HF2) |
| `utilidad_operativa` | `OperatingIncomeLoss` | real | USD | cualquier signo | 0: punto de equilibrio operativo. Vacío: no reportado (bancos) | Utilidad antes de intereses e impuestos. Margen operativo y ROIC (HF1, HF2) |
| `utilidad_neta` | `NetIncomeLoss` | real | USD | cualquier signo | 0: equilibrio. Negativo: pérdida. Vacío: no reportado | Resultado final del año. ROE, EPS y margen neto (HF1, HF3) |
| `patrimonio` | `StockholdersEquity`, `...IncludingPortionAttributableToNoncontrollingInterest` | real | USD | cualquier signo (puede ser negativo por recompras) | Vacío: no reportado. Patrimonio <= 0 vuelve sin sentido a ROE y P/B | Patrimonio de los accionistas. ROE, BVPS, deuda/patrimonio (HF1, HF3) |
| `deuda_lp` | `LongTermDebt`, `LongTermDebtNoncurrent` | real | USD | >= 0 | 0: sin deuda de largo plazo. Vacío: no reportada (puede ser 0 real o no reportada; no se distingue) | Deuda financiera de largo plazo. Apalancamiento, ROIC y Merton (HF3, HF4) |
| `caja` | `CashAndCashEquivalentsAtCarryingValue` | real | USD | >= 0 | 0: sin efectivo (raro). Vacío: no reportado | Efectivo y equivalentes. Se resta del capital invertido (HF2) |
| `cfo` | `NetCashProvidedByUsedInOperatingActivities` | real | USD | cualquier signo | Vacío: no reportado | Flujo de caja operativo. Base del FCF (HF3) |
| `capex` | `PaymentsToAcquirePropertyPlantAndEquipment` | real | USD | >= 0 (pago positivo) | 0: sin inversión en activos fijos. Vacío: no reportado (no es 0) | Inversión en activos fijos. `capex_ventas` y FCF (HF2, HF3) |
| `acciones` | `WeightedAverageNumberOfDilutedSharesOutstanding` | real | acciones | > 0 | Vacío: no reportado; deja EPS, BVPS y `fcf_yield` en vacío | Promedio ponderado de acciones diluidas. Convierte totales a por acción (HF3) |
| `end` | EDGAR | fecha | día | 2006 a 2026 | Vacío: no ocurre | Cierre del año fiscal al que pertenece el dato |
| `filed` | EDGAR | fecha | día | posterior a `end` | Vacío: no ocurre | Fecha en que el 10-K fue público. Llave de unión con precios para evitar look-ahead (todas las HF) |

## 4. Ratios y múltiplos (`fundamentales`), instantánea `ratios_anuales`

Toda razón divide con `_div`: si el denominador es 0 el resultado queda vacío, no infinito. Los múltiplos se calculan semanalmente con el dato anual vigente en la fecha `filed` (sin look-ahead).

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `roe` | EDGAR | real | fracción anual | típico -1 a 1 | 0: utilidad neta nula. Vacío: falta utilidad o patrimonio, o patrimonio 0 | `utilidad_neta / patrimonio`. Calidad (HF1, HF2) |
| `roic` | EDGAR | real | fracción anual | típico -0.5 a 1 | 0: utilidad operativa nula. Vacío: falta algún insumo o capital invertido 0 | `utilidad_operativa*(1-0.21) / (patrimonio + deuda_lp - caja)` (HF1, HF2) |
| `margen_bruto` | EDGAR | real | fracción | 0 a 1 | 0: sin utilidad bruta. Vacío: no aplica (bancos) | `utilidad_bruta / ingresos` (HF2) |
| `margen_operativo` | EDGAR | real | fracción | < 1 | 0: equilibrio operativo. Vacío: no reportado | `utilidad_operativa / ingresos` (HF2) |
| `margen_neto` | EDGAR | real | fracción | < 1 | 0: equilibrio. Vacío: no reportado | `utilidad_neta / ingresos` (HF2) |
| `deuda_patrimonio` | EDGAR | real | adimensional | >= 0 (negativo si patrimonio < 0) | 0: sin deuda de largo plazo. Vacío: falta dato | `deuda_lp / patrimonio` (HF2) |
| `capex_ventas` | EDGAR | real | fracción | >= 0 | 0: sin capex. Vacío: falta dato | `capex / ingresos`. Intensidad de capital (HF2) |
| `eps` | EDGAR | real | USD por acción | cualquier signo | 0: utilidad nula. Vacío: falta utilidad o acciones | `utilidad_neta / acciones` (HF3) |
| `bvps` | EDGAR | real | USD por acción | cualquier signo | Vacío: falta patrimonio o acciones | `patrimonio / acciones` (HF3) |
| `fcf` | EDGAR | real | USD | cualquier signo | 0: flujo operativo igual al capex. Vacío: falta `cfo` o `capex` | `cfo - capex` (HF3) |
| `pe` | precio + EDGAR | real | veces | > 0 | Vacío: EPS <= 0 o sin dato (P/E sin sentido, nunca 0) | `close / eps` (HF3, HF5) |
| `pb` | precio + EDGAR | real | veces | > 0 | Vacío: BVPS <= 0 o sin dato | `close / bvps` (HF3, HF5) |
| `fcf_yield` | precio + EDGAR | real | fracción | cualquier signo | 0: FCF nulo. Vacío: falta FCF, acciones o precio | `fcf / (close * acciones)` (HF3) |

## 5. Etiquetas (`etiquetas`)

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `etiqueta` | derivado | binario | 0 o 1 | {0, 1} | 1: el precio tocó la barrera inferior (entrada) antes que la superior o el tiempo. 0: escape por arriba o vencimiento. Vacío: censurada (menos de n semanas por delante), sin sigma, o hueco de precio. Nunca 0 por falta de dato | Triple barrera solo-largo, variable objetivo del SVM (HT1, HT2) |
| `resultado` | derivado | texto | categoría | `entrada`, `escape`, `tiempo` | Vacío: igual que la etiqueta vacía | Qué barrera se tocó |
| `semanas` | derivado | real | semanas | 1 a n | Vacío: no tocó ninguna barrera (`tiempo`) o fila censurada | Semanas hasta tocar la barrera. Insumo del eje probabilístico (HP1, HP2) |
| `etiqueta_retorno` | derivado | binario | 0 o 1 | {0, 1} | 1: el retorno a n semanas supera el del umbral (0 o benchmark). 0: no lo supera. Vacío: sin futuro disponible | Etiqueta alternativa para comparar (HT3) |

## 6. Métricas de riesgo (`riesgo`, `simulacion`)

| Campo | Fuente | Tipo | Unidad | Rango válido | Significado del 0 o del vacío | Descripción y uso |
|---|---|---|---|---|---|---|
| `vol_ewma` | derivado de `r` | real | fracción anualizada | >= 0 | 0: retornos nulos. Primera barra tiene valor (lambda 0.94) | Volatilidad EWMA anualizada (x raiz 52). Ancho de las barreras (HT1, HP0) |
| `var_95` | derivado de `r` | real | fracción por semana | negativo (pérdida) | Vacío: sin retornos. No tiene 0 esperado | Cuantil 5 % de `r`, histórico o paramétrico (HP0) |
| `es_95` | derivado de `r` | real | fracción por semana | <= `var_95` | Vacío: sin retornos | Media de los retornos peores que el VaR (HP0) |
| `beta` | derivado | real | adimensional | típico 0 a 2 | 0: sin relación con SPY. Vacío: sin datos solapados | Pendiente de `r` contra SPY (HP0, HP3) |
| `alpha` | derivado | real | fracción por semana | cercano a 0 | 0: sin exceso sobre el mercado. Vacío: sin datos solapados | Intercepto de la regresión contra SPY (HP3) |
| `d2` | derivado (Merton) | real | adimensional | cualquier signo | Vacío: entradas inválidas (E, sigma, D o T <= 0) o el solver no converge | Distancia al incumplimiento (HF4) |
| `pd_merton` | derivado (Merton) | real | probabilidad | 0 a 1 | 0: riesgo despreciable. Vacío: igual que `d2` | `N(-d2)`, devuelto como `pd` por `riesgo.merton` (HF4) |
