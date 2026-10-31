# Resultados de la evaluación

| # | Pedido | Modo | Skills activadas | Esperado | ¿Acertó? |
|---|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | con skills | limpiando-enaho | 18.5 % | sí |
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | sin skills | ninguna | 18.5 % | sí |
| 2 | Grafica la pobreza urbana y rural con la ENAHO 2024 | con skills | graficando-enaho, limpiando-enaho | 24.8 y 39.3 % | sí |
| 2 | Grafica la pobreza urbana y rural con la ENAHO 2024 | sin skills | ninguna | 24.8 y 39.3 % | sí |
| 3 | Haz un mapa de la pobreza por departamento con la ENAHO 2024 | con skills | mapeando-enaho, limpiando-enaho | 45.0 y 6.0 % | sí |
| 3 | Haz un mapa de la pobreza por departamento con la ENAHO 2024 | sin skills | ninguna | 45.0 y 6.0 % | sí |

## Respuestas

### 1 · con skills · ¿Cuál fue la pobreza en Cusco en 2024?

En 2024, el **18.5 %** de la población de Cusco era pobre en términos monetarios, según la ENAHO 2024 del INEI. Equivale a unas **261 mil personas**, de alrededor de 1.41 millones de habitantes. Es casi 9 puntos menos que el promedio nacional (27.6 %).

| Cusco 2024 | Pobreza | Pobreza extrema |
|---|---|---|
| **Total** | **18.5 %** | 2.1 % |
| Urbana | 14.9 % | 1.0 % |
| Rural | 24.7 % | 4.0 % |

El cálculo usa los microdatos de la ENAHO 2024 (módulos 34 y 02). Antes de calcularlo comprobé que la base reproduce la cifra oficial nacional: 27.58 % frente al 27.6 % publicado, y todas las comprobaciones salieron bien. Las cifras están ponderadas por hogar con `factor07 × mieperho`, que es como calcula el INEI, sobre 1,230 hogares encuestados en Cusco.

La muestra de Cusco es pequeña, así que las cifras urbana y rural tienen un margen de error mayor que el total departamental.

¿Quieres que lo compare con otros departamentos en un gráfico o un mapa?

### 1 · sin skills · ¿Cuál fue la pobreza en Cusco en 2024?

Según la ENAHO 2024 (archivo `sumaria-2024.dta`), la **pobreza monetaria en Cusco fue de 18,5 %** en 2024.

| Indicador (Cusco, 2024) | % de la población | Personas (aprox.) |
|---|---|---|
| **Pobreza total** | **18,5 %** | ~261 mil |
| Pobreza extrema | 2,1 % | ~30 mil |
| No pobre | 81,5 % | — |
| Población total | — | ~1,41 millones |

Por área:
- **Rural:** 24,7 %
- **Urbano:** 14,9 %

**Cómo lo calculé:**
- Tomé los hogares cuyo ubigeo empieza con `08`, que es el código de Cusco. Son 1.230 hogares en la muestra.
- Pobre es quien tiene `pobreza` = 1 (pobre extremo) o 2 (pobre no extremo).
- Cada hogar pesa según su factor de expansión multiplicado por el número de miembros (`factor07 × mieperho`), para que la tasa sea de personas y no de hogares.
- Para el área, urbano es `estrato` del 1 al 5 y rural del 6 al 8.

Con el mismo método, la pobreza nacional sale 27,6 %, que coincide con la cifra oficial del INEI para 2024.

Cusco queda unos 9 puntos por debajo del promedio nacional. Como la muestra departamental es pequeña, el margen de error es amplio (aproximadamente ±2 a 3 puntos). Para reportar la cifra conviene citar el intervalo de confianza oficial del INEI.

Al ejecutar el cálculo, `uv` creó una carpeta `.venv` dentro del directorio del proyecto.

### 2 · con skills · Grafica la pobreza urbana y rural con la ENAHO 2024

