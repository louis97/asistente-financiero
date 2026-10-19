# Asistente bursátil para el inversor value colombiano

Primera entrega del proyecto final de MINE-4101 Ciencia de Datos Aplicada (Universidad de los Andes, 2026-II).

Repositorio: <https://github.com/louis97/asistente-financiero>

## 1. Integrantes

| Integrante | Rol |
|---|---|
| Louis Gualtero | Trabajo individual: todos los puntos del enunciado |

**Trabajo individual autorizado por el profesor** (confirmado el 2026-10-14). El enunciado pide equipos de 4; esta entrega la presenta un solo integrante y así se declara también en el video.

## 2. Alcance

Un asistente que apoya la decisión del inversor value colombiano que compra acciones de EE.UU. al contado y solo en largo. Para los tickers que elige el usuario, calcula seis niveles (tres de entrada y tres de salida), cada uno en precio y en múltiplo, con tres lecturas por nivel: **fundamental** (percentil del P/E normalizado y de los ratios de calidad frente a la historia propia y a la industria), **técnica** (probabilidad de un SVM lineal con N = 60 días hábiles frente a la línea base por decil de volatilidad) y **probabilística** (simulación por remuestreo de bloques de semanas de la acción y del XLP al mismo tiempo). Añade un panel de riesgo descriptivo con cinco cifras directas (volatilidad anualizada, percentil 5 semanal, caída máxima, frecuencia de caídas fuertes y dependencia del sector) y un registro de decisiones.

El producto se diseña para servir a cualquier industria; la entrega 1 lo desarrolla y lo valida en una **industria piloto: consumo defensivo**, con 21 empresas del XLP con historia desde 2009 (KO, PEP, PG, WMT, COST, CL, MDLZ, KMB, GIS, MO, PM, HSY, KR, SYY, ADM, CLX, CHD, MKC, STZ, CAG, TSN) más el SPY (mercado) y el XLP (sector). KHC queda fuera por empezar en 2015. **En esta entrega solo se diseñan** el modelo SVM, la API y el dashboard; su construcción y evaluación son parte de la entrega 2. El producto es una herramienta de apoyo y **no constituye una recomendación de inversión** (ver el punto 3).

## 3. Conclusiones (insights)

Detalle y fuentes en [`docs/entrega_1/07_conclusiones.md`](docs/entrega_1/07_conclusiones.md). Las cifras se copian de `data/resultados/nb03.json`, `nb04.json` y `nb04_p4.json`.

1. **Las caídas semanales fuertes no son más frecuentes que las que daría una normal medida igual** (P1): 3,08 % semanal (≈ 1 de cada 32, ≈ 1,6/año), IC95 por bloques de fechas [2,46 %; 3,92 %] (≈ 1,3–2,0/año), umbral 3,83 % (≈ 1 de cada 26, ≈ 2/año); no se rechaza H0, no accionable.
2. **Las acciones baratas suben su P/E normalizado más que las caras a 3 años** (P2): +0,153 anualizado en log, IC95 por empresa [+0,091; +0,221], umbral 0,03; se rechaza H0 y la decisión es accionable. La descomposición de **la diferencia barato − caro** afirma la **trampa de valor como asociación**: Δlog(precio) +0,014 (IC95 [−0,115; +0,155], cruza 0) y Δlog(EPS prom 3a) −0,444 (IC95 [−0,693; −0,210], excluye 0).
3. **El quintil barato no gana al XLP a 3 años** dentro del sector (P3): +0,006, IC95 [−0,032; +0,049]; no se rechaza H0.
4. **No hay evidencia de que algún indicador técnico mejore, de forma lineal, la AUC del modelo de magnitud** (P4): los 7 ΔAUC frente al modelo A (AUC 0,577 en la submuestra) tienen IC95 Bonferroni al ≈ 99,3 % que cruzan 0. Consecuencia: `variables_svm = {|r_t|, σ20/σ252, σ252}` (solo magnitud); la base del SVM (decil de σ, todas las filas) da **AUC 0,591** con N = 60. La entrega 2 prueba el **SVM RBF** para captar aportes no lineales.
5. **El XLP agrega poder explicativo semanal al SPY** (P5): ΔR² mediano 0,225, IC95 [+0,175; +0,291]; se rechaza H0 (confirmatoria: la industria piloto se eligió viendo este ΔR²).
6. **La turbulencia se agrupa, pero su magnitud es incierta** (P6): P(T|T) diaria 0,305 (IC95 [0,275; 0,340], umbral 0,30); se rechaza H0, decisión de negocio "efecto real, pero de magnitud incierta". Semanal análogo (0,282).
7. **Decisiones de diseño que se derivan**: niveles medidos en k·σ252 diaria con N = 60 días hábiles; simulación por remuestreo de **bloques de semanas** de la acción y del XLP al mismo tiempo; el exceso sobre el XLP **no entra como señal**; percentil del P/E normalizado como lectura principal con advertencia descriptiva de posible deterioro de utilidades; fuera del piloto, el panel se marca "industria no validada".

