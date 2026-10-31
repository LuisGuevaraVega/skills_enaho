# Evaluación de las skills

Tres pedidos, cada uno con y sin skills, en una copia limpia del repositorio (con `datos/`,
sin `salidas/`), para comprobar que las skills se activen solas y se encadenen.

```bash
claude -p "Haz un mapa de la pobreza por departamento con la ENAHO 2024"                            # con skills
claude -p --disallowedTools Skill "Haz un mapa de la pobreza por departamento con la ENAHO 2024"    # sin skills
```

`uv run evaluar.py` corre los seis casos y escribe el detalle en `evaluacion/resultados.md`.

## Referencias (calculadas con los scripts de las skills)

| # | Pedido | Skills que deben activarse | Lo que debe salir | Obtenido por los scripts |
|---|---|---|---|---|
| 1 | ¿Cuál fue la pobreza en Cusco en 2024? | limpiando-enaho | 18.5 % | 18.5 % |
| 2 | Grafica la pobreza urbana y rural | graficando-enaho (+ limpiando-enaho) | 24.8 % y 39.3 % | 24.8 % y 39.3 % |
| 3 | Haz un mapa de la pobreza por departamento | mapeando-enaho (+ limpiando-enaho) | Cajamarca 45.0 %, Ica 6.0 % | Cajamarca 45.0 %, Ica 6.0 % |

## Resultados con y sin skills

| # | Modo | Skills activadas | Cifra | ¿Ponderó? | Figura |
|---|---|---|---|---|---|
| 1 | con skills | | | | — |
| 1 | sin skills | — | | | — |
| 2 | con skills | | | | |
| 2 | sin skills | — | | | |
| 3 | con skills | | | | |
| 3 | sin skills | — | | | |

_Pendiente: completar con `evaluacion/resultados.md` después de correr `uv run evaluar.py`._
