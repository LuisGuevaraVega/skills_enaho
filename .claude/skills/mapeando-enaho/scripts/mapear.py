"""Mapa de la pobreza ponderada de la ENAHO por departamento, unido al GeoJSON por código.

Uso:
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py
    uv run .claude/skills/mapeando-enaho/scripts/mapear.py --indicador pobre_extremo

Entra:  salidas/personas_{anio}.parquet, datos/peru_departamental_simple.geojson
Sale:   mapas/{indicador}_departamento.png (pobreza_departamento.png para pobre) y mapas/*.csv
"""

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

LLAVES = ["conglome", "vivienda", "hogar"]
GEOJSON = Path("datos/peru_departamental_simple.geojson")
INDICADORES = {"pobre": "Pobreza monetaria", "pobre_extremo": "Pobreza monetaria extrema"}
# Referencias del INEI 2024 (sumaria, factor07 × mieperho): la unión y la ponderación deben dar esto.
REFERENCIA_2024 = {"06": 45.0, "16": 43.0, "21": 39.9, "11": 6.0, "18": 11.0, "17": 11.1}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--indicador", choices=list(INDICADORES), default="pobre")
    p.add_argument("--anio", type=int, default=2024)
    args = p.parse_args()

    f = Path("salidas") / f"personas_{args.anio}.parquet"
    if not f.exists():
        sys.exit(f"ERROR: no existe {f}. Usa primero la skill limpiando-enaho.")
    if not GEOJSON.exists():
        sys.exit(f"ERROR: no existe {GEOJSON}. Usa primero la skill descargando-enaho.")

    # Pobreza por departamento como el INEI: un registro por hogar, factor07 × mieperho.
    hog = pd.read_parquet(f).drop_duplicates(LLAVES)
    hog["w"] = hog.factor07 * hog.mieperho
    tasa = (hog.groupby("departamento")
            .apply(lambda x: (x[args.indicador] * x.w).sum() / x.w.sum() * 100, include_groups=False)
            .astype(float).round(1).rename("pct").reset_index())

    # Unión por código, nunca por nombre: ubigeo[:2] con FIRST_IDDP, ambos como texto de 2 dígitos.
    geo = gpd.read_file(GEOJSON)
    geo["departamento"] = geo["FIRST_IDDP"].astype(str).str.zfill(2)
    mapa = geo.merge(tasa, on="departamento", how="left", validate="1:1")

    sin_dato = mapa.loc[mapa.pct.isna(), "NOMBDEP"].tolist()
    assert len(mapa) == 25, f"se esperaban 25 departamentos, hay {len(mapa)}"
    assert not sin_dato, f"departamentos sin dato (la unión falló): {sin_dato}"
    if args.anio == 2024 and args.indicador == "pobre":
        for cod, ref in REFERENCIA_2024.items():
            obtenido = mapa.loc[mapa.departamento == cod, "pct"].item()
            assert abs(obtenido - ref) < 0.1, f"departamento {cod}: {obtenido} % ≠ {ref} % del INEI"

    fig, ax = plt.subplots(figsize=(7, 9))
    mapa.plot(column="pct", cmap="Blues", vmin=0, vmax=mapa.pct.max(), linewidth=0.5,
              edgecolor="white", ax=ax, legend=True,
              legend_kwds={"label": "% de personas", "shrink": 0.6})
    callao = mapa.loc[mapa.departamento == "07", "pct"].item()
    for _, fila in mapa[mapa.departamento != "07"].iterrows():  # Callao es muy pequeño: va en la nota
        punto = fila.geometry.representative_point()
        ax.annotate(f"{fila.pct:.0f}", (punto.x, punto.y), ha="center", fontsize=7,
                    color="white" if fila.pct > mapa.pct.max() * 0.6 else "#222222")
    ax.set_axis_off()
    ax.set_title(f"{INDICADORES[args.indicador]} por departamento, Perú {args.anio}",
                 loc="left", fontsize=13, fontweight="bold")
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {args.anio}. Ponderado con factor de expansión. "
             f"Lima (15) y Callao (07) por separado; Callao: {callao:.1f} %.", fontsize=8, color="#555555")

    nombre = "pobreza" if args.indicador == "pobre" else args.indicador
    salida = Path("mapas") / f"{nombre}_departamento.png"
    salida.parent.mkdir(exist_ok=True)
    fig.savefig(salida, dpi=200, bbox_inches="tight")
    tabla = mapa[["departamento", "NOMBDEP", "pct"]].sort_values("pct", ascending=False)
    tabla.to_csv(salida.with_suffix(".csv"), index=False)
    print(tabla.to_string(index=False))
    print(f"25 departamentos con dato. Mapa guardado en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
