# Declaración de uso de IA

Versión final de la primera entrega. Se actualizó durante el proyecto a partir de la bitácora, los planes y los chats.

## Herramientas
| Herramienta | Uso |
|---|---|
| Google Gemini (chat) | Ideación inicial del producto con un prompt de "consultor en rediseño de procesos": diagnóstico del proceso actual, cuantificación, rediseño, priorización y hoja de ruta. Redacción del mensaje para el stakeholder y del formulario de 12 preguntas. Transcripción en `Diseño de Asistente Bursátil.txt`. |
| Claude Code (Anthropic; modelos usados: Claude Opus para orquestación, diseño y revisiones finales; Claude Sonnet para la mayor parte de la implementación y de las revisiones por tarea; Claude Haiku para tareas mecánicas de código) con el plugin *superpowers* (flujo de brainstorming → spec → plan) | Brainstorming del diseño, revisión de literatura académica (búsqueda web), síntesis del material del curso de Ingeniería Financiera, definición de hipótesis, spec, rúbrica operativa y planes versionados. Implementación: módulos de `src/asistente/` con TDD, notebooks 01 a 04, pruebas y ejecución con `uv`. Flujo de desarrollo dirigido por subagentes (*subagent-driven development*): un subagente implementador por tarea y revisiones por tarea (cumplimiento de la especificación y calidad) antes de continuar. Apoyo en la interpretación y en la redacción de `README.md`, `docs/entrega_1/` y `USO_IA.md`. |

## Partes en las que se usó IA
| Parte | Tipo de apoyo | Control humano |
|---|---|---|
| Definición del problema y del producto (puntos 1–2) | Ideación y estructuración | Las decisiones las tomó el autor: usuario objetivo, alcance, SVM en vez de Transformers, los 6 niveles de entrada y salida, etc. (ver `docs/bitacora_ideas.md`) |
| Revisión de literatura | Búsqueda y resumen de artículos | Cada cita se verifica con su DOI antes de usarla; se marcan las pendientes |
| Material del curso IIND-4414 | Resumen de diapositivas y scripts R con agentes | Resúmenes en `docs/research/ingenieria_financiera/` |
| Hipótesis y enfoque analítico | Propuesta y discusión | Ajustes del autor (p.ej. reubicar la hipótesis de caminata aleatoria) |
| Implementación (puntos 5 y 6) | Código de `src/asistente/` (EDGAR, Damodaran, indicadores, etiquetas, riesgo, simulación), notebooks 01 a 04 y `run_all.sh`, escritos por Claude Code en tareas pequeñas con prueba primero | 75 pruebas automatizadas (pytest); cada tarea revisada por un segundo agente; el autor fijó los criterios (sin look-ahead, fecha `filed`, k y N por evidencia) y revisó los resultados. Los notebooks se ejecutan de punta a punta con `run_all.sh` |
| Interpretación de resultados (puntos 6 y 7) | Borradores de las lecturas con cifras, síntesis y conclusiones a partir de las salidas de los notebooks | Las cifras salen de celdas ejecutadas (T7) y cada conclusión cita notebook y sección (T4); el autor decide qué se afirma y mantiene la salvedad de que los resultados son asociativos y que los indicadores técnicos muestran señal débil. Correcciones surgidas de las revisiones: línea base GBM con deriva, IC por bloques de fechas, ajuste por splits |
| Documentación (README, markdowns 1 a 5 y 7, reporte, diapositivas) | Redacción y estructuración a partir de las salidas y de la guía de la entrega | El autor revisa y valida el contenido; los datos de la validación con el stakeholder no se inventan (plantilla por completar tras la sesión) |

## Prompts y momentos clave del flujo
1. Gemini: "quiero que me guíes para diseñar un producto así: asistente de inversiones en el mercado bursátil…" (definición inicial).
2. Claude Code: "quiero usar superpowers para poder completar la entrega 1" (inicio del flujo de brainstorming).
3. "necesitamos consultar literatura académica y basar las decisiones que tomamos en ella… ten en cuenta que esto es una serie de tiempo".
4. "dime 5 cosas que posiblemente esté omitiendo en el plan" (análisis de brechas).
5. "lee el contenido de mi materia de ingeniería financiera… e incluyamos todo lo que nos pueda ayudar".
6. Corrección del autor: "el escenario bajista es de todas formas esperando que la empresa suba de precio" (rediseño del modelo hacia el planteamiento B).
7. "añade las lecciones del taller 1… aplicadas en la forma mas no en su contenido".

## Flujo de trabajo
Brainstorming iterativo (una pregunta a la vez) → bitácora de ideas → planes versionados (`docs/plans/plan_v1…v5`) → spec → plan de implementación → implementación con TDD → revisión del autor.

## Prompts de la fase de implementación (resumidos)
8. "Implementa el plan de la entrega 1 con subagentes: una tarea por subagente, con revisión de cumplimiento de la especificación y de calidad al terminar cada una" (inicio de la implementación).
9. Instrucciones por tarea (resumen): escribir primero la prueba y verla fallar, implementar, ver la prueba en verde, correr la suite completa y hacer el commit con el mensaje indicado; detenerse y reportar si un valor del plan parece incorrecto.
10. Correcciones del autor y de las revisiones: la línea base del SVM debe usar la deriva estimada solo con datos pasados; los intervalos por régimen deben ser por bloques de fechas; los múltiplos deben usar EPS ajustado por splits y precio sin ajuste por dividendos.
11. Conclusiones: "toda cifra del texto debe salir de una celda ejecutada y cada conclusión enlaza el notebook y la sección; toda recomendación se revisa con la pregunta ¿el inversor tiene este dato hoy?" (lecciones T4, T6 y T7).
12. Documentación final: `README.md` con las seis secciones exigidas y el índice actividad -> archivo, y `run_all.sh` para reproducir el análisis.

Los prompts no contienen credenciales ni datos personales; la variable `SEC_USER_AGENT` se documenta solo con un valor de ejemplo.

## Flujo de trabajo en la implementación
Especificación y plan versionados -> tarea -> subagente implementador (TDD, commit) -> revisión de cumplimiento -> revisión de calidad -> correcciones -> siguiente tarea. El autor decide el alcance, las hipótesis, los criterios de aceptación y qué se afirma en los textos.