Hice el gráfico: según la ENAHO 2024, la pobreza monetaria es de **39,3 %** en el área rural y de **24,8 %** en la urbana.

| Área | Pobreza monetaria |
|---|---|
| Rural | **39,3 %** |
| Urbana | **24,8 %** |

La pobreza rural supera a la urbana en unos 14,5 puntos porcentuales.

Las cifras están ponderadas con el factor de expansión del hogar por el número de miembros, igual que calcula el INEI. Primero preparé una base de personas desde la sumaria y el módulo 200. Esa base da una pobreza nacional de 27,6 %, que coincide con la cifra oficial del INEI.

Archivos:
- `figuras/pobre_por_area_2024.png`
- `salidas/personas_2024.parquet`

### 2 · sin skills · Grafica la pobreza urbana y rural con la ENAHO 2024

Hice el gráfico de pobreza monetaria urbana y rural con la ENAHO 2024 (archivo `sumaria-2024.dta`).

![gráfico](resultados/pobreza_urbano_rural_2024.png)

| Área | Pobreza total | Extrema | No extrema |
|---|---|---|---|
| Nacional | **27.6%** | 5.5% | 22.1% |
| Urbano | **24.8%** | 3.1% | 21.7% |
| Rural | **39.3%** | 15.5% | 23.8% |

**Resultados:**
- La pobreza rural (39.3%) es unos 14.5 puntos más alta que la urbana (24.8%).
- La diferencia más grande está en la pobreza extrema: 15.5% en el área rural frente a 3.1% en la urbana, unas cinco veces más.
- La pobreza no extrema es parecida en las dos áreas (21.7% urbana y 23.8% rural).
- El 27.6% nacional coincide con la cifra oficial que publicó el INEI para 2024.

**Cómo lo calculé** (siguiendo el método del INEI):
- **Área:** urbano = estratos 1 a 5 (2 000 habitantes o más); rural = estratos 6 a 8.
- **Ponderador:** `factor07 × mieperho`, para que las tasas sean de personas y no de hogares.
- **Pobreza:** usé la variable `pobreza` (1 = pobre extremo, 2 = pobre no extremo, 3 = no pobre).
- **Muestra:** 33 691 hogares (22 031 urbanos y 11 660 rurales), que representan 34.5 millones de personas.

**Archivos:**
- `scripts/pobreza_area.py`: el script que hace el cálculo y el gráfico.
- `resultados/pobreza_urbano_rural_2024.png`: el gráfico, a 200 dpi.
- `resultados/pobreza_urbano_rural_2024.csv`: las tasas y la población expandida.

Las cifras son estimaciones puntuales: no calculé intervalos de confianza ni tomé en cuenta el diseño muestral, que tiene conglomerados y estratos. Como en la carpeta también está el GeoJSON departamental, puedo hacer un mapa de pobreza por departamento si te sirve.

### 3 · con skills · Haz un mapa de la pobreza por departamento con la ENAHO 2024

Hice el mapa con la ENAHO 2024: **`mapas/pobreza_departamento.png`**.

Primero armé la base de personas (`salidas/personas_2024.parquet`). La pobreza nacional sale 27.58 %, igual a la cifra oficial del INEI (27.6 %). Además, salen 108,664 residentes habituales y 25 departamentos. Pasaron todas las validaciones.

**Con más pobreza:**
1. Cajamarca: 45.0 %
2. Loreto: 43.0 %
3. Puno: 39.9 %

**Con menos pobreza:**
1. Ica: 6.0 %
2. Moquegua: 11.0 %
3. Madre de Dios: 11.1 %

Estas seis cifras coinciden con las que se esperaban para 2024.

**Tabla completa** (`mapas/pobreza_departamento.csv`, % de personas pobres):

