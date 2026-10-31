"""Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO y arma una base de personas.

Uso:
    uv run .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024

Entra:  datos/sumaria-{anio}.dta, datos/enaho01-{anio}-200.dta
Sale:   salidas/personas_{anio}.parquet, salidas/validacion.txt
"""

import argparse
import sys
import unicodedata
from pathlib import Path

import pandas as pd

DATOS = Path("datos")
SALIDAS = Path("salidas")
LLAVES = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES + ["codperso"]

# Cifras oficiales del INEI para validar (pobreza monetaria %, residentes habituales).
OFICIAL = {2024: {"pobreza": 27.6, "residentes": 108_664}}
TOLERANCIA = 0.1

SUMARIA_COLS = LLAVES + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07",
                         "gashog2d", "inghog2d"]
PERSONA_COLS = LLAVES_PERSONA + ["p203", "p204", "p205", "p206", "p207", "p208a", "facpob07"]


def normalizar(cols):
    """Minúsculas y sin tildes; «aÑo» (con la eñe rota) pasa a anio."""
    salida = []
    for c in cols:
        c = unicodedata.normalize("NFKD", str(c).lower()).encode("ascii", "ignore").decode()
        salida.append("anio" if c in ("ao", "ano", "a?o") else c)
    return salida


def leer(path: Path, columnas: list[str]) -> pd.DataFrame:
    # 1. Leer: códigos, no etiquetas; llaves como texto.
    df = pd.read_stata(path, convert_categoricals=False)
    # 2. Normalizar nombres.
    df.columns = normalizar(df.columns)
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        sys.exit(f"ERROR: faltan columnas en {path.name}: {faltan}")
    df = df[columnas].copy()
    for c in LLAVES_PERSONA + ["ubigeo"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip()
    return df


def pct(x, w) -> float:
    return float((x * w).sum() / w.sum() * 100)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--anio", type=int, default=2024)
    args = p.parse_args()
    anio = args.anio

    f_sum = DATOS / f"sumaria-{anio}.dta"
    f_per = DATOS / f"enaho01-{anio}-200.dta"
    for f in (f_sum, f_per):
        if not f.exists():
            sys.exit(f"ERROR: no existe {f}. Usa primero la skill descargando-enaho "
                     f"(uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio {anio}).")

    sumaria = leer(f_sum, SUMARIA_COLS)
    personas = leer(f_per, PERSONA_COLS)
    n_modulo200 = len(personas)

    # 3. Filtrar residentes habituales (definición del INEI).
    residente = ((personas.p204 == 1) & (personas.p205 == 2)) | ((personas.p204 == 2) & (personas.p206 == 1))
    personas = personas[residente].copy()

    # 4. Unir personas con su hogar: muchos a uno, falla si un hogar está repetido.
    base = personas.merge(sumaria, on=LLAVES, how="left", validate="m:1", indicator=True)

    # 5. Construir variables.
    base["departamento"] = base.ubigeo.str[:2]
    base["urbano"] = base.estrato <= 5
    base["area"] = base.urbano.map({True: "Urbana", False: "Rural"})
    base["pobre"] = base.pobreza <= 2
    base["pobre_extremo"] = base.pobreza == 1
    base["sexo"] = base.p207.map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base.p208a
    base["grupo_edad"] = pd.cut(base.edad, [-1, 13, 17, 29, 44, 59, 200],
                                labels=["0-13", "14-17", "18-29", "30-44", "45-59", "60+"])
    base["anio"] = anio

    # 6. Validar.
    pobreza_hog = pct(sumaria.pobreza <= 2, sumaria.factor07 * sumaria.mieperho)
    extrema_hog = pct(sumaria.pobreza == 1, sumaria.factor07 * sumaria.mieperho)
    pobreza_per = pct(base.pobre, base.facpob07)
    poblacion = float(base.facpob07.sum())

    checks = [
        ("llaves de hogar únicas en la sumaria", not sumaria.duplicated(LLAVES).any()),
        ("llaves de persona únicas", not personas.duplicated(LLAVES_PERSONA).any()),
        ("la unión no perdió ni duplicó filas", len(base) == len(personas)),
        ("toda persona encontró su hogar", (base._merge == "both").all()),
        ("ubigeo con 6 dígitos (ceros conservados)", base.ubigeo.str.len().eq(6).all()),
        ("25 departamentos", base.departamento.nunique() == 25),
    ]
    ref = OFICIAL.get(anio)
    if ref:
        checks += [
            (f"pobreza (sumaria) = {ref['pobreza']} % ± {TOLERANCIA}", abs(pobreza_hog - ref["pobreza"]) < TOLERANCIA),
            (f"residentes habituales = {ref['residentes']:,}", len(base) == ref["residentes"]),
        ]

    ok = all(v for _, v in checks)
    lineas = [
        f"Validación ENAHO {anio}",
        "=" * 40,
        f"Filas en el módulo 200:              {n_modulo200:,}",
        f"Residentes habituales (base):        {len(base):,}",
        f"Hogares en la sumaria:               {len(sumaria):,}",
        f"Población expandida (facpob07):      {poblacion:,.0f}",
        f"Pobreza, sumaria (factor07×mieperho): {pobreza_hog:.2f} %",
        f"Pobreza extrema, sumaria:            {extrema_hog:.2f} %",
        f"Pobreza, personas (facpob07):        {pobreza_per:.2f} %",
        f"Cifra oficial INEI:                  {ref['pobreza'] if ref else 'sin referencia en OFICIAL'} %",
        "",
        *[f"[{'OK' if v else 'FALLA'}] {nombre}" for nombre, v in checks],
        "",
        f"RESULTADO: {'VALIDADA' if ok else 'NO VALIDADA, no usar la base'}",
    ]

    # 7. Guardar: la validación siempre; la base solo si pasó, para que nadie use una base mala.
    SALIDAS.mkdir(exist_ok=True)
    texto = "\n".join(lineas) + "\n"
    (SALIDAS / "validacion.txt").write_text(texto, encoding="utf-8")
    print(texto)
    destino = SALIDAS / f"personas_{anio}.parquet"
    if not ok:
        destino.unlink(missing_ok=True)
        print(f"No se guardó {destino}: la validación falló.")
        return 1
    base.drop(columns="_merge").to_parquet(destino, index=False)
    print(f"Base guardada en {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
