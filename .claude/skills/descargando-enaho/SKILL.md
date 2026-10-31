---
name: descargando-enaho
description: Descarga los módulos de la ENAHO desde el portal de microdatos del INEI (sumaria 34, miembros 02 u otros) y el GeoJSON de departamentos del Perú a la carpeta datos/. Úsala cuando falten los zip o los .dta de la ENAHO, cuando pidan bajar, descargar u obtener la ENAHO o los microdatos del INEI de un año, o cuando otra skill de la ENAHO diga que no encuentra los datos.
argument-hint: "[año] [módulos...]"
allowed-tools: Bash(uv run *)
---

# Descargar la ENAHO

1. El año es `$0`; si está vacío, usa 2024. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/descargar.py --anio <año>`
   - Si el usuario pide otros módulos, agrégalos: `--modulos 34 02 05`.
   - Si el año no está en la tabla del script, pide el código INEI y pásalo con `--codigo`.
2. Si termina con `OK`, los .dta y `peru_departamental_simple.geojson` están en `datos/`.
   Si falla, muestra el error tal cual; no descargues a mano ni inventes otra URL.
3. `datos/` no se sube a GitHub: el script crea `datos/.gitignore`.

## Lo que hay que saber

- La URL es `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{código}-Modulo{NN}.zip`.
- Códigos verificados de la ENAHO anual (metodología actualizada):

  | Año | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
  |-----|------|------|------|------|------|------|------|------|------|------|
  | Código | 498 | 546 | 603 | 634 | 687 | 737 | 759 | 784 | 906 | 966 |

- Módulos frecuentes: 01 vivienda y hogar, 02 miembros, 03 educación, 04 salud,
  05 empleo e ingresos, 34 sumaria (pobreza, gasto, ingreso).
- El script comprueba que la sumaria descargada sea del año pedido; si no, el código es incorrecto.
- Cada zip pesa entre 6 y 30 MB. Si ya existe, no se vuelve a bajar (usa `--forzar` para repetir).
- Después de descargar, la siguiente skill es `limpiando-enaho`.