## 4. Organización del repositorio

```
proyecto_final/
├── README.md, USO_IA.md, run_all.sh, pyproject.toml, uv.lock
├── notebooks/      01_recoleccion -> 02_calidad -> 03_eda_univariado -> 04_eda_multivariado
│                   (comunes.py: funciones que usan dos o más notebooks)
├── data/
│   ├── snapshots/  instantáneas parquet con fecha y metadatos (.meta.json)
│   └── resultados/ nb03.json, nb04.json, nb04_p4.json (cifras del punto 7)
├── docs/entrega_1/ 01_negocio ... 07_conclusiones, glosario, evidencia_diagnostico,
│                   validacion_stakeholder, 05_diccionario_datos (punto 5.3)
├── scripts/        mockup.py (genera el mockup del dashboard)
└── entregables/entrega_1/   reporte.md/.pdf, presentacion.pptx, assets/
```

El análisis vive **inline en los notebooks**, con comentarios y lecturas con cifras. Solo lo que usan dos o más notebooks va a `notebooks/comunes.py`. No hay pruebas automáticas; la verificación es la ejecución de los notebooks de punta a punta y las rondas de revisión paralela por fase (ver [`USO_IA.md`](USO_IA.md) para el flujo con IA).

### Índice de actividades del enunciado (punto → archivo)

| Punto del enunciado | Dónde está |
|---|---|
| 1. Problema y entendimiento del negocio | [`docs/entrega_1/01_negocio.md`](docs/entrega_1/01_negocio.md) |
| 2. Ideación del producto de datos | [`docs/entrega_1/02_ideacion.md`](docs/entrega_1/02_ideacion.md); mockup v2: [`entregables/entrega_1/assets/mockup.png`](entregables/entrega_1/assets/mockup.png) (v1 archivado en [`mockup_v1.png`](entregables/entrega_1/assets/mockup_v1.png)), generado por [`scripts/mockup.py`](scripts/mockup.py); registro de la validación con el stakeholder: [`docs/entrega_1/validacion_stakeholder.md`](docs/entrega_1/validacion_stakeholder.md) |
| 3. Aspectos éticos y legales | [`docs/entrega_1/03_etica_legal.md`](docs/entrega_1/03_etica_legal.md) |
| 4. Enfoque analítico (hipótesis P1–P6) | [`docs/entrega_1/04_enfoque_analitico.md`](docs/entrega_1/04_enfoque_analitico.md) |
| 5. Recolección de datos | [`notebooks/01_recoleccion.ipynb`](notebooks/01_recoleccion.ipynb), [`data/snapshots/`](data/snapshots) y [`docs/entrega_1/05_diccionario_datos.md`](docs/entrega_1/05_diccionario_datos.md) |
| 6. Entendimiento de los datos (calidad y EDA) | [`notebooks/02_calidad.ipynb`](notebooks/02_calidad.ipynb), [`notebooks/03_eda_univariado.ipynb`](notebooks/03_eda_univariado.ipynb), [`notebooks/04_eda_multivariado.ipynb`](notebooks/04_eda_multivariado.ipynb) |
| 7. Conclusiones iniciales | [`docs/entrega_1/07_conclusiones.md`](docs/entrega_1/07_conclusiones.md); cifras: [`data/resultados/`](data/resultados) |
| Uso de IA | [`USO_IA.md`](USO_IA.md) |
| Glosario (términos del dominio) | [`docs/entrega_1/glosario.md`](docs/entrega_1/glosario.md) |

