"""Textos fijos de la pantalla: glosario de bolsillo, ayudas (tooltips), leyenda legal y avisos.
Las definiciones salen de docs/entrega_1/glosario.md, en una línea y en lenguaje llano."""

DISCLAIMER = "No es asesoría de inversión."
LEYENDA_ASESORIA = ("El contenido de la presente comunicación o mensaje no constituye una recomendación profesional para "
                    "realizar inversiones en los términos del artículo 2.40.1.1.2 del Decreto número 2555 de 2010 o las "
                    "normas que lo modifiquen, sustituyan o complementen")
SUBTITULO_BANNER = "Herramienta de apoyo: muestra probabilidades con su incertidumbre y deja la decisión al usuario."

NOMBRES_NIVEL = ["valoración histórica", "deep value", "value", "negativo", "base", "positivo"]
ALGORITMOS = {"arbol": "árbol de decisión", "svm_lineal": "SVM lineal", "svm_rbf": "SVM con núcleo RBF"}
PERIODO_PRUEBA = "2019 en adelante"

# Pregunta que responde cada sección (una línea bajo su título)
PREGUNTAS = {
    "tabla": "**Fundamental:** ¿es razonable este precio para esta empresa? **Técnica** (entradas): ¿compro ya o espero? "
             "Es la probabilidad de que el precio baje hasta la entrada en 60 días hábiles. **Simulación** (salidas): "
             "¿qué tan probable es vender a ese precio en el próximo año?",
    "grafico": "¿Dónde queda el precio de hoy frente a mis niveles?",
    "riesgo": "¿Cuánto me puede doler mientras espero?",
    "desempeno": "¿Cuánto confiar en la probabilidad técnica?",
    "simulacion": "¿Cuánto confiar en la probabilidad de las salidas?",
    "edicion": "¿Qué cambia si muevo mis niveles?",
    "registro": "¿Qué decidí y por qué?",
}

# Explicación común de las notas de la columna Fundamental (una sola vez; cada nivel solo agrega su dato)
NOTA_FUNDAMENTAL = ("El percentil dice dónde queda el P/E normalizado del nivel frente a la historia de la empresa (bajo = barato). "
                    "Qué se midió: en las 21 empresas de consumo defensivo, con datos de finales de 2012 a 2023, las que estaban entre el 20 % más barato "
                    "de su propia historia vieron crecer su utilidad promedio de 3 años cerca de 36 % menos que las más caras en los 3 años siguientes "
                    "(rango probable: 19 % a 50 %), y el precio no se distinguió entre los dos grupos. Es una asociación histórica: no anticipa lo que pasará "
                    "con esta empresa.")

