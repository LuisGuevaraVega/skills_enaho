"""Corre los tres pedidos de evaluación con y sin skills usando `claude -p`.

Cada corrida trabaja en una copia limpia del repositorio (con los datos, sin salidas/),
así se prueba también que las skills se encadenen. La copia «sin skills» no lleva .claude/,
para que Claude no pueda leer las skills ni sus scripts. Escribe evaluacion/resultados.md.

Uso:
    uv run evaluar.py
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PEDIDOS = [
    ("¿Cuál fue la pobreza en Cusco en 2024?", ["18.5"]),
    ("Grafica la pobreza urbana y rural con la ENAHO 2024", ["24.8", "39.3"]),
    ("Haz un mapa de la pobreza por departamento con la ENAHO 2024", ["45.0", "6.0"]),
]
HERRAMIENTAS = "Bash,Read,Write,Edit,Glob,Grep,Skill"
DATOS = ["sumaria-2024.dta", "enaho01-2024-200.dta", "peru_departamental_simple.geojson"]
TIMEOUT = 20 * 60
SALIDA = RAIZ / "evaluacion"


def contiene(respuesta: str, cifra: str) -> bool:
    """18.5 también vale como 18,5; 45.0 también como 45 % o 45,0."""
    entero, dec = cifra.split(".")
    patron = rf"(?<![\d.,]){entero}([.,]{dec})?(?![\d])" if dec == "0" else rf"(?<![\d.,]){entero}[.,]{dec}(?!\d)"
    return re.search(patron, respuesta) is not None


def preparar(carpeta: Path, con_skills: bool) -> None:
    (carpeta / "datos").mkdir()
    for nombre in DATOS:
        shutil.copy2(RAIZ / "datos" / nombre, carpeta / "datos" / nombre)
    for nombre in ("pyproject.toml", "uv.lock"):
        shutil.copy2(RAIZ / nombre, carpeta / nombre)
    if con_skills:
        shutil.copytree(RAIZ / ".claude", carpeta / ".claude")


def correr(i: int, pedido: str, con_skills: bool) -> dict:
    modo = "con" if con_skills else "sin"
    res = {"i": i, "modo": modo, "pedido": pedido, "skills": [], "respuesta": "", "error": ""}
    carpeta = Path(tempfile.mkdtemp(prefix=f"enaho_{modo}_{i}_"))
    try:
        preparar(carpeta, con_skills)
        cmd = ["claude", "-p", pedido, "--allowedTools", HERRAMIENTAS,
               "--permission-mode", "acceptEdits", "--output-format", "stream-json", "--verbose"]
        if not con_skills:
            cmd += ["--disallowedTools", "Skill"]
        r = subprocess.run(cmd, cwd=carpeta, capture_output=True, text=True, encoding="utf-8",
                           timeout=TIMEOUT)
        (SALIDA / f"{modo}_{i}.jsonl").write_text(r.stdout, encoding="utf-8")
        if r.stderr:
            (SALIDA / f"{modo}_{i}.err").write_text(r.stderr, encoding="utf-8")
        if r.returncode != 0:
            res["error"] = f"claude salió con código {r.returncode}"

        for linea in r.stdout.splitlines():
            try:
                ev = json.loads(linea)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "assistant":
                for bloque in ev["message"].get("content", []):
                    if bloque.get("type") == "tool_use" and bloque.get("name") == "Skill":
                        res["skills"].append(bloque["input"].get("skill", "?"))
            if ev.get("type") == "result":
                res["respuesta"] = ev.get("result", "")

        # Sin skills, Claude elige dónde guardar las figuras: se buscan en toda la copia.
        for png in carpeta.rglob("*.png"):
            if ".venv" not in png.parts:
                shutil.copy2(png, SALIDA / f"{modo}_{i}_{png.name}")
    except subprocess.TimeoutExpired:
        res["error"] = f"sin respuesta en {TIMEOUT // 60} minutos"
    except Exception as e:  # una corrida que falla no debe tumbar las demás
        res["error"] = f"{type(e).__name__}: {e}"
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)
    return res


def main() -> int:
    faltan = [n for n in DATOS if not (RAIZ / "datos" / n).exists()]
    if faltan:
        print(f"ERROR: faltan {faltan} en datos/. Corre primero:\n"
              "  uv run .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024")
        return 1
    if shutil.which("claude") is None:
        print("ERROR: no encuentro el comando claude en el PATH.")
        return 1

    SALIDA.mkdir(exist_ok=True)
    trabajos = [(i, p, c) for i, (p, _) in enumerate(PEDIDOS, 1) for c in (True, False)]
    with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
        res = list(ex.map(lambda t: correr(*t), trabajos))

    lineas = ["# Resultados de la evaluación", "",
              "| # | Pedido | Modo | Skills activadas | Esperado | ¿Acertó? |",
              "|---|---|---|---|---|---|"]
    for r in res:
        esperado = PEDIDOS[r["i"] - 1][1]
        if r["error"]:
            acierto = f"error: {r['error']}"
        else:
            acierto = "sí" if all(contiene(r["respuesta"], c) for c in esperado) else "no"
        lineas.append(f"| {r['i']} | {r['pedido']} | {r['modo']} skills | "
                      f"{', '.join(r['skills']) or 'ninguna'} | {' y '.join(esperado)} % | {acierto} |")
    lineas += ["", "## Respuestas", ""]
    for r in res:
        lineas += [f"### {r['i']} · {r['modo']} skills · {r['pedido']}", "",
                   r["respuesta"].strip() or f"_(sin respuesta: {r['error']})_", ""]
    (SALIDA / "resultados.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas[:4 + len(res)]))
    print(f"\nDetalle en {SALIDA / 'resultados.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
