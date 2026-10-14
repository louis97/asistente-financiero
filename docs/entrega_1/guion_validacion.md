# Guion de validación del mockup con el stakeholder

**Duración:** 15–20 minutos. **Formato:** el entrevistador comparte el mockup (`entregables/entrega_1/assets/mockup.png`) y anota las respuestas en `validacion_stakeholder.md`. **Quién lo realiza:** el autor del proyecto con su inversor (stakeholder del punto 1). Los valores del mockup son ilustrativos y así se le dice al participante antes de empezar.

**Introducción (1 minuto).** Se explica que el objetivo es evaluar el diseño y no al participante, que no hay respuestas correctas y que los datos del mockup son inventados. Se pide autorización para registrar sus respuestas de forma anonimizada, con la finalidad académica del curso y el derecho a retirarlas (Ley 1581 de 2012, arts. 4 y 12; ver `03_etica_legal.md`).

## Parte 1. Tareas sobre el mockup (7–8 minutos)

Cada tarea se plantea en voz alta mientras el participante mira el mockup. El entrevistador anota qué elemento mira, qué dice y dónde duda; no explica nada hasta que el participante termine.

1. "Tienes esta pantalla delante hoy. ¿Qué nivel de entrada mirarías primero y por qué?"
2. "¿Qué te dice la columna de probabilidad del SVM? ¿Qué harías con ese número?"
3. "¿Qué entiendes por la columna de percentil histórico y la de percentil en la industria? ¿Un percentil bajo te dice que la acción está barata?"
4. "Sale un reporte trimestral y los niveles por múltiplo se recalculan solos. ¿Qué esperarías ver en la pantalla para enterarte de que cambiaron?"
5. "En la columna de Monte Carlo, ¿entiendes la separación entre la parte del sector y la parte propia de la empresa? ¿Te sirve para decidir?"
6. "Mira el panel de riesgo. ¿Qué número usarías en 5 segundos y cuál no entiendes o no usarías?"
7. "¿Encuentras todo lo que necesitas para decidir en esta sola pantalla? ¿Qué haces hoy que aquí no puedes hacer?"

## Parte 2. Claridad, confianza y explicabilidad (5–6 minutos)

Escala de 1 a 5 (1 = nada de acuerdo, 5 = totalmente de acuerdo). Se pide una frase de justificación por cada puntuación.

| # | Afirmación | Dimensión |
|---|---|---|
| 2.1 | Entiendo qué significa cada uno de los seis niveles. | Claridad |
| 2.2 | Entiendo la diferencia entre la lectura fundamental, la técnica y la probabilística. | Claridad |
| 2.3 | La pantalla me deja ver rápido qué nivel merece atención. | Claridad |
| 2.4 | Confiaría en la probabilidad del SVM para decidir el momento de una compra. | Confianza |
| 2.5 | Confiaría más en la probabilidad si veo la línea base (probabilidad de una caminata aleatoria) y los errores históricos del modelo. | Confianza (Dietvorst et al., 2015; Parasuraman & Manzey, 2010) |
| 2.6 | Si el modelo me muestra qué indicadores pesaron en su estimación, me siento en condiciones de contradecirlo. | Explicabilidad |
| 2.7 | Prefiero ajustar yo mismo los niveles y los umbrales a recibir niveles calculados por el modelo. | Control (Dietvorst et al., 2016) |
| 2.8 | Una etiqueta de "compra" o "venta" me daría más confianza que una probabilidad con su incertidumbre. | Presentación del score |
| 2.9 | El aviso de que no es asesoría de inversión me resulta claro y visible. | Transparencia |

Preguntas abiertas de cierre de la parte: "¿Qué te haría dejar de confiar en esta herramienta?" y "¿Qué evidencia de desempeño necesitarías ver antes de usarla con dinero real?".

## Parte 3. Cambios que pediría (3–4 minutos)

1. "Si pudieras cambiar tres cosas de esta pantalla, ¿cuáles serían?"
2. "¿Hay algo en la pantalla que quitarías porque estorba?"
3. "¿Qué falta? (por ejemplo ratios que usas hoy y no aparecen)"
4. "¿Para qué usarías esta herramienta: antes de comprar, tras un reporte, o ambos?"
5. Cierre: "Si esta pantalla existiera, ¿en qué momento de tu semana la abrirías?"

## Qué se hace después de la sesión

El autor completa `validacion_stakeholder.md` el mismo día, con la fecha de la sesión y el participante anonimizado. Cada cambio que el participante pida se clasifica como aceptado, aplazado o rechazado con su razón, y los aceptados se reflejan en el mockup, en `scripts/mockup.py` y en la sección "Validación con el stakeholder" de `02_ideacion.md`. Los comentarios que no cambian el diseño también se registran, porque la rúbrica pide que el feedback documentado tenga una consecuencia visible.
