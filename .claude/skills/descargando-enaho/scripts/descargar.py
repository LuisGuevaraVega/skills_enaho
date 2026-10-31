"""Descarga los módulos de la ENAHO del INEI y el GeoJSON de departamentos a datos/.

Uso:
    uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024
    uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024 --modulos 34 02 05
"""

import argparse
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

# Código de la ENAHO metodología actualizada (anual) en el portal de microdatos del INEI.
CODIGOS = {
    2015: 498,
    2016: 546,
    2017: 603,
    2018: 634,
    2019: 687,
    2020: 737,
    2021: 759,
    2022: 784,
    2023: 906,
    2024: 966,
}
URL_INEI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"
URL_GEOJSON = (
    "https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
    "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson"
)
DATOS = Path("datos")


def bajar(url: str, destino: Path, forzar: bool) -> None:
    if destino.exists() and destino.stat().st_size > 0 and not forzar:
        print(f"ya existe   {destino}")
        return
    print(f"descargando {url}")
    tmp = destino.with_suffix(destino.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.replace(destino)
    print(f"guardado    {destino} ({destino.stat().st_size / 1e6:.1f} MB)")


def extraer_dta(zip_path: Path, carpeta: Path) -> list[Path]:
    """Extrae solo los .dta, sin las subcarpetas del zip, y nunca fuera de carpeta."""
    salidas = []
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            nombre = Path(info.filename).name
            if not nombre.lower().endswith(".dta"):
                continue
            destino = carpeta / nombre.lower()
            with z.open(info) as src, open(destino, "wb") as dst:
                shutil.copyfileobj(src, dst)
            salidas.append(destino)
    return salidas


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--modulos", nargs="+", default=["34", "02"], help="códigos de módulo, p. ej. 34 02 05")
    p.add_argument("--codigo", type=int, help="código INEI de la encuesta si el año no está en la tabla")
    p.add_argument("--sin-geojson", action="store_true")
    p.add_argument("--forzar", action="store_true", help="vuelve a descargar aunque ya exista")
    args = p.parse_args()

    codigo = args.codigo or CODIGOS.get(args.anio)
    if codigo is None:
        print(f"ERROR: no conozco el código INEI de {args.anio}. Pásalo con --codigo.", file=sys.stderr)
        return 1

    DATOS.mkdir(exist_ok=True)
    gitignore = DATOS / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")

    extraidos = []
    for m in args.modulos:
        m = m.zfill(2)
        zip_path = DATOS / f"{codigo}-Modulo{m}.zip"
        bajar(URL_INEI.format(codigo=codigo, modulo=m), zip_path, args.forzar)
        extraidos += extraer_dta(zip_path, DATOS)

    for f in extraidos:
        print(f"extraído    {f}")

    # El nombre de la sumaria trae el año: si no coincide, el código no es de ese año.
    if "34" in [m.zfill(2) for m in args.modulos]:
        sumarias = [f for f in extraidos if f.name.startswith("sumaria")]
        if not any(str(args.anio) in f.name for f in sumarias):
            print(f"ERROR: la sumaria descargada ({[f.name for f in sumarias]}) no es de {args.anio}.", file=sys.stderr)
            return 1

    if not args.sin_geojson:
        bajar(URL_GEOJSON, DATOS / "peru_departamental_simple.geojson", args.forzar)

    print(f"OK: ENAHO {args.anio} (código {codigo}) lista en {DATOS}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
