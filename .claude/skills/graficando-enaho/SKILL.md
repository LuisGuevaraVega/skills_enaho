---
name: graficando-enaho
description: Grafica indicadores de la ENAHO del INEI, como la pobreza monetaria por área urbana y rural, sexo, grupo de edad o departamento, con barras ponderadas y reglas fijas de diseño. Úsala cuando pidan un gráfico, figura, barras o visualización de la pobreza u otros resultados de la ENAHO.
argument-hint: "[area|sexo|grupo_edad|departamento]"
allowed-tools: Bash(uv run *)
---

# Graficar la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
2. Elige `--por` según el pedido: `area` (urbana/rural), `sexo`, `grupo_edad`, `departamento`
   o `total`. Para pobreza extrema agrega `--indicador pobre_extremo`.
3. Corre exactamente, desde la raíz del repositorio:
   `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por <variable>`
4. Responde con las cifras que imprime el script y la ruta de la figura en `figuras/`.
5. Si piden algo que el script no cubre, escribe un script nuevo en `figuras/` que cumpla
   todas las reglas de abajo; no cambies las reglas.

## Reglas fijas

- Pondera siempre: `facpob07` para variables de la persona; `factor07 × mieperho` por hogar
  para área y departamento (método del INEI). Nunca cuentes filas.
- Barras que empiezan en cero, ordenadas de mayor a menor (la edad conserva su orden).
- Un solo color (`#1f4e79`); el valor escrito en cada barra con un decimal y «%».
- El título dice qué y cuándo: «Pobreza monetaria por área de residencia, Perú 2024».
- Eje con la unidad: «% de personas».
- Nota al pie: «Fuente: INEI, ENAHO 2024».
- PNG a 200 dpi en `figuras/`.

## Cifras esperadas (2024)

Urbana 24.8 %, rural 39.3 %; Cusco 18.5 %; total 27.6 %.
