# Cambios de precios en España

Recreación para España del gráfico de cambios acumulados de precios de bienes y servicios, usando medias anuales de datos oficiales del INE.

## Cambios de precios

![Cambios de precios en España, medias anuales con referencia a la pandemia de 2020](outputs/ine-price-changes-spain/ine_spain_price_changes.png)

Última versión del gráfico: medias anuales `2002-2025`, referencia vertical en `2020`, fuente INE, línea de `Compra de vivienda` con el IPV, URL del repo y autoría de Victoriano Izquierdo / `@victorianoi`.

## Asequibilidad ajustada por salarios

![Asequibilidad de precios en España ajustada por salario mediano bruto anual](outputs/ine-price-changes-spain/ine_spain_affordability_wages.png)

Este segundo gráfico divide cada serie de precios por el salario mediano bruto anual. Por encima de `0%`, la partida exige más salario mediano que en el año base; por debajo de `0%`, exige menos. La serie de salario mediano del INE está disponible para `2008-2024`, así que este gráfico usa ese periodo. Además de las partidas del IPC, incluye una línea de `Compra de vivienda` con el Índice de Precios de Vivienda del INE.

## Poder adquisitivo internacional

![Poder adquisitivo comparado entre España, Francia, Reino Unido, Suiza y EEUU](outputs/international-purchasing-power/international_purchasing_power.png)

Este gráfico compara España, Francia, Reino Unido, Suiza y EEUU con datos de WID.world. Cada curva aproxima qué porcentaje de adultos cae en cada tramo de `5.000` euros equivalentes de poder de compra en España: España queda en euros nominales reales y el resto de países se reescala por PPP. El panel derecho resume qué porcentaje de cada país supera la mediana española de `2024`.

No es una distribución de salario bruto. Usa renta nacional post-impuestos por adulto equivalente, que incluye redistribución en especie/gasto público imputado; por eso es más útil para comparar nivel de vida amplio, pero debe leerse con esa cautela.

## Tweets publicados

Estos son los posts de X publicados a partir de los gráficos del repo.

### Cambios de precios en España

