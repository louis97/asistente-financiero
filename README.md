# Asistente bursátil para el inversor value colombiano

Primera entrega del proyecto final de MINE-4101 (Ciencia de Datos Aplicada, Universidad de los Andes).
Repositorio: <https://github.com/louis97/asistente-financiero>

## 1. Integrantes

| Integrante | Rol |
|---|---|
| Louis Gualtero | Trabajo individual: todos los puntos del enunciado |

## 2. Alcance

Un asistente para un inversor value colombiano que compra acciones de EE. UU. El usuario define seis
niveles (tres de entrada y tres de salida), cada uno en precio y en múltiplo. Para cada nivel el
asistente da tres lecturas: el percentil del múltiplo implícito en la historia y la industria; la
probabilidad de un SVM de que el precio toque el nivel de entrada en 12 semanas antes de escaparse
hacia arriba (triple barrera solo-largo, k = 1, N = 12), frente a su línea base (tasa de toque por decil de σ_t; el GBM con deriva queda como referencia teórica); y la
probabilidad de un Monte Carlo de índice único, con y sin el componente del sector. Añade un panel
de riesgo y un registro de decisiones.

Esta primera entrega cubre los puntos 1 a 7: problema, ideación, ética, enfoque analítico,
recolección de datos, entendimiento de los datos (calidad y EDA) y conclusiones. **No incluye el
modelo SVM ni el Monte Carlo**, que son de la entrega final. Universo: 30 acciones (10 de tecnología,
10 de consumo defensivo y 10 financieras) y 4 ETF (SPY, XLK, XLP, XLF), con datos semanales desde 2009.
El producto es de apoyo a la decisión y no constituye una recomendación de inversión.

## 3. Conclusiones (insights)

Detalle y fuentes en [`docs/entrega_1/07_conclusiones.md`](docs/entrega_1/07_conclusiones.md).

1. **Volatilidad agrupada y colas pesadas (HP0 y HT4 apoyadas).** ν mediano 4.15; GARCH-t supera a la volatilidad constante en 28 de 34 series (QLIKE 3.713 frente a 3.883).
2. **La caminata aleatoria no se sostiene como regla (HT0 no apoyada), y P_GBM no está calibrada (HT0 calibración no apoyada).** Pasan 15 de 30 tickers (con Ljung-Box sobre residuos de GARCH-t serían 26 de 30, desviación que la regla no contempla). Con k = 1, N = 12, el GBM con μ = 0 sobreestima la clase 1 en 9.5 pp y el GBM con deriva pasada, en 0.8 pp; la pendiente de calibración es b = −0.294 (IC −0.641 a −0.011). Queda como referencia teórica del SVM; el rival que decide HT1 (preparada) es la tasa empírica de toque por decil de σ_t, con etiquetas resueltas antes de t (cambio fijado antes de evaluar HT1).
3. **Indicadores técnicos: no separan las clases (HT2 no concluyente) y su signo no es estable con la convención adoptada (HT3 no apoyada).** AUC 0.496–0.514, ningún IC por bloques de fechas excluye 0.5; sube a 0.64–0.79 solo en COVID y 2022 (puntos sin IC).
4. **El sector importa (HP3 apoyada).** IC de β excluye 0 en 30 de 30; R² mediano del modelo de índice único 0.525 (financieras 0.700, tecnología 0.387).
5. **Los múltiplos no revierten como regla general (HF1 y HF2 no apoyadas).** 7 de 29 tickers (HF1) y 10 de 29 (HF2); calidad y valoración (HF3) y d₂ de Merton (HF4) no concluyentes.
6. **El VaR no está bien calibrado (HP1 no apoyada).** Excepciones del 95 % fuera de muestra: 7.49 % (GARCH-t) y 6.78 % (histórico).
7. **Datos aptos para riesgo, incompletos para fundamentales (HF5 apoyada).** Utilidad bruta ausente en 16 de 30 emisores; 6 de 6 cifras coinciden con el 10-K.

Decisiones de diseño que se derivan: etiqueta k = 1, N = 12; volatilidad GARCH-t/EWMA con innovaciones t;
rival del SVM: tasa empírica de toque por decil de σ_t (etiquetas con t' + N ≤ t, cortes expansivos), con el GBM con deriva ≤ t como referencia teórica (no calibrado, b < 0; HT1 y HP2 preparadas, pendientes de la entrega final); 5 indicadores retenidos (`rsi14`, `dist_sma20`, `vol_rel20`, `donchian20`,
`mom_12_1`) más σ_t y rasgos de régimen calculados hacia atrás; ratios propios para financieras; percentil de múltiplos solo como contexto.

## 4. Organización del repositorio

```
proyecto_final/
├── README.md, USO_IA.md, run_all.sh, pyproject.toml, uv.lock
├── src/asistente/     datos, edgar, damodaran, fundamentales, indicadores, etiquetas, riesgo, simulacion, config
├── tests/             pytest por módulo (series sintéticas)
├── notebooks/         01_recoleccion -> 02_calidad -> 03_eda_series -> 04_eda_relaciones (orden de ejecución)
├── data/snapshots/    instantáneas parquet con fecha y metadatos (.meta.json)
├── docs/
│   ├── entrega_1/     01_negocio ... 07_conclusiones, guion_validacion, validacion_stakeholder
│   ├── guia_entrega_1.md, hipotesis.md, bitacora_ideas.md
│   ├── research/, plans/, superpowers/   (literatura, planes y especificación)
├── scripts/           mockup.py (genera el mockup)
└── entregables/entrega_1/   [reporte.pdf](entregables/entrega_1/reporte.pdf), presentacion.pptx, assets/ (mockup y figuras de los notebooks)
```