| Departamento | % | Departamento | % |
|---|---|---|---|
| Cajamarca | 45.0 | Amazonas | 25.7 |
| Loreto | 43.0 | Tacna | 24.0 |
| Puno | 39.9 | Apurímac | 24.0 |
| Huánuco | 39.0 | Áncash | 22.8 |
| Pasco | 39.0 | San Martín | 22.0 |
| Callao | 33.9 | Cusco | 18.5 |
| Huancavelica | 33.4 | Junín | 18.5 |
| Ayacucho | 32.8 | Arequipa | 15.8 |
| Piura | 31.9 | Lambayeque | 14.0 |
| La Libertad | 30.2 | Madre de Dios | 11.1 |
| Ucayali | 27.1 | Moquegua | 11.0 |
| Lima | 27.1 | Ica | 6.0 |
| Tumbes | 26.9 | | |

**Cómo se calculó:**
- Cada departamento se une al mapa por su código de ubigeo, no por el nombre.
- Las cifras están ponderadas como lo hace el INEI: un registro por hogar, con el factor de expansión por el número de miembros del hogar.
- Lima y Callao van por separado. Callao casi no se ve en el mapa por lo pequeño que es, así que su valor (33.9 %) está en la nota al pie.
- El mapa usa una escala de azules que empieza en 0 %, con la leyenda «% de personas» y la fuente «INEI, ENAHO 2024».

Si quieres la versión de pobreza extrema, puedo generarla con `--indicador pobre_extremo`.

### 3 · sin skills · Haz un mapa de la pobreza por departamento con la ENAHO 2024

Hice el mapa con la ENAHO 2024. La pobreza nacional sale **27,6 %**, igual a la cifra oficial del INEI para 2024, así que el cálculo coincide con la metodología oficial.

**Archivos generados**
- `resultados/mapa_pobreza_departamental_2024.png`: el mapa por departamento, con la etiqueta de cada uno.
- `resultados/pobreza_departamental_2024.csv`: la tabla con pobreza total, pobreza extrema, intervalo de confianza al 95 %, coeficiente de variación y número de hogares en la muestra.
- `scripts/mapa_pobreza.py`: el código para volver a generarlo todo. Se corre con `uv run python scripts/mapa_pobreza.py datos resultados`.

**Cómo lo calculé**
- Usé el módulo Sumaria. Cuento como pobre a quien es pobre extremo o pobre no extremo (`pobreza` 1 o 2).
- Cada hogar pesa según el número de personas que viven en él (`factor07 × mieperho`), así que el resultado es el porcentaje de personas, no de hogares.
- Asigné cada hogar a su departamento con los dos primeros dígitos de `ubigeo` y lo uní al geojson por `FIRST_IDDP`. Los 25 departamentos tienen dato.
- Los errores estándar tienen en cuenta el diseño de la muestra (`estrato` y `conglome`).

**Resultados**

| Más pobres | % | Menos pobres | % |
|---|---|---|---|
| Cajamarca | 45,0 | Ica | 6,0 |
| Loreto | 43,0 | Moquegua | 11,0 |
| Puno | 39,9 | Madre de Dios | 11,1 |
| Pasco | 39,0 | Lambayeque | 14,0 |
| Huánuco | 39,0 | Arequipa | 15,8 |

**A tener en cuenta**
- **Lima va como un solo departamento (27,1 %)**, que junta Lima Metropolitana y Lima Provincias, porque el geojson lo trae así. Los reportes del INEI suelen mostrarlas por separado, así que esa cifra no se compara directo con ellos.
- **Callao (33,9 %) queda por encima de lo que uno esperaría.** Revisé que los datos estén bien unidos y lo están, pero vale contrastarlo con el informe técnico del INEI antes de publicarlo.
- **Algunas cifras son poco precisas.** Madre de Dios, Moquegua, Ica y Lambayeque tienen un coeficiente de variación mayor a 15 %, y Madre de Dios llega a 19 %. Conviene leerlas con cautela.
- No usé `enaho01-2024-200.dta`, porque el módulo Sumaria ya trae todo lo necesario.
