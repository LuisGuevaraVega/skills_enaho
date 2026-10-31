---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas residentes con pobreza monetaria y factor de expansión, validada contra la cifra oficial. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular la pobreza del Perú por región, departamento, área, sexo o edad.
argument-hint: "[año]"
allowed-tools: Bash(uv run *)
---

# Limpiar la ENAHO

1. El año es `$0`; si está vacío, usa 2024. Si faltan `datos/sumaria-<año>.dta` o
   `datos/enaho01-<año>-200.dta`, usa primero la skill `descargando-enaho`.
2. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio <año>`
3. Lee `salidas/validacion.txt`. Si dice `NO VALIDADA` o la pobreza difiere de la cifra
   oficial del INEI en más de 0.1 puntos, detente y muestra la validación: no respondas con esa base.
4. Responde con `salidas/personas_<año>.parquet`. Toda cifra va ponderada:
   - Por departamento, área o total (variables del hogar): un registro por hogar
     (`drop_duplicates` de conglome, vivienda, hogar) ponderado con `factor07 × mieperho`.
     Así calcula el INEI y así se replican sus cifras publicadas.
   - Por sexo, edad u otra variable de la persona: ponderado con `facpob07`.
   - Nunca cuentes filas ni promedies el código `pobreza`: pobre es `pobreza <= 2`.
5. Antes de usar una variable que no está en la base, lee [reference.md](reference.md).
6. Si piden un gráfico, usa `graficando-enaho`; si piden un mapa, `mapeando-enaho`.

## Validación esperada (2024)

Pobreza 27.6 % (27.58 % con la sumaria), extrema 5.5 %, 108,664 residentes habituales,
25 departamentos. Cusco 18.5 %, urbana 24.8 %, rural 39.3 %.
