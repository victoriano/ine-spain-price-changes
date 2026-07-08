# Cambios de precios en España con datos del INE

Recreacion del grafico de cambios acumulados de precios, adaptada a Espana.

## Criterio

- Cada punto del grafico es una media anual.
- Base principal: primera media anual disponible de cada serie dentro de 2002-2025.
- La mayoria de partidas del IPC arrancan en 2002.
- `Coste salarial por hora` es trimestral y se agrega a media anual para el grafico de cambios de precios.
- `Salario mediano bruto anual` procede de la EAES y esta disponible para 2008-2024.
- `Servicios moviles` empieza en 2017 en la subclase actual del INE.
- La linea negra es el IPC general acumulado desde la media anual de 2002 hasta la media anual de 2025.
- La linea vertical gris marca 2020 como referencia temporal de la pandemia.
- Vivienda en IPC espanol no incluye vivienda en propiedad imputada; se usa el grupo de vivienda, agua, electricidad, gas y otros combustibles.
- `Compra de vivienda` usa el Indice de Precios de Vivienda nacional general, media anual; mide precio de compraventa, no esfuerzo hipotecario ni coste financiero.
- El grafico de asequibilidad divide cada serie de precios por el salario mediano bruto anual: `precio normalizado / salario mediano normalizado - 1`.
- El grafico de asequibilidad no ajusta por impuestos; la mediana salarial de la EAES es bruta.

## Fuentes

- IPC grupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76125.csv
- IPC subgrupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79183.csv
- IPC clases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76127.csv
- IPC subclases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79184.csv
- IPV compra de vivienda: https://www.ine.es/jaxiT3/files/t/csv_bdsc/25173.csv
- ETCL salarios por hora: https://www.ine.es/jaxiT3/files/t/csv_bdsc/11222.csv
- EAES salario mediano bruto anual: https://www.ine.es/jaxiT3/files/t/csv_bdsc/28191.csv

## Valores finales

| Serie | Base | Fin | Cambio | Categoria INE | Nota |
| --- | --- | --- | ---: | --- | --- |
| Educación superior | 2002 | 2025 | +113.6% | 10.4 Educación Superior |  |
| Alimentos y bebidas | 2002 | 2025 | +96.8% | 01 Alimentos y bebidas no alcohólicas |  |
| Vivienda y suministros | 2002 | 2025 | +90.1% | 04 Vivienda, agua, electricidad, gas y otros combustibles | El IPC espanol no incluye vivienda en propiedad imputada. |
| Coste salarial por hora | 2002 | 2025 | +82.0% | Coste salarial total por hora, ajustado de estacionalidad y calendario | Serie trimestral agregada a media anual; porcentaje acumulado 2002-2025. |
| Educación infantil | 2002 | 2025 | +71.2% | 10.1.0.1 Educación Infantil |  |
| IPC general | 2002 | 2025 | +66.6% | Índice general |  |
| Servicios médicos amb. | 2002 | 2025 | +57.3% | 06.2 Servicios de cuidados ambulatorios |  |
| Libros | 2002 | 2025 | +55.4% | 09.7.1 Libros | Proxy de libros de texto; la subclase libros educativos empieza en 2007. |
| Automóviles | 2002 | 2025 | +44.3% | 07.1.1 Automóviles | Proxy de coche nuevo; automoviles nuevos solo esta disponible desde 2017. |
| Muebles y hogar | 2002 | 2025 | +37.4% | 05 Muebles, artículos del hogar y artículos para el mantenimiento corriente del hogar |  |
| Hospitalarios | 2002 | 2025 | +34.5% | 06.3 Servicios de cuidados hospitalarios |  |
| Vestido y calzado | 2002 | 2025 | +22.1% | 03 Vestido y calzado |  |
| Servicios móviles | 2017 | 2025 | -13.2% | 08.3.2.0 Servicios de comunicación móvil | Disponible desde 2017; porcentaje acumulado desde esa media anual. |
| Juguetes | 2002 | 2025 | -38.0% | 09.2.1 Juegos, juguetes y artículos relacionados con las aficiones  |  |
| Equipos audiovisuales | 2002 | 2025 | -80.8% | 08.1.4.0 Equipo para la recepción, grabación y reproducción de sonido e imagen | Proxy de TVs. |
| Equipos informáticos | 2002 | 2025 | -93.1% | 08.1.3 Equipos de procesamiento de información | Proxy de software/equipo informatico. |
