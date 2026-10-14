# Declaración de uso de IA (borrador; se actualiza durante el proyecto)

> Borrador. Cuando el repositorio esté creado se moverá a su raíz como `USO_IA.md`.

## Herramientas
| Herramienta | Uso |
|---|---|
| Google Gemini (chat) | Ideación inicial del producto con un prompt de "consultor en rediseño de procesos": diagnóstico del proceso actual, cuantificación, rediseño, priorización y hoja de ruta. Redacción del mensaje para el stakeholder y del formulario de 12 preguntas. Transcripción en `Diseño de Asistente Bursátil.txt`. |
| Claude Code (Anthropic, modelo Claude Opus) con el plugin *superpowers* (flujo de brainstorming → spec → plan) | Brainstorming del diseño, revisión de literatura académica (búsqueda web), síntesis del material del curso de Ingeniería Financiera, definición de hipótesis, spec, rúbrica operativa y planes versionados. Más adelante: implementación del código, pruebas y apoyo en la interpretación. |

## Partes en las que se usó IA
| Parte | Tipo de apoyo | Control humano |
|---|---|---|
| Definición del problema y del producto (puntos 1–2) | Ideación y estructuración | Las decisiones las tomó el autor: usuario objetivo, alcance, SVM en vez de Transformers, los 6 niveles de entrada y salida, etc. (ver `docs/bitacora_ideas.md`) |
| Revisión de literatura | Búsqueda y resumen de artículos | Cada cita se verifica con su DOI antes de usarla; se marcan las pendientes |
| Material del curso IIND-4414 | Resumen de diapositivas y scripts R con agentes | Resúmenes en `docs/research/ingenieria_financiera/` |
| Hipótesis y enfoque analítico | Propuesta y discusión | Ajustes del autor (p.ej. reubicar la hipótesis de caminata aleatoria) |
| Implementación | *(se completa al implementar)* | Pruebas automatizadas (pytest) y revisión |
| Interpretación de resultados | *(se completa)* | |
| Documentación (README, reporte, diapositivas) | *(se completa)* | |

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
