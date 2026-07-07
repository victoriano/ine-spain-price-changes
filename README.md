# Cambios de precios en España

Recreación para España del gráfico de cambios acumulados de precios de bienes y servicios, usando datos oficiales del INE.

![Cambios de precios en España](outputs/ine-price-changes-spain/ine_spain_price_changes.png)

## Qué incluye

- `outputs/ine-price-changes-spain/ine_spain_price_changes.png`: gráfico final en PNG.
- `outputs/ine-price-changes-spain/ine_spain_price_changes.svg`: versión vectorial.
- `outputs/ine-price-changes-spain/ine_spain_price_changes_series.csv`: series normalizadas usadas para dibujar.
- `outputs/ine-price-changes-spain/ine_spain_price_changes_summary.csv`: tabla resumen con el cambio acumulado final.
- `outputs/ine-price-changes-spain/summary.json`: el mismo resumen en JSON.
- `scripts/data_viz/ine_price_changes_spain.py`: script reproducible que descarga los datos del INE y regenera los archivos.

## Metodología

El periodo principal es `2002M01-2025M12`, porque las series detalladas actuales del IPC del INE empiezan en enero de 2002. La variación de cada línea se calcula contra el primer dato disponible de esa serie dentro del periodo.

La línea negra es el IPC general acumulado desde `2002M01` hasta `2025M12`. El coste salarial por hora procede de la ETCL y es trimestral (`2002T1-2025T4`). La serie de servicios móviles empieza en `2017M01`, porque no está disponible con la subclase actual desde 2002.

Algunas categorías son equivalentes aproximados de las del gráfico estadounidense original:

- `Libros` se usa como proxy de libros de texto.
- `Automóviles` se usa como proxy de coches nuevos, porque la subclase de automóviles nuevos arranca en 2017.
- `Equipos audiovisuales` se usa como proxy de TVs.
- `Equipos informáticos` se usa como proxy de software/equipo informático.
- `Vivienda y suministros` es el grupo del IPC español; no incluye vivienda en propiedad imputada.

## Fuentes

- INE IPC grupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76125.csv
- INE IPC subgrupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79183.csv
- INE IPC clases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76127.csv
- INE IPC subclases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79184.csv
- INE ETCL salarios por hora: https://www.ine.es/jaxiT3/files/t/csv_bdsc/11222.csv

## Regenerar

Con `uv`:

```bash
uv run scripts/data_viz/ine_price_changes_spain.py
```

El script escribe los artefactos en `outputs/ine-price-changes-spain/`.
