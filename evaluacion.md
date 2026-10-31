# Evaluación de las skills

Tres pedidos, cada uno con y sin skills, en una copia limpia del repositorio (con `datos/`,
sin `salidas/`), para comprobar que las skills se activen solas y se encadenen. La copia
«sin skills» además no lleva `.claude/`, para que Claude no pueda leer las skills ni sus
respuestas esperadas con Read o Grep.

```bash
claude -p "Haz un mapa de la pobreza por departamento con la ENAHO 2024"                            # con skills
claude -p --disallowedTools Skill "Haz un mapa de la pobreza por departamento con la ENAHO 2024"    # sin skills
```

`uv run evaluar.py` corre los seis casos en paralelo. Las respuestas completas están en
[`evaluacion/resultados.md`](evaluacion/resultados.md). Corrida del 31 de octubre de 2026.

## Resultados

| # | Pedido | Modo | Skills activadas | Cifra | ¿Ponderó? | Figura | Tiempo · turnos · costo |
|---|---|---|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | con | limpiando-enaho | 18.5 % ✓ | sí, `factor07 × mieperho` | — | 50 s · 8 · $0.22 |
| 1 | | sin | — | 18.5 % ✓ | sí, `factor07 × mieperho` | — | 38 s · 4 · $0.23 |
| 2 | Grafica la pobreza urbana y rural | con | graficando-enaho → limpiando-enaho | 24.8 % y 39.3 % ✓ | sí | `figuras/pobre_por_area_2024.png`, reglas fijas | 40 s · 11 · $0.26 |
| 2 | | sin | — | 24.8 % y 39.3 % ✓ | sí | `resultados/…png`, diseño propio | 66 s · 10 · $0.25 |
| 3 | Haz un mapa de la pobreza por departamento | con | mapeando-enaho → limpiando-enaho | Cajamarca 45.0 %, Ica 6.0 % ✓ | sí | `mapas/pobreza_departamento.png`, 25 con dato | 51 s · 9 · $0.26 |
| 3 | | sin | — | Cajamarca 45.0 %, Ica 6.0 % ✓ | sí | `resultados/…png`, diseño propio | 96 s · 13 · $0.51 |

Figuras de las corridas con skills: [`evaluacion/con_2_pobre_por_area_2024.png`](evaluacion/con_2_pobre_por_area_2024.png)
y [`evaluacion/con_3_pobreza_departamento.png`](evaluacion/con_3_pobreza_departamento.png).
Las de las corridas sin skills no se guardaron: Claude las escribió en `resultados/` y la
versión de `evaluar.py` de esa corrida solo copiaba `figuras/` y `mapas/` (ya corregido).

## Lo que muestra

- **Las skills se activan solas y se encadenan.** Los pedidos 2 y 3 activaron dos skills
  seguidas: graficar o mapear detectaron que no existía la base limpia y llamaron primero a
  `limpiando-enaho`, que validó 27.58 % y 108,664 residentes antes de responder.
- **Sin skills, Claude también acertó las cifras.** Con un modelo actual y los .dta a la
  vista, trabajó directo sobre la sumaria con el método del INEI. La diferencia no estuvo en
  la cifra sino en el proceso:
  - **Reproducibilidad:** cada corrida sin skills escribió su propio script, con otros nombres
    y en otras carpetas (`scripts/pobreza_area.py`, `scripts/mapa_pobreza.py`, `resultados/`).
    Con skills, el mismo pedido siempre corre el mismo script y deja la misma salida.
  - **Validación:** sin skills nadie construyó ni validó la base de personas (residentes
    habituales, unión `m:1`, llaves con ceros); el pedido 3 directamente no usó el módulo 200.
  - **Diseño:** sin skills, el formato del gráfico y del mapa depende de cada corrida; con
    skills, barras desde cero, un color, escala de un tono desde 0 y fuente al pie son fijos.
  - **Costo:** el mapa sin skills costó el doble ($0.51 contra $0.26) y tardó casi el doble
    (96 s contra 51 s), porque tuvo que escribir y depurar su propio código.
- Sin skills, el pedido 3 agregó por su cuenta intervalos de confianza con el diseño muestral,
  algo que las skills no hacen. Es una mejora posible para `mapeando-enaho`.