[Tweet original](https://x.com/victorianoi/status/2074520158907818265), publicado el `2026-07-07`.

> ¿Qué cosas son ahora muchísimo más caras y más baratas en España que hace 20 años? Recree ese gráfico viral con datos de USA pero con los datos del @es_INE .
>
> Coinciden bastante excepto en algunas cosas que no estoy seguro si tiene que ver con cómo se categorizan y miden ciertas cosas en el IPC o porque son intrínsecas al país, como el tema de la Sanidad en USA. Aquí imagino que la educación superior ha crecido tanto ¿por la proliferación de las universidades privadas?
>
> Es aluncinante lo de la vivienda, los alimentos y los coches (lo que más afecta a la calidad de vida) cómo se han disparado desde la pandemia. En USA también han crecido mucho pero no parecen tan correlados con la pandemia.
>
> El resto de categorías (coches, muebles, vestido y calzado) también son más caros en España que lo son ahora en USA.
>
> Sólo la tecnología es más barata hoy día en ambos sitios... Lo que me lleva a tener esperanza que la IA y automatización en nuevas industrias nos pueda conducir a un futuro más próspero que los pasados 20 años

### Asequibilidad ajustada por salario mediano

[Tweet original](https://x.com/victorianoi/status/2074532273366376701), publicado el `2026-07-07`.

> Rehice el gráfico anterior, pero ajustando cada precio por el salario mediano bruto anual en España.
>
> La historia cambia bastante: desde 2008, muchas cosas son más asequibles en términos de salario mediano. Tecnología, juguetes, ropa, muebles, servicios móviles e incluso coches pesan menos que antes.
>
> Pero no todo mejora: educación superior y alimentos sí son menos asequibles. Y vivienda aparece casi plana, aunque aquí hay una trampa importante: el IPC no mide bien comprar casa. No incluye entrada, hipoteca, tipos de interés ni precio de compraventa.
>
> No se ha encarecido “todo”. Se ha encarecido lo que más importa para construir una vida.
>
> Repo y metodología:
> https://github.com/victoriano/ine-spain-price-changes

### Poder adquisitivo comparado

[Tweet original](https://x.com/victorianoi/status/2075180436167258174), publicado el `2026-07-09`.

> ¿Cuánto mejor viven los 🇺🇸 americanos vs europeos ricos 🇨🇭, segunda división europea 🇬🇧🇫🇷 y tercera 🇪🇸🇮🇹 ?
>
> Es x4.3 veces más probable tener un salario para vivir bien naciendo en 🇺🇸 USA que en 🇪🇸 España.
>
> Si veo un debate recurrente en mi timeline últimamente es el tema del europoors, pero no había visto un buen gráfico para alcanzar a comprender la magnitud. Todos sabemos que hay megaricos en USA y Suiza, UK pero cuánta gente tiene más poder acquisitivo que el español mediano y que el español acomadado (alguien que gane más de 70K en España)
>
> Con datos WID 2024, renta post-impuestos por adulto equivalente y coste de vida reescalado a España:
>
> 🇨🇭 El 83,7% de los suizos tiene más poder adquisitivo que el español mediano que gana 28K al año.
> 🇬🇧 Reino Unido 69,0%
> 🇫🇷 Francia 68,7%
> 🇺🇸 EEUU 67,6%
>
> Y para mí lo más llamativo en realidad no es tanto respecto la mediana, como de ganar más de 70K al año equivalentes a España en poder adquisitivo (que es donde diría que uno puede crear algo de riqueza como para vivir con cierta tranquilidad e independencia) Ahí como se ve en el gráfico caen mucho Francia y UK que no tienen muchísima más gente que España viviendo en ese umbral de confort como sí que tienen EEUU (casi un 20% de su población) y Suiza.
>
> 🇺🇸 EEUU - 18%
> 🇨🇭 Suiza - 16%
> 🇬🇧 Reino Unido - 7,4%
> 🇫🇷 Francia - 5%
> 🇪🇸 España - 4,2%
>
> No son salarios brutos. Es nivel de vida comparable.

## Originales de referencia

Estos son los dos gráficos estadounidenses originales usados como inspiración visual y metodológica.

![Original US price changes chart](references/originals/price-changes-us-original.png)

![Original American dream affordability chart](references/originals/american-dream-broken-original.png)

## Qué incluye

- `outputs/ine-price-changes-spain/ine_spain_price_changes.png`: gráfico final en PNG.
- `outputs/ine-price-changes-spain/ine_spain_price_changes.svg`: versión vectorial.
- `outputs/ine-price-changes-spain/ine_spain_price_changes_series.csv`: series anuales normalizadas usadas para dibujar.
- `outputs/ine-price-changes-spain/ine_spain_price_changes_summary.csv`: tabla resumen con el cambio acumulado final.
- `outputs/ine-price-changes-spain/ine_spain_median_wage_series.csv`: serie anual de salario mediano bruto usada como denominador del gráfico de asequibilidad.
- `outputs/ine-price-changes-spain/ine_spain_home_purchase_series.csv`: Índice de Precios de Vivienda nacional general usado para la línea de compra de vivienda.
- `outputs/ine-price-changes-spain/summary.json`: el mismo resumen en JSON.
- `outputs/ine-price-changes-spain/ine_spain_affordability_wages.png`: gráfico ajustado por salario mediano bruto anual.
- `outputs/ine-price-changes-spain/ine_spain_affordability_wages.svg`: versión vectorial del gráfico ajustado por salarios.
- `outputs/ine-price-changes-spain/ine_spain_affordability_wages_series.csv`: series de asequibilidad usadas para dibujar.
- `outputs/ine-price-changes-spain/ine_spain_affordability_wages_summary.csv`: resumen final de asequibilidad por partida.
- `outputs/ine-price-changes-spain/affordability_summary.json`: el mismo resumen de asequibilidad en JSON.
- `outputs/international-purchasing-power/international_purchasing_power.png`: gráfico internacional de poder adquisitivo en euros equivalentes de España.
- `outputs/international-purchasing-power/international_purchasing_power.svg`: versión vectorial del gráfico internacional.
- `outputs/international-purchasing-power/international_purchasing_power_thresholds.csv`: umbrales WID por percentil, país, euros-PPA y euros equivalentes en España.
- `outputs/international-purchasing-power/international_purchasing_power_distribution.csv`: distribución aproximada por tramos de 5.000 euros equivalentes en España.
- `outputs/international-purchasing-power/international_purchasing_power_summary.csv`: resumen por país.
- `outputs/international-purchasing-power/summary.json`: el mismo resumen internacional en JSON.
- `references/originals/price-changes-us-original.png`: gráfico estadounidense original de cambios de precios.
- `references/originals/american-dream-broken-original.png`: gráfico estadounidense original de asequibilidad ajustada por salarios.
- `scripts/data_viz/ine_price_changes_spain.py`: script reproducible que descarga los datos del INE y regenera los archivos.
- `scripts/data_viz/international_purchasing_power.py`: script reproducible que descarga los datos WID y regenera la comparación internacional.

## Metodología

El periodo principal es `2002-2025`. Cada punto del gráfico es la media anual de la serie mensual o trimestral correspondiente. Uso medias anuales para evitar que partidas muy estacionales, como vestido y calzado, introduzcan dientes de sierra mensuales.

La variación de cada línea se calcula contra la primera media anual disponible dentro del periodo. La línea negra es el IPC general acumulado desde la media anual de `2002` hasta la media anual de `2025`. El coste salarial por hora procede de la ETCL y se agrega desde datos trimestrales. La serie de servicios móviles empieza en `2017`, porque no está disponible con la subclase actual desde 2002.

El eje incluye una referencia vertical gris en `2020` para situar la pandemia.

El gráfico de asequibilidad usa la fórmula `precio normalizado / salario mediano normalizado - 1`, con escala logarítmica para comparar mejor tanto las caídas fuertes como las subidas. El denominador es el salario mediano bruto anual de la EAES, no el salario neto después de impuestos.

La vivienda debe leerse con cautela. `Vivienda y suministros` es el grupo del IPC español para vivienda, agua, electricidad, gas y otros combustibles, pero no mide la compra de vivienda en propiedad. Para capturar esa parte, los gráficos añaden `Compra de vivienda` con el Índice de Precios de Vivienda nacional general del INE. Aun así, esa línea mide precios de compraventa, no entrada, principal de hipoteca, tipos de interés ni esfuerzo financiero mensual.

Algunas categorías son equivalentes aproximados de las del gráfico estadounidense original:

- `Libros` se usa como proxy de libros de texto.
- `Automóviles` se usa como proxy de coches nuevos, porque la subclase de automóviles nuevos arranca en 2017.
- `Equipos audiovisuales` se usa como proxy de TVs.
- `Equipos informáticos` se usa como proxy de software/equipo informático.
- `Vivienda y suministros` es el grupo del IPC español; no incluye vivienda en propiedad imputada.
- `Compra de vivienda` usa el Índice de Precios de Vivienda nacional general del INE; se interpreta con base `2007` en el primer gráfico y base `2008` en el gráfico de asequibilidad, porque el salario mediano arranca en 2008.

## Fuentes

- INE IPC grupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76125.csv
- INE IPC subgrupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79183.csv
- INE IPC clases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76127.csv
- INE IPC subclases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79184.csv
- INE IPV compra de vivienda: https://www.ine.es/jaxiT3/files/t/csv_bdsc/25173.csv
- INE ETCL salarios por hora: https://www.ine.es/jaxiT3/files/t/csv_bdsc/11222.csv
- INE EAES salario mediano bruto anual: https://www.ine.es/jaxiT3/files/t/csv_bdsc/28191.csv
- WID.world datos y descargas bulk: https://wid.world/data/
- WID.world diccionario de códigos: https://wid.world/codes-dictionary/

## Regenerar

Con `uv`:

```bash
uv run scripts/data_viz/ine_price_changes_spain.py
uv run scripts/data_viz/international_purchasing_power.py
```

Los scripts escriben los artefactos en `outputs/ine-price-changes-spain/` y `outputs/international-purchasing-power/`.
