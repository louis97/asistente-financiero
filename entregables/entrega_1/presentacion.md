---
title: "Asistente Bursátil para el inversor value colombiano"
author: "Louis Gualtero · MINE-4101 · Entrega 1"
---

## 1. Problema

- Inversor value colombiano que compra acciones de EE.UU.: screener, fundamentales y gráfico en pantallas separadas
- De 2 a 15 cambios de pantalla por activo; 2 a 3 horas tras cada reporte trimestral
- Riesgo medido "a ojo"; sin registro de decisiones
- KPIs: < 5 min por activo, 1 pantalla, latencia ≤ 1 día, 100 % de decisiones registradas

## 2. Ideación: seis niveles, tres lecturas

![](assets/mockup.png){width=75%}

- Validación con el stakeholder: pendiente

## 3. Ética y regulación

- Sin recomendación de compra o venta (Ley 964 de 2005); aviso en cada pantalla
- Datos personales anonimizados (Ley 1581 de 2012)
- SVM lineal explicable, frente a la tasa de toque por decil de σ (GBM como referencia) y con error histórico
- Sin look-ahead: fecha `filed`, purga y embargo

## 4. Enfoque analítico

- Preguntas de negocio a hipótesis HT, HF y HP con H0 y H1
- Etiqueta de triple barrera solo-largo (k = 1, N = 12)
- Validación walk-forward con purga y embargo
- Cuatro líneas base (decide HT1 la tasa de toque por decil de σ); IC bootstrap para declarar una hipótesis apoyada

## 5. Datos

- yfinance, SEC EDGAR y Damodaran (gratuitos)
- 30 acciones y 4 ETF; 27 326 filas semanales desde 2009
- Utilidad bruta presente en solo 14 de 30 emisores
- EDGAR coincide en 6 de 6 con el 10-K de AAPL, KO y JPM

## 6. EDA: riesgo y colas

![](assets/vol_ewma_garch.png){width=60%}

- ν mediano 4.15; GARCH-t gana en 28 de 34 series (HP0, HT4 apoyadas)
- Caminata aleatoria: pasan 15 de 30 (HT0 no apoyada); P_GBM no calibrada
- VaR: GARCH-t adecuado en 14 de 30 (HP1 no apoyada)

## 6. EDA: señal débil, sector fuerte

![](assets/nb04_auc_por_regimen.png){width=55%}

- AUC por indicador 0.496–0.514 (HT2 no concluyente, HT3 no apoyada)
- Sector R² mediano 0.525 (HP3 apoyada)
- Múltiplos revierten en 7 de 29 (HF1) y 10 de 29 (HF2), no apoyadas

## 7. Conclusiones y próximos pasos

- Indicadores técnicos solos: señal débil; la probabilidad depende de σ y del régimen
- Diseño: GARCH-t con innovaciones t; rival del SVM: tasa de toque por decil de σ (GBM con deriva solo como referencia teórica, no calibrado); múltiplos como contexto
- Siguiente: SVM walk-forward (HT1 preparada, no probada), Monte Carlo, validación con el stakeholder
- Repositorio: github.com/louis97/asistente-financiero (rama entrega-1). Video: pendiente
