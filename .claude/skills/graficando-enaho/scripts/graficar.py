"""Grafica la pobreza ponderada de la ENAHO por área, sexo, grupo de edad o departamento.

Uso:
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por area
    uv run .claude/skills/graficando-enaho/scripts/graficar.py --por sexo --indicador pobre_extremo

Entra:  salidas/personas_{anio}.parquet (de la skill limpiando-enaho)
Sale:   figuras/{indicador}_por_{por}_{anio}.png y la tabla impresa
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

LLAVES = ["conglome", "vivienda", "hogar"]
COLOR = "#1f4e79"
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
# Variables del hogar: se pondera como el INEI (un registro por hogar, factor07 × mieperho).
# Variables de la persona: se pondera con facpob07.
NIVEL_HOGAR = {"area", "departamento", "total"}
ETIQUETAS = {
    "area": "área de residencia", "sexo": "sexo", "grupo_edad": "grupo de edad",
    "departamento": "departamento", "total": "total",
}
INDICADORES = {"pobre": "Pobreza monetaria", "pobre_extremo": "Pobreza monetaria extrema"}


def tasa(base: pd.DataFrame, por: str, indicador: str) -> pd.Series:
    if por in NIVEL_HOGAR:
        d = base.drop_duplicates(LLAVES).assign(w=lambda x: x.factor07 * x.mieperho)
    else:
        d = base.assign(w=base.facpob07)
    d = d.assign(total="Perú")
    g = d.groupby(por, observed=True)
    return (g.apply(lambda x: (x[indicador] * x.w).sum() / x.w.sum() * 100, include_groups=False)
            .astype(float).round(1))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--por", choices=list(ETIQUETAS), default="area")
    p.add_argument("--indicador", choices=list(INDICADORES), default="pobre")
    p.add_argument("--anio", type=int, default=2024)
    args = p.parse_args()

    f = Path("salidas") / f"personas_{args.anio}.parquet"
    if not f.exists():
        sys.exit(f"ERROR: no existe {f}. Usa primero la skill limpiando-enaho.")
    base = pd.read_parquet(f)

    serie = tasa(base, args.por, args.indicador)
    if args.por == "departamento":
        serie.index = serie.index.map(DEPARTAMENTOS)
    # Categorías con orden propio (edad) se dejan así; el resto, de mayor a menor.
    if args.por != "grupo_edad":
        serie = serie.sort_values(ascending=args.por == "departamento")

    horizontal = len(serie) > 6
    fig, ax = plt.subplots(figsize=(8, 8 if horizontal else 5))
    if horizontal:
        barras = ax.barh(serie.index, serie.values, color=COLOR)
        ax.set_xlim(0, serie.max() * 1.15)
        ax.set_xlabel("% de personas")
    else:
        barras = ax.bar(serie.index, serie.values, color=COLOR, width=0.6)
        ax.set_ylim(0, serie.max() * 1.15)
        ax.set_ylabel("% de personas")
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in serie.values], padding=3, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"{INDICADORES[args.indicador]} por {ETIQUETAS[args.por]}, Perú {args.anio}",
                 loc="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {args.anio}. Estimaciones ponderadas con factor de expansión.",
             fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    salida = Path("figuras") / f"{args.indicador}_por_{args.por}_{args.anio}.png"
    salida.parent.mkdir(exist_ok=True)
    fig.savefig(salida, dpi=200)
    print(serie.to_string())
    print(f"Figura guardada en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
