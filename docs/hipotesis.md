# Mapa de hipótesis por eje de análisis (borrador v2, 2026-10-13)

Todo se formula como **asociación**, no como causa (lección del examen 1). Columna "E1": ✔ = el EDA de la Entrega 1 puede darle una primera respuesta; ◐ = el EDA solo la prepara (etiquetas, línea base); la prueba completa requiere entrenar o simular.

## Nota sobre la caminata aleatoria (eficiencia débil, Fama 1970)
No es una hipótesis transversal que se valide en los tres ejes. Dice que los precios pasados no predicen la **dirección** futura. No dice nada sobre la volatilidad (que sí es predecible), ni sobre los fundamentales, ni sobre el valor del producto. Por eso:
- en el eje técnico es **la línea base a vencer** (HT0);
- en el probabilístico es **el supuesto del modelo** que se verifica (HP0);
- en el fundamental **no aplica**, porque usa información contable y no precios pasados.

Resultado esperado del EDA (Cont, 2001): los retornos tienen poca autocorrelación (la dirección es casi una caminata aleatoria), pero los retornos al cuadrado sí la tienen (la volatilidad es predecible). Esto justifica escalar las barreras con σ y usar GARCH.

**Hipótesis principales (★):** HT0, HT1, HT2, HF1, HF2, HP0, HP3. Las demás son secundarias, con un análisis más ligero.

## Eje técnico (SVM): "¿compro ya o espero?"
| ID | Hipótesis | Prueba / métrica | Referencias | E1 |
|---|---|---|---|---|
| ★ HT0 | **Línea base:** la dirección del precio semanal se comporta como una caminata aleatoria. Cualquier probabilidad del SVM se compara contra la probabilidad bajo este supuesto | ADF + KPSS sobre log-precios; Ljung-Box sobre retornos; probabilidad GBM de tocar el nivel | Fama (1970); curso XXI p7, XXVI p9–11 | ✔ |
| ★ HT1 | Los indicadores técnicos mejoran la estimación de P(el precio toca el nivel de entrada en N semanas antes de escaparse) frente a la probabilidad GBM | AUC, Brier y calibración del SVM vs. GBM; validación walk-forward con purga | Kim (2003); Lo, Mamaysky & Wang (2000); López de Prado (2018) | ◐ |
| ★ HT2 | La sobreextensión (RSI alto, distancia grande a la SMA/EMA, techo del canal Donchian) se asocia con mayor probabilidad de retroceso | Distribución de cada indicador por clase de la etiqueta; AUC univariada; Mann-Whitney + block bootstrap | Park & Irwin (2007); Jegadeesh (1990) | ✔ |
| HT3 | La relación indicador → etiqueta es estable entre regímenes de mercado | HT2 repetida por régimen (2008, 2020, 2022, etc.) | Ang & Timmermann (2012) | ✔ |
| HT4 | La volatilidad semanal se agrupa, por lo que las barreras deben escalarse con σ | ARCH-LM, ACF de r², persistencia α+β del GARCH | Engle (1982); Bollerslev (1986); curso XIII–XIV | ✔ |

## Eje fundamental comparativo: "¿es razonable este nivel para esta empresa?"
| ID | Hipótesis | Prueba / métrica | Referencias | E1 |
|---|---|---|---|---|
| ★ HF1 | Los múltiplos de valoración (P/E, P/B) revierten a su propia media histórica | ADF sobre la serie del múltiplo; ajuste OU (η, vida media ln2/η) | Curso XXV–XXVI; Dixit & Pindyck (1994) | ✔ |
| ★ HF2 | El múltiplo relativo (empresa ÷ mediana de la industria) revierte: los descuentos frente al sector tienden a cerrarse | Igual que HF1 sobre el múltiplo relativo | Curso XXV; Asness et al. (2013) | ✔ |
| HF3 | Estar barata frente a su historia y a su industria (percentil bajo), con calidad (ROIC/ROE sobre la industria), se asocia con mejores retornos posteriores a 12 meses | Retorno posterior por quintil de percentil, con fecha `filed`; Spearman; bootstrap | Fama & French (1992); Piotroski (2000) | ✔ (muestra pequeña: exploratorio) |
| HF4 | Menor distancia al default (Merton d₂) se asocia con mayor riesgo de caída (drawdown y VaR) | Correlación entre d₂ y el drawdown o VaR posterior, por industria | Merton (1974); curso XXX | ✔ |
| HF5 | Los ratios calculados desde EDGAR son consistentes con yfinance y Damodaran (validez de la fuente) | Diferencias relativas por ratio y empresa; coincidencia con el 10-K publicado | Lección del examen 1 (validar etiquetas del proveedor) | ✔ |

## Eje probabilístico: "¿qué tan probable es llegar a cada nivel y en cuánto tiempo?"
| ID | Hipótesis | Prueba / métrica | Referencias | E1 |
|---|---|---|---|---|
| ★ HP0 | **Supuesto del modelo:** un GBM normal (caminata aleatoria con volatilidad constante) es adecuado para simular el precio semanal; si no, se pasa a GARCH-t | ACF de r y r², ARCH-LM, Jarque-Bera + QQ-plot | Cont (2001); Engle (1982); curso XI–XIV, XXIII | ✔ |
| HP1 | Un GBM normal subestima las colas; GARCH con errores t describe mejor el riesgo | Jarque-Bera + QQ-plot; ajuste normal vs. t; VaR backtesting (Kupiec, Christoffersen) | Cont (2001); Christoffersen (2012); Kupiec (1995) | ✔ |
| HP2 | Las probabilidades del Monte Carlo están calibradas: en la historia, los niveles con P≈x% se alcanzaron cerca del x% de las veces | Simulación walk-forward sobre niveles históricos (±k·σ); diagrama de calibración; Brier | Glasserman (2013); López de Prado (2018) | ◐ |
| ★ HP3 | El ETF sectorial explica una parte importante del movimiento de cada acción, así que la probabilidad de llegar a un objetivo depende en buena medida del sector | R² y β (móvil) del modelo de índice único; descomposición de la varianza en sistemática e idiosincrática | Sharpe (1964); curso VaR III | ✔ |

## Cómo se combinan en el producto
- **Niveles de entrada:** HF (¿barato?) + HT (¿llegará ahí pronto?) + HP como línea base.
- **Niveles de salida:** HF (¿objetivo razonable?) + HP (¿probabilidad y tiempo?) + HP3 (¿depende del sector?).
- **HT0 y HP0** cubren la caminata aleatoria: como rival del SVM y como supuesto del Monte Carlo.

## Pendiente
- Ajustar la redacción con el usuario. Las hipótesis deben ser comprobables con los datos reales; si el EDA muestra que no lo son, se replantean.
- Verificar con DOI las referencias que no aparecen en las diapositivas (Jegadeesh 1990, Bollerslev 1986, Kupiec 1995, Sharpe 1964, Glasserman 2013).
