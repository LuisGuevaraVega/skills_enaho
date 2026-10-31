---
name: mapeando-enaho
description: Hace mapas coropléticos de la pobreza monetaria de la ENAHO del INEI por departamento del Perú, uniendo por código de ubigeo con el GeoJSON de los 25 departamentos. Úsala cuando pidan un mapa, mapa de calor o distribución geográfica o regional de la pobreza u otro indicador de la ENAHO.
argument-hint: "[pobre|pobre_extremo]"
allowed-tools: Bash(uv run *)
---

# Mapear la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
   Si no existe `datos/peru_departamental_simple.geojson`, usa la skill `descargando-enaho`.
2. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py`
   (para pobreza extrema: `--indicador pobre_extremo`).
3. Si el script falla en un `assert`, muestra el error y detente: la unión o la ponderación están mal.
4. Responde con la ruta del mapa (`mapas/pobreza_departamento.png`), los tres departamentos
   con más y con menos pobreza, y la tabla `mapas/pobreza_departamento.csv`.

## Reglas fijas

- Une por código: `ubigeo[:2]` con `FIRST_IDDP`, ambos como texto de dos dígitos.
  Nunca por nombre: «APURIMAC» del GeoJSON no es «Apurímac».
- Exige 25 departamentos y ninguno sin dato.
- Lima (15) y Callao (07) van separados.
- Pondera como el INEI: un registro por hogar con `factor07 × mieperho`.
- Un solo tono de claro a oscuro (`Blues`) desde 0; nunca arcoíris.
- Leyenda con la unidad: «% de personas». Nota al pie: «Fuente: INEI, ENAHO 2024».

## Cifras esperadas (2024)

Más pobreza: Cajamarca 45.0 %, Loreto 43.0 %, Puno 39.9 %.
Menos pobreza: Ica 6.0 %, Moquegua 11.0 %, Madre de Dios 11.1 %.