## 5. Instrucciones de ejecución

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12 (uv lo instala).

```bash
git clone https://github.com/louis97/asistente-financiero.git
cd asistente-financiero
uv sync
# Solo para volver a descargar los datos (notebook 01):
export SEC_USER_AGENT="Nombre correo"   # sustituya por su nombre y su correo; la SEC lo exige
./run_all.sh                            # descarga, pruebas y notebooks 01 a 04
# Sin red ni descarga, con las instantáneas versionadas de data/snapshots:
RUN_DOWNLOAD=0 ./run_all.sh
```

`run_all.sh` ejecuta `uv sync`, `uv run pytest -q` y los notebooks en orden con `nbconvert --execute`.
Con `RUN_DOWNLOAD=0` omite el notebook 01 y reproduce 02 a 04 desde las instantáneas.
Orden de los notebooks: **01** recolección (punto 5) -> **02** calidad -> **03** EDA de series ->
**04** EDA de relaciones (punto 6). Las figuras se guardan en `entregables/entrega_1/assets/`.

## 6. Dependencias

Definidas en [`pyproject.toml`](pyproject.toml) y fijadas en `uv.lock` (Python >= 3.12):
`arch`, `matplotlib`, `numpy`, `openpyxl`, `pandas`, `pyarrow`, `requests`, `scikit-learn`, `scipy`,
`seaborn`, `statsmodels`, `xlrd`, `yfinance`. Desarrollo: `ipykernel`, `jupyter`, `nbconvert`, `pytest`.
Para generar el reporte en PDF (opcional): `pandoc` y `tectonic` (`brew install pandoc tectonic`).

## 7. Índice de actividades del enunciado

| Punto del enunciado | Implementación | Interpretación |
|---|---|---|
| 1. Problema y entendimiento del negocio | n/a | [`docs/entrega_1/01_negocio.md`](docs/entrega_1/01_negocio.md) |
| 2. Ideación del producto de datos | [`mockup.png`](entregables/entrega_1/assets/mockup.png), [`scripts/mockup.py`](scripts/mockup.py) | [`docs/entrega_1/02_ideacion.md`](docs/entrega_1/02_ideacion.md); validación: [`guion_validacion.md`](docs/entrega_1/guion_validacion.md), [`validacion_stakeholder.md`](docs/entrega_1/validacion_stakeholder.md) |
| 3. Aspectos éticos y legales | n/a | [`docs/entrega_1/03_etica_legal.md`](docs/entrega_1/03_etica_legal.md) |
| 4. Enfoque analítico | n/a | [`docs/entrega_1/04_enfoque_analitico.md`](docs/entrega_1/04_enfoque_analitico.md), a partir de [`docs/hipotesis.md`](docs/hipotesis.md) |
| 5. Recolección de datos | [`notebooks/01_recoleccion.ipynb`](notebooks/01_recoleccion.ipynb), [`src/asistente/`](src/asistente/), [`data/snapshots/`](data/snapshots/) | En el notebook 01 y [`docs/entrega_1/05_diccionario_datos.md`](docs/entrega_1/05_diccionario_datos.md) |
| 6. Entendimiento de los datos: calidad | [`notebooks/02_calidad.ipynb`](notebooks/02_calidad.ipynb) | Lecturas y síntesis dentro del notebook (matriz de decisiones, sección 7) |
| 6. EDA nivel 1 (series de tiempo) | [`notebooks/03_eda_series.ipynb`](notebooks/03_eda_series.ipynb) | Lecturas y síntesis dentro del notebook (síntesis general, sección 10) |
| 6. EDA niveles 2 y 3 (relaciones, sector, valoración) | [`notebooks/04_eda_relaciones.ipynb`](notebooks/04_eda_relaciones.ipynb) | Lecturas y síntesis dentro del notebook (estado de hipótesis, sección 11) |
| 7. Conclusiones | n/a (cifras tomadas de los notebooks 02 a 04) | [`docs/entrega_1/07_conclusiones.md`](docs/entrega_1/07_conclusiones.md) |
| Pruebas del código | [`tests/`](tests/) | `uv run pytest -q` |
| Uso de IA | n/a | [`USO_IA.md`](USO_IA.md) |
| Guía de criterios y lecciones | n/a | [`docs/guia_entrega_1.md`](docs/guia_entrega_1.md) |

## 8. Entregables

- Reporte PDF (máximo 6 páginas): [`entregables/entrega_1/reporte.pdf`](entregables/entrega_1/reporte.pdf).
- Video en YouTube: (pendiente).
- Diapositivas: [`entregables/entrega_1/presentacion.pptx`](entregables/entrega_1/presentacion.pptx); versión PDF: pendiente de exportar.
