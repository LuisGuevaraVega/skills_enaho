# Referencia: ENAHO 2024

## Archivos

| Módulo | Archivo | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| 34 · Sumaria | `sumaria-2024.dta` | hogar | 33,691 | conglome, vivienda, hogar | `factor07` |
| 02 · Miembros | `enaho01-2024-200.dta` | persona | 117,721 | las tres + codperso | `facpob07` |

Cada zip del INEI trae el diccionario en PDF. La base limpia tiene 108,664 residentes habituales.

## Columnas de la base limpia (`salidas/personas_2024.parquet`)

| Columna | Origen | Significado |
|---|---|---|
| conglome, vivienda, hogar, codperso | llaves | texto, con ceros a la izquierda |
| ubigeo | sumaria | texto de 6 dígitos: departamento (2), provincia (2), distrito (2) |
| departamento | `ubigeo[:2]` | código de 01 a 25; Lima 15 y Callao 07 por separado |
| dominio | sumaria | 1–3 costa, 4–6 sierra, 7 selva, 8 Lima Metropolitana |
| estrato | sumaria | 1–5 urbano, 6–8 rural |
| urbano, area | `estrato <= 5` | booleano y texto «Urbana»/«Rural» |
| pobreza | sumaria | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| pobre, pobre_extremo | `pobreza <= 2`, `pobreza == 1` | booleanos |
| mieperho | sumaria | miembros del hogar (sin trabajadores del hogar ni pensionistas) |
| factor07 | sumaria | factor de expansión del hogar |
| facpob07 | miembros | factor de expansión de la persona |
| gashog2d, inghog2d | sumaria | gasto e ingreso anual del hogar; ver la definición exacta en el diccionario de la sumaria |
| p203 | miembros | parentesco con el jefe (1 jefe, 2 cónyuge, 3 hijo…) |
| p204, p205, p206 | miembros | miembro del hogar, ausente 30+ días, presente 30+ días |
| p207, sexo | miembros | 1 hombre, 2 mujer |
| p208a, edad | miembros | edad en años cumplidos |
| grupo_edad | edad | 0-13, 14-17, 18-29, 30-44, 45-59, 60+ |

## Reglas que no se discuten

- **Residente habitual**: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.
- **Llaves como texto**: `ubigeo` «010101» como número pierde el cero y la unión falla.
- **Unión**: `personas.merge(sumaria, on=LLAVES, validate="m:1")`.
- **Nombres**: la columna del año llega como «aÑo»; el script la normaliza a `anio`.
- **Ponderar siempre**: 33,691 hogares representan 34.1 millones de personas.

## Variables de otros módulos

Para agregar una variable de otro módulo (p. ej. 05 empleo, 03 educación):
1. Descárgalo con `descargando-enaho --modulos NN`.
2. Únelo a la base por `LLAVES_PERSONA` (conglome, vivienda, hogar, codperso) con `validate="1:1"`
   o `"m:1"`, leyendo con `convert_categoricals=False` y las llaves como texto.
3. Revisa el diccionario PDF del módulo antes de interpretar códigos.
