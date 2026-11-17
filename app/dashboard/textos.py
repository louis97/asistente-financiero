"""Textos fijos de la pantalla: glosario de bolsillo, ayudas (tooltips), leyenda legal y avisos.
Las definiciones salen de docs/entrega_1/glosario.md, en una línea y en lenguaje llano."""

DISCLAIMER = "No es asesoría de inversión."
LEYENDA_ASESORIA = ("El contenido de la presente comunicación o mensaje no constituye una recomendación profesional para "
                    "realizar inversiones en los términos del artículo 2.40.1.1.2 del Decreto número 2555 de 2010 o las "
                    "normas que lo modifiquen, sustituyan o complementen")
SUBTITULO_BANNER = "Herramienta de apoyo: muestra probabilidades con su incertidumbre y deja la decisión al usuario."

ALGORITMOS = {"arbol": "árbol de decisión", "svm_lineal": "SVM lineal", "svm_rbf": "SVM con núcleo RBF"}
PERIODO_PRUEBA = "2019 en adelante"

GLOSARIO_BOLSILLO = {
    "P/E": "precio ÷ utilidad por acción (TTM = últimos 12 meses). Dice cuántos dólares se pagan por cada dólar de utilidad.",
    "P/B": "precio ÷ patrimonio por acción. Dice cuántos dólares se pagan por cada dólar de patrimonio contable.",
    "percentil": "«entre los valores pasados, ¿en qué puesto queda el de hoy?». p6 = más barato que el 94 % de su historia.",
    "industria piloto": "consumo defensivo (alimentos, bebidas, aseo personal y del hogar, y tabaco): productos que la gente "
                        "consume en cualquier fase del ciclo económico.",
    "modelo técnico": "un árbol de decisión simple que estima la probabilidad de tocar el nivel a partir de la volatilidad "
                      "reciente y de la distancia del nivel; se eligió entre árbol, SVM lineal y SVM RBF.",
    "lectura técnica": "probabilidad de que el precio toque el nivel en 60 días hábiles, con el modelo técnico. Solo en entradas.",
    "lectura probabilística": "probabilidad de que el precio alcance la salida en el horizonte de 52 semanas, por simulación "
                              "con la historia. Solo en salidas.",
    "línea base": "frecuencia histórica con la que el precio tocó niveles a la misma distancia en días de volatilidad parecida. "
                  "Si el modelo no la supera, no aporta.",
}

TOOLTIPS = {
    "AUC": "Qué tan bien el modelo separa los casos en que el precio sí tocó el nivel de los que no: 0,5 es azar y 1 es separación perfecta.",
    "ΔAUC": "AUC del modelo menos AUC de la línea base: si es positivo, el modelo ordena mejor que la línea base.",
    "Brier": "Error cuadrático medio de las probabilidades frente a lo que pasó: va de 0 a 1 y menos es mejor.",
    "calibración": "Compara la probabilidad que da el modelo con la frecuencia real: un modelo calibrado que dice 20 % acierta cerca de 2 de cada 10 veces.",
    "línea base": GLOSARIO_BOLSILLO["línea base"],
    "percentil": GLOSARIO_BOLSILLO["percentil"],
    "σ (volatilidad)": "Cuánto se mueve el precio: la desviación típica de los retornos diarios del último año, expresada en términos anuales.",
    "P/E": GLOSARIO_BOLSILLO["P/E"],
    "P/B": GLOSARIO_BOLSILLO["P/B"],
    "P/E normalizado": "Precio ÷ utilidad promedio de los últimos 3 años: evita que un solo año excepcional haga ver barata a una acción.",
    "R²": "Fracción del movimiento del precio que explican el mercado y el sector; va de 0 a 1.",
    "ΔR²": "Cuánto mejora esa explicación al añadir el sector a la del mercado; es la dependencia del sector que el mercado solo no explica.",
    "simulación": "Reconstruye muchos años posibles repitiendo trozos seguidos del pasado de la acción y cuenta en cuántos el precio llega a la salida. No es un pronóstico.",
    "R² y ΔR²": "R²: fracción del movimiento explicada por mercado y sector. ΔR²: lo que añade el sector al mercado.",
    "modelo técnico": GLOSARIO_BOLSILLO["modelo técnico"],
    "lectura técnica": GLOSARIO_BOLSILLO["lectura técnica"],
    "lectura probabilística": GLOSARIO_BOLSILLO["lectura probabilística"],
    "rango de la calibración histórica": "Rango en el que cayó la frecuencia real de toque cuando el modelo daba probabilidades de ese tramo, en 2019 en adelante.",
    "error de simulación": "Mide la precisión del cálculo de la simulación (cuánto cambiaría repitiéndola), no la incertidumbre del futuro.",
    "horizonte 52 semanas": "La simulación mira un año (52 semanas) hacia adelante; este plazo es fijo y no se edita.",
    "% vs. precio actual": "Distancia del nivel frente al último precio: negativa si el nivel queda por debajo.",
    "peor semana típica": "Percentil 5 del retorno semanal: 1 de cada 20 semanas cayó al menos esto.",
    "caída máxima": "La mayor pérdida acumulada desde un máximo hasta el mínimo siguiente en los datos.",
    "caídas semanales fuertes": "Fracción de semanas con una caída mayor que 2 veces la volatilidad reciente, frente a la que daría un mercado normal sin rachas.",
    "nivel": "Precio que fijaste: tres de entrada (por debajo del precio actual) y tres de salida (por encima).",
}
