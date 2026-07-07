# Cambios de precios en España con datos del INE

Recreacion del grafico de cambios acumulados de precios, adaptada a Espana.

## Criterio

- Base principal: primer dato disponible de cada serie dentro de 2002M01-2025M12.
- La mayoria de partidas del IPC arrancan en 2002M01.
- `Coste salarial por hora` es trimestral y se normaliza desde 2002T1 hasta 2025T4.
- `Servicios moviles` empieza en 2017M01 en la subclase actual del INE.
- La linea negra es el IPC general acumulado desde 2002M01 hasta 2025M12.
- Vivienda en IPC espanol no incluye vivienda en propiedad imputada; se usa el grupo de vivienda, agua, electricidad, gas y otros combustibles.

## Fuentes

- IPC grupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76125.csv
- IPC subgrupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79183.csv
- IPC clases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76127.csv
- IPC subclases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79184.csv
- ETCL salarios por hora: https://www.ine.es/jaxiT3/files/t/csv_bdsc/11222.csv

## Valores finales

| Serie | Base | Fin | Cambio | Categoria INE | Nota |
| --- | --- | --- | ---: | --- | --- |
| Educación superior | 2002M01 | 2025M12 | +118.6% | 10.4 Educación Superior |  |
| Alimentos y bebidas | 2002M01 | 2025M12 | +103.3% | 01 Alimentos y bebidas no alcohólicas |  |
| Vivienda y suministros | 2002M01 | 2025M12 | +95.9% | 04 Vivienda, agua, electricidad, gas y otros combustibles | El IPC espanol no incluye vivienda en propiedad imputada. |
| Coste salarial por hora | 2002T1 | 2025T4 | +88.5% | Coste salarial total por hora, ajustado de estacionalidad y calendario | Serie trimestral; porcentaje acumulado 2002T1-2025T4. |
| Educación infantil | 2002M01 | 2025M12 | +76.3% | 10.1.0.1 Educación Infantil |  |
| IPC general | 2002M01 | 2025M12 | +72.5% | Índice general |  |
| Servicios médicos amb. | 2002M01 | 2025M12 | +63.6% | 06.2 Servicios de cuidados ambulatorios |  |
| Libros | 2002M01 | 2025M12 | +58.6% | 09.7.1 Libros | Proxy de libros de texto; la subclase libros educativos empieza en 2007. |
| Automóviles | 2002M01 | 2025M12 | +46.5% | 07.1.1 Automóviles | Proxy de coche nuevo; automoviles nuevos solo esta disponible desde 2017. |
| Muebles y hogar | 2002M01 | 2025M12 | +40.0% | 05 Muebles, artículos del hogar y artículos para el mantenimiento corriente del hogar |  |
| Hospitalarios | 2002M01 | 2025M12 | +38.4% | 06.3 Servicios de cuidados hospitalarios |  |
| Vestido y calzado | 2002M01 | 2025M12 | +37.7% | 03 Vestido y calzado |  |
| Servicios móviles | 2017M01 | 2025M12 | -13.7% | 08.3.2.0 Servicios de comunicación móvil | Disponible desde 2017M01; porcentaje acumulado desde esa fecha. |
| Juguetes | 2002M01 | 2025M12 | -39.3% | 09.2.1 Juegos, juguetes y artículos relacionados con las aficiones  |  |
| Equipos audiovisuales | 2002M01 | 2025M12 | -81.5% | 08.1.4.0 Equipo para la recepción, grabación y reproducción de sonido e imagen | Proxy de TVs. |
| Equipos informáticos | 2002M01 | 2025M12 | -93.9% | 08.1.3 Equipos de procesamiento de información | Proxy de software/equipo informatico. |