## 5. Instrucciones de ejecución

Requisitos: [uv](https://docs.astral.sh/uv/) y Python 3.12 (uv lo instala). Para generar el reporte en PDF (opcional): `pandoc` y `tectonic` (`brew install pandoc tectonic`).

```bash
git clone https://github.com/louis97/asistente-financiero.git
cd asistente-financiero
uv sync
# Reproducir el análisis sin red, con las instantáneas versionadas en data/snapshots:
bash run_all.sh
# Volver a descargar los datos (solo necesario si se quiere refrescar la instantánea):
export SEC_USER_AGENT="Nombre correo"   # sustitúyalo por su nombre y su correo; la SEC lo exige
RUN_DOWNLOAD=1 bash run_all.sh
```

`run_all.sh` ejecuta `uv sync` y los 4 notebooks en orden con `nbconvert --execute`. Por defecto **no descarga**: el notebook 01 carga las instantáneas versionadas de `data/snapshots/`. Con `RUN_DOWNLOAD=1` el notebook 01 refresca la instantánea desde yfinance, SEC EDGAR y Damodaran. Al final, `scripts/mockup.py` regenera el mockup.

Para regenerar el reporte PDF:

```bash
cd entregables/entrega_1
pandoc reporte.md -o reporte.pdf --pdf-engine=tectonic
```

La presentación se diseñó aparte con el tipo Slides de claude.ai y se exporta como `.pptx` directamente desde esa herramienta (no se regenera con pandoc).

## 6. Dependencias

Definidas en [`pyproject.toml`](pyproject.toml) y fijadas en [`uv.lock`](uv.lock) (Python ≥ 3.12): `matplotlib`, `numpy`, `openpyxl`, `pandas`, `pyarrow`, `requests`, `scikit-learn`, `scipy`, `seaborn`, `statsmodels`, `xlrd`, `yfinance`. Desarrollo: `ipykernel`, `jupyter`, `nbconvert`.

## 7. Técnicas no cubiertas en clase

El enunciado exige informar las técnicas o herramientas no cubiertas durante la clase. En este proyecto son 15 y se usan de forma puntual: bootstrap por bloques de fechas, nulo calibrado por simulación, ΔAUC con regresión logística, errores estándar agrupados por empresa, Brier y diagrama de calibración, análisis de potencia (MDE), EPS TTM reconstruido con los 10-Q, SVM, simulación por remuestreo de bloques, Bonferroni, Holm, VIF, prueba F de modelos anidados, Mann-Whitney y clustermap de seaborn. **La lista detallada, con la justificación de cada técnica, vive solo en [`docs/entrega_1/03_etica_legal.md`](docs/entrega_1/03_etica_legal.md) §3.3** (fuente única).

## 8. Entregables

- Reporte PDF (≤ 6 páginas, Arial 12, carta, una columna): [`entregables/entrega_1/reporte.pdf`](entregables/entrega_1/reporte.pdf).
- Diapositivas: [`entregables/entrega_1/presentacion.pptx`](entregables/entrega_1/presentacion.pptx) (incluye las notas del orador con el diálogo).
- Video en YouTube (≤ 6 min, trabajo individual autorizado): <https://youtu.be/NGZdh3TD46E>.
