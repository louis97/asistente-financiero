# Bitácora de retroalimentación del stakeholder (punto 12)

Stakeholder: el colega inversor (participante 1). Segundo usuario: el autor (participante 2). Organización: el grupo de inversión que forman ambos (ver el reporte §1). Sesgo declarado: el autor es a la vez usuario y diseñador.

## Resumen de las 4 interacciones
| # | Fecha | Modalidad | Estado | Evidencia |
|---|---|---|---|---|
| 1 | fecha por confirmar (entrevista y formulario de diagnóstico) | entrevista y formulario | hecha | `docs/entrega_1/evidencia_diagnostico.md` |
| 2 | 2026-10-18 | asíncrona, pantalla de ejemplo (primera versión) | hecha | `docs/entrega_1/validacion_stakeholder.md` |
| 3 | 2026-11-26 (sesión 2) | asíncrona y virtual | hecha | `docs/entrega_2/12_sesiones/respuestas_sesion2.md` |
| 4 | (sesión 3: 25 o 26 nov) | presencial o asíncrona | planeada | `docs/entrega_2/12_sesiones/respuestas_sesion3.md` |

## Interacción 1 (entrevista y formulario de diagnóstico)
- **Fecha y modalidad:** fecha por confirmar (la evidencia no la registra); entrevista y formulario.
- **Participantes:** participante 1 / participante 2 (anónimos).
- **Qué se mostró o preguntó:** el problema actual de análisis de acciones: tiempo, ventanas abiertas, demora tras un reporte y registro de decisiones.
- **Acuerdos** (problema, producto, enfoque, resultados): ver `docs/entrega_1/evidencia_diagnostico.md` y `docs/entrega_1/01_negocio.md` §1.7.
- **Cambios aplicados** (archivo y sección): objetivos y KPI en `docs/entrega_1/01_negocio.md` §1.6 y §1.7.
- **Cambios aplazados o rechazados y su razón:** la línea base definitiva se midió después, en la sesión 2 (interacción 3).

## Interacción 2 (2026-10-18, asíncrona)
- **Fecha y modalidad:** 2026-10-18, por mensajería; pantalla de ejemplo (primera versión) y formulario.
- **Participantes:** participante 1 (anónimo).
- **Qué se mostró o preguntó:** la pantalla de ejemplo y el formulario de validación. El formulario no se respondió; el participante dio 14 observaciones libres.
- **Acuerdos** (problema, producto, enfoque, resultados): cinco hallazgos (conceptos sin explicar, pantalla sobrecargada, niveles pensados en %, expectativa de un veredicto, formulario atado al contexto); detalle en `docs/entrega_1/validacion_stakeholder.md`.
- **Cambios aplicados** (archivo y sección): pantalla de ejemplo corregida (definiciones, columnas separadas, columna en %); no se adopta el veredicto.
- **Cambios aplazados o rechazados y su razón:** edición de niveles en % (aplazada); prototipo navegable (llega con el dashboard).

## Interacción 3 (sesión 2)
- **Fecha y modalidad:** 2026-11-26, asíncrona y virtual: cada participante respondió por escrito la hoja de la sesión 2 (`docs/entrega_2/12_sesiones/hoja_sesion2.md`), sin audio ni llamada. Las respuestas anónimas están en `docs/entrega_2/12_sesiones/respuestas_sesion2.md`.
- **Participantes:** participante 1 / participante 2 (anónimos).
- **Qué se mostró o preguntó:** 12 preguntas de selección: qué quiere lograr (A1 a A3), cómo analiza hoy (B1 a B5, con los ítems 6.1 a 6.7 sobre la pantalla de ejemplo), cuánto vale esperar en un nivel de compra (C1 a C3) y si encontró los datos de la pantalla (D1).
- **Acuerdos** (problema, producto, enfoque, resultados):
  - **Objetivo general:** A1 a, elegido por los dos (una sola pantalla con el análisis de la acción, para gastar menos tiempo y cambiar menos de pantalla).
  - **Objetivos específicos:** los que marcaron los dos: A2 b (abrir menos páginas o ventanas), A2 e (dejar anotada cada decisión) y A2 f (entender y confiar en lo que muestra la pantalla). A2 c (niveles por múltiplo que se actualizan solos, participante 1) y A2 d (probabilidad con rango y referencia simple, participante 2) tuvieron un voto cada una y se reportan como opciones, no como objetivos.
  - **Mejor forma de medir (A3):** sin acuerdo; el participante 1 eligió los días entre un reporte y los niveles actualizados (KPI 3) y el participante 2 los minutos por acción (KPI 1). Los cinco KPI se conservan.
  - **Línea base de los KPI:** tabla "Mediciones de los KPI". Donde los rangos de los dos no se solapan se reportan ambos, sin promediar.
  - **Razón beneficio/costo:** `docs/entrega_2/12_sesiones/razon_beneficio_costo.json` = mínimo 0,78, central 1,26, máximo 1,97 (la nota del JSON detalla el cálculo; `notebooks/07_modelos.ipynb`, cálculo de valor, lo marca sobre la sensibilidad de 0,5 a 3). Beneficio B = C1; costo C = C2 + C3, con el punto medio de cada categoría (el costo mínimo de cada participante tiene piso de 0,1 %) y el promedio de los dos participantes. Dos decisiones del autor, declaradas: (1) C1 se entendió como cuánto más bajo queda el nivel de compra frente al precio actual; el participante 1 tachó 0–3 % pero agregó la opción "No entiendo", así que su C1 se trató como sin respuesta y B sale solo del participante 2 (12–20 %); (2) el participante 2 respondió C2 con texto libre (espera a que el precio toque el nivel y no persigue el precio), y se tomó C2 = 0 %. Ningún valor se recortó a la rejilla 0,5–3.
