# Declaración de uso de IA

Los commits no llevan atribución; el uso de IA se declara aquí.

## Herramientas

| Herramienta | Uso |
|---|---|
| Asistente de IA conversacional (Google Gemini) | Ideación inicial del producto con un prompt de "consultor en rediseño de procesos": diagnóstico del proceso actual, cuantificación, rediseño y priorización. También se usó para redactar el mensaje al participante y el formulario de 12 preguntas. La transcripción no se incluye en el repositorio (menciona a terceros); el resumen de respuestas vive en [`docs/entrega_1/evidencia_diagnostico.md`](docs/entrega_1/evidencia_diagnostico.md). |
| Claude Code (Anthropic) con el plugin `superpowers` | Orquestación del flujo brainstorming → spec → plan → implementación → revisión por tarea → revisión paralela por fase. El **orquestador principal** corrió en un modelo superior (Claude Sonnet 4.5 / 4.7); los **subagentes** (implementadores, revisores y exploradores) corrieron fijos en **Claude Opus 4.8** (en algunas ventanas la API lo atiende como 4.7, aceptado por el autor el 2026-10-16). Se usó en la implementación de los 4 notebooks, en la escritura inicial de los documentos de `docs/entrega_1/` y en la generación del mockup y los entregables. La bitácora, la spec, los planes y las rondas de revisión versionadas se guardan en un repositorio privado del autor y no viajan con el repositorio público. |

## En qué partes se usó

| Parte | Tipo de apoyo | Control humano |
|---|---|---|
| Definición del problema y del producto (puntos 1 y 2) | Ideación y estructuración con el asistente conversacional y con Claude Code | Las decisiones las tomó el autor: usuario objetivo, alcance, seis niveles de entrada y salida, industria piloto. Se registran en la bitácora de ideas del autor (repositorio privado). |
| Revisión de literatura (puntos 1 y 3) | Búsqueda y resumen de artículos académicos y normas | Cada cita se verifica con su DOI o URL oficial antes de usarse. |
| Hipótesis y enfoque analítico (punto 4) | Propuesta y discusión de P1–P6 con la plantilla de inferencia descrita en `docs/entrega_1/04_enfoque_analitico.md` | El autor fijó los umbrales antes de ejecutar, con cada decisión declarada ("se rechaza H0" / "no se rechaza H0") y revisada en las rondas de revisión del repositorio privado. |
| Implementación (puntos 5 y 6) | Código **inline en los notebooks** (recolección, calidad, EDA univariado y multivariado), con comentarios y lecturas con cifras. Lo que usan dos o más notebooks vive en `notebooks/comunes.py`. No hay pruebas automáticas. | El autor fijó las reglas (sin look-ahead, fecha `filed` de los reportes, ventana expansiva, universo del piloto) y revisó los resultados con cuatro revisiones paralelas (consolidado en el repositorio privado). Los notebooks se ejecutan de punta a punta con `bash run_all.sh`. |
| Interpretación de resultados (puntos 6 y 7) | Borradores de las lecturas con cifras, síntesis y conclusiones a partir de las salidas de los notebooks y de `data/resultados/*.json` | Las cifras salen de celdas ejecutadas; cada conclusión cita el notebook y la sección. El autor decide qué se afirma y mantiene la salvedad de que los resultados son asociativos. |
| Documentación (README, markdowns del punto 1 al 7, reporte, diapositivas, guion del video) | Redacción y estructuración a partir de las salidas del análisis | El autor revisa y valida el contenido; los datos de la validación con el stakeholder no se inventan (el registro recoge solo lo que el participante dijo en la sesión asíncrona del 2026-10-18). El feedback del participante sobre la legibilidad de los textos generados con IA motivó revisar y acortar las partes narrativas. |

## Prompts más relevantes

1. Asistente conversacional: "quiero que me guíes para diseñar un producto así: asistente de inversiones en el mercado bursátil…" (definición inicial del producto).
2. Claude Code: "quiero usar superpowers para poder completar la entrega 1" (inicio del flujo).
3. "añade las lecciones del taller 1 aplicadas en la forma, no en el contenido" (aterrizaje del enunciado).
4. **Reencuadre del alcance**: "este proyecto es para un compañero sin formación en finanzas; nada de modelos econométricos ni de ingeniería financiera; una hipótesis por pregunta de negocio" (reescritura total del enfoque analítico).
5. "las decisiones se escriben como 'se rechaza H0' o 'no se rechaza H0'; cada prueba lleva su matriz de supuestos y, con observaciones dependientes, la decisión sale del IC por bootstrap".
6. "toda cifra del texto debe salir de una celda ejecutada y cada conclusión enlaza su notebook y su sección; toda recomendación pasa la pregunta '¿el inversor tiene este dato hoy?'".
7. "no quiero empezar el desarrollo y encontrarme con notebooks o documentos que referencian datos inexistentes, ideas descartadas, afirmaciones sin evidencia o inconsistencias" (consigna de la revisión paralela de cierre de cada fase).

## Flujo de trabajo

Brainstorming iterativo (una pregunta a la vez) → bitácora de ideas → spec → plan versionado → implementación por tareas con revisión por tarea (hasta 5 rondas de corrección con re-revisión) → cierre de fase con **revisión paralela de 4 revisores** (todos en Claude Opus 4.8 / 4.7) y un consolidado por fase. La bitácora, la spec, los planes y las revisiones viven en un repositorio privado del autor y no se publican. Antes de declarar cualquier cosa terminada, se ejecutan los notebooks y se muestra la evidencia. El modelo del orquestador principal es superior al de los subagentes (regla de operación del proyecto).

## Verificación

- Las cifras del reporte, de las diapositivas y del README coinciden con `docs/entrega_1/07_conclusiones.md` y con los JSON de `data/resultados/`.
- Los notebooks se ejecutan sin errores en el orden 01 → 02 → 03 → 04 (comprobado con `bash run_all.sh`).
- Las técnicas no cubiertas en clase se declaran en [`docs/entrega_1/03_etica_legal.md`](docs/entrega_1/03_etica_legal.md) §3.3 (fuente única).
