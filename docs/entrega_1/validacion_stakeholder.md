# Registro de la sesión de validación con el stakeholder

## Datos de la sesión

- **Fecha:** 2026-10-18.
- **Modalidad:** asíncrona, por mensajería. Se envió al participante el mockup v1 ([`assets/mockup_v1.png`](../../entregables/entrega_1/assets/mockup_v1.png)) y el formulario ([`guion_validacion.md`](guion_validacion.md)), sin contexto adicional.
- **Participante:** un inversor value (anónimo). No se registran nombre, contacto ni montos.
- **Autorización informada:** Ley 1581 de 2012, arts. 4, 8, 9 y 12. Aceptada verbalmente antes del envío.
- **Resultado:** el formulario no se respondió. El participante dio **feedback libre** (14 observaciones), porque las preguntas del formulario le parecieron demasiado atadas al contexto del autor y del asistente conversacional usado para redactarlas.

## Hallazgos y decisiones

Las 14 observaciones se agrupan en cinco hallazgos. "Aceptado ahora" significa aplicado en el mockup v2 ([`assets/mockup.png`](../../entregables/entrega_1/assets/mockup.png)) y/o en este punto; "aplazado" se recoge en el [punto 7](07_conclusiones.md) §7.4.

| Hallazgo | Decisión | Razón y cambio |
|---|---|---|
| H1. Los conceptos no se explican: P/E, P/B, "consumo defensivo", "probabilística" ni de dónde sale el valor del SVM. | Aceptado ahora | Se agrega una franja "Cómo leer esta pantalla" con 7 definiciones de una línea; la columna técnica se rotula "modelo SVM, se entrena en la entrega 2". Mockup v2. |
| H2. El mockup está sobrecargado: columna Fundamental con nombre largo y texto generado, P/E y P/B juntos, panel de riesgo comprimido. | Aceptado ahora | P/E y P/B en columnas separadas; la columna Fundamental solo muestra el valor y la interpretación pasa a tres notas numeradas bajo la tabla; el panel de riesgo queda con 5 filas espaciadas y una línea de ayuda. Mockup v2. |
| H3. El modelo mental de los niveles es otro: el participante los piensa como % de ganancia, no como precios escritos a mano. | Parcial: columna % aceptada ahora; edición en % aplazada | Se agrega la columna "% vs. precio actual" en cada nivel; los niveles siguen definidos en precio y múltiplo (RF1). La edición en % se evalúa en la entrega 2. |
| H4. Espera un veredicto ("¿está en un precio aceptable?"). | No se adopta; se mitiga | Choca con RN1 y con la regla de no recomendar ([punto 3](03_etica_legal.md)). La marca del precio actual lleva una frase descriptiva ("entre $67 y $76"), nunca un veredicto. |
| H5. La validación con un formulario atado al contexto y una imagen estática pierde contexto; un reporte generado por un LLM es difícil de leer sin contexto. | Aplazado + aplicado | Un mockup navegable con pruebas de usabilidad se registra como acción próxima en el punto 7. Los textos del reporte y de este registro se redactaron sin apoyarse en generación automática de párrafos. |

## Línea base de los KPI y limitaciones

- **KPI 1, 2 y 5:** la línea base no se obtuvo en esta sesión (el participante no respondió el formulario con las preguntas del punto 4 del guion). Queda como acción próxima.
- **Limitaciones:** una sola persona, no representativa; sesión asíncrona sin posibilidad de aclarar en vivo; el feedback se recibió sobre el mockup v1 (la única diferencia con [`mockup_v1.png`](../../entregables/entrega_1/assets/mockup_v1.png) es el pie, corregido antes del envío).