GLOSARIO_BOLSILLO = {
    "P/E": "precio ÷ utilidad por acción (TTM = últimos 12 meses). Dice cuántos dólares se pagan por cada dólar de utilidad.",
    "P/B": "precio ÷ patrimonio por acción. Dice cuántos dólares se pagan por cada dólar de patrimonio contable.",
    "percentil": "«entre los valores pasados, ¿en qué puesto queda el de hoy?». p6 = más barato que el 94 % de su historia.",
    "mercado y sector": "mercado = S&P 500, medido con el SPY (fondo que lo replica); sector = XLP (fondo de consumo defensivo). "
                        "Fuera de la industria piloto solo se compara con el SPY.",
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
    "calibración": "Compara lo que el modelo dijo con lo que pasó: si dice 20 % y calibra bien, toca el nivel unas 2 de cada 10 veces.",
    "mejora frente a una tasa constante": "Puntaje de Brier skill (BSS): qué tanto menos se equivoca la simulación que predecir siempre la tasa histórica de entrenamiento; 0 = igual y 1 = perfecta. IC95: si excluye el 0, la mejora no es azar.",
    "rango probable": "IC95: con 95 % de confianza, la frecuencia real de ese tramo está en este rango.",
    "línea base": GLOSARIO_BOLSILLO["línea base"],
    "percentil": GLOSARIO_BOLSILLO["percentil"],
    "σ (volatilidad)": "Cuánto se mueve el precio: la desviación típica de los retornos diarios del último año, expresada en términos anuales.",
    "P/E": GLOSARIO_BOLSILLO["P/E"],
    "P/B": GLOSARIO_BOLSILLO["P/B"],
    "P/E normalizado": "Precio ÷ utilidad promedio de los últimos 3 años: evita que un solo año excepcional haga ver barata a una acción.",
    "R²": "Fracción del movimiento semanal del precio que explican el mercado (S&P 500, medido con el SPY) y el sector (XLP, fondo de consumo defensivo); va de 0 a 1. Fuera de la industria piloto solo cuenta el SPY.",
    "ΔR²": "Cuánto mejora esa explicación al añadir el sector (XLP) a la del mercado (SPY); es lo que el mercado solo no explica.",
    "simulación": "Reconstruye muchos años posibles repitiendo trozos seguidos del pasado de la acción y cuenta en cuántos el precio llega a la salida. No es un pronóstico.",
    "R² y ΔR²": "R²: fracción del movimiento semanal explicada por el mercado (SPY) y el sector (XLP). ΔR²: lo que añade el sector al mercado.",
    "modelo técnico": GLOSARIO_BOLSILLO["modelo técnico"],
    "lectura técnica": GLOSARIO_BOLSILLO["lectura técnica"],
    "lectura probabilística": GLOSARIO_BOLSILLO["lectura probabilística"],
    "rango de la calibración histórica": "Rango en el que cayó lo que pasó de verdad cuando el modelo daba probabilidades de ese tramo, en 2019 en adelante.",
    "error de simulación": "Mide la precisión del cálculo de la simulación (cuánto cambiaría repitiéndola), no la incertidumbre del futuro.",
    "horizonte 52 semanas": "La simulación mira un año (52 semanas) hacia adelante; este plazo es fijo y no se edita.",
    "% vs. precio actual": "Distancia del nivel frente al último precio: negativa si el nivel queda por debajo.",
    "peor semana típica": "Percentil 5 del retorno semanal: 1 de cada 20 semanas cayó al menos esto.",
    "caída máxima": "La mayor pérdida acumulada desde un máximo hasta el mínimo siguiente en los datos.",
    "caídas semanales fuertes": "Fracción de semanas con una caída mayor que 2 veces la volatilidad reciente. "
    "«Esperada»: la que habría si las semanas fueran independientes y con forma normal; si la observada la supera, las caídas fuertes se dan en rachas.",
    "nivel": "Precio que fijaste: tres de entrada (por debajo del precio actual) y tres de salida (por encima).",
    "nivel: valoración histórica": "Valoración histórica (entrada): el precio al que, según tú, hay que empezar a comprar con decisión porque la empresa estaría muy barata; la entrada más lejana (la más baja).",
    "nivel: deep value": "Deep value (entrada): un precio por debajo de value, en el que la empresa te resulta más atractiva; la entrada intermedia.",
    "nivel: value": "Value (entrada): el precio al que, según tú, la empresa empieza a sonar atractiva para comprar; la entrada más cercana al precio actual.",
    "nivel: negativo": "Negativo (salida): el precio objetivo en un escenario negativo; la salida más cercana por encima del precio actual.",
    "nivel: base": "Base (salida): el precio objetivo en el escenario que consideras más probable.",
    "nivel: positivo": "Positivo (salida): el precio objetivo en un escenario positivo; la salida más lejana por encima del precio actual.",
    "fuera del rango entrenado": "1 volatilidad es lo que la acción se mueve típicamente en 60 días hábiles. El modelo se entrenó con niveles de entre 0,5 y 2. Fuera de ese rango lo evalúa en el borde más cercano, "
                                 "por eso su probabilidad se marca «como máximo» (nivel más lejos) o «al menos» (más cerca).",
}