- **Cambios aplicados** (archivo y sección): `docs/entrega_1/01_negocio.md` §1.6 y §1.7 (objetivos y línea base confirmados); `notebooks/07_modelos.ipynb` (la sensibilidad del cálculo de valor marca el rango 0,78 / 1,26 / 1,97 sobre la rejilla de 0,5 a 3); `docs/entrega_1/07_conclusiones.md` §7.3 (estado de la línea base).
- **Cambios aplazados o rechazados y su razón:** A1 b, c, d y A2 a, c, d no se adoptan como objetivos (menos de dos votos; las dos de un voto quedan como opciones). Sin cambio en las metas de los KPI (ver la nota bajo la tabla). Limitaciones: dos personas, una es el autor; las respuestas son declaradas, no medidas; la modalidad asíncrona impidió aclarar C1 en el momento.

## Interacción 4 (sesión 3)
- **Fecha y modalidad:**
- **Participantes:** participante 1 / participante 2 (anónimos).
- **Qué se mostró o preguntó:**
- **Acuerdos** (problema, producto, enfoque, resultados):
- **Cambios aplicados** (archivo y sección):
- **Cambios aplazados o rechazados y su razón:**

## Definición de la problemática (acuerdo sobre la organización)
Correo al profesor con la solicitud de aprobar la organización como grupo de inversión con stakeholder identificado, y su respuesta (resumir sin nombres; si no hay respuesta, declarar "se continúa como si fuera positiva").

## Referencia previa de la línea base (entrevista de diagnóstico)
KPI 2 (cambios de pantalla): rango previo 2–15 (colega: 10–15; autor: 2 o más); en la sesión 2 ambos respondieron 3–5 (B2). KPI 1: 2–3 horas por ciclo, unidad por activo pendiente (B1). KPI 4: 0 % (en la sesión 2 el participante 1 declaró lo contrario; ver la nota bajo la tabla).

## Mediciones de los KPI
| KPI | Línea base (sesión 2, 2 participantes) | Medición con el dashboard (sesión 3) | Meta | Lectura (asociación, no causa) |
|---|---|---|---|---|
| 1. Tiempo por activo (mediana de 2 a 3 acciones por participante) | Participante 1: 150 min por acción (2–3 h para 1 acción). Participante 2: 48 min por acción (más de 3 h, tomado como 4 h, para 4–6 acciones, tomado como 5). No se solapan: se reportan ambos. | | menos de 5 min | |
| 2. Cambios de pantalla (máximo) | 3–5 páginas o ventanas por acción (los dos coinciden, B2) | | 1 | |
| 3. Latencia (días; `data/produccion/latencia.csv`) | 3–7 días (los dos coinciden, B3) | | 1 día o menos | |
| 4. Decisiones documentadas (registradas / órdenes puestas) | Participante 1: 10 de 10 (100 %), en hoja de cálculo. Participante 2: 0 de 10 (0 %), en ningún lado. No se solapan: se reportan ambos. | | 100 % | |
| 5. Puntaje medio de los ítems 6.1 a 6.7 (línea base: sobre la pantalla de ejemplo; medición: tras usar el dashboard) y proporción que lo usaría | Rango conjunto por ítem (participante 1 / participante 2): 6.1 3–5, 6.2 4–5, 6.3 3–5, 6.4 3–5, 6.5 3, 6.6 3–4, 6.7 4–5. Puntaje medio: 3,43 (participante 1) y 4,43 (participante 2). | | 4 o más en cada ítem | |

Notas de la línea base (sesión 2):
- KPI 2: el rango previo de la entrevista (2–15) queda reemplazado por el de la sesión 2 (3–5), que viene de la pregunta B2 y de los dos participantes.
- KPI 4: la línea base de la entrega 1 (0 %) venía de "no hay un lugar donde anotar"; la pregunta B4a muestra que el participante 1 sí anota todo (en una hoja de cálculo) y el participante 2 nada. B4a pregunta por el motivo, mientras el KPI 4 pide fecha, nivel, lectura y nota; con esa diferencia, la meta de 100 % se mantiene y se mide con el registro del dashboard.
- KPI 5: la meta (4 o más en cada ítem) no se cumple en la línea base en los ítems 6.1, 6.3, 6.4 y 6.5 del participante 1 y en 6.5 y 6.6 del participante 2; es lo esperado antes de usar el dashboard y la sesión 3 repite los mismos ítems.
- KPI 1: la línea base por acción (48 y 150 min) es de la sesión 2 y reemplaza el supuesto de la entrega 1 de que un ciclo cubre una acción (2 a 3 horas); la meta (menos de 5 minutos) no cambia.

Nota: la parte del KPI 5 "proporción que lo usaría" no tiene línea base (solo se pregunta en la sesión 3).

Limitaciones: dos personas, una es el autor, los rangos son declarados, no medidos.
