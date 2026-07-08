# Poder adquisitivo internacional

Comparación de España, Francia, Reino Unido, Suiza y EEUU con datos de WID.world. La renta se convierte a euros equivalentes de poder de compra en España: España queda en euros nominales reales y el resto de países se reescala por PPP.

![Poder adquisitivo comparado](international_purchasing_power.png)

## Resumen

Referencia: mediana española de `2024`, `28.158` euros reales por adulto equivalente.

| País | Mediana equivalente en España | Media equivalente en España | % por encima de la mediana española |
| --- | ---: | ---: | ---: |
| Suiza | 50.963 | 53.656 | 83.7% |
| Reino Unido | 32.865 | 41.125 | 69.0% |
| Francia | 35.060 | 40.240 | 68.7% |
| EEUU | 38.453 | 54.179 | 67.6% |
| España | 28.158 | 32.911 | 50.0% |

## Metodología

- Fuente: WID.world bulk downloads por país.
- Variable de renta: `tdiincj992`, umbral de renta nacional post-impuestos por percentil, adultos `equal-split`.
- Conversión a euros equivalentes en España: cada umbral local se divide por `xlceupi999`, y luego se multiplica por el factor PPP de España en el mismo año. Así España se mantiene en euros nominales reales.
- El panel principal aproxima una distribución: qué porcentaje de adultos cae en cada tramo de 5.000 euros equivalentes en España. Se calcula interpolando los umbrales percentilares de WID, no con microdatos individuales.
- El panel derecho resume qué porcentaje de cada país supera la mediana española.

Esta no es una distribución de salario bruto. Es una métrica más amplia de nivel de vida porque incluye redistribución en especie/gasto público imputado dentro de la renta nacional post-impuestos. WID tiene también `cainc` para renta disponible post-impuestos estricta, pero en la descarga actual no ofrece umbrales/promedios con granularidad suficiente para construir este gráfico comparable.

## Archivos

- `international_purchasing_power.png`: gráfico final en PNG.
- `international_purchasing_power.svg`: versión vectorial.
- `international_purchasing_power_thresholds.csv`: umbrales por percentil, país, euros-PPA y euros equivalentes en España.
- `international_purchasing_power_distribution.csv`: distribución aproximada por tramos de 5.000 euros equivalentes en España.
- `international_purchasing_power_summary.csv`: resumen por país.
- `summary.json`: resumen en JSON.
