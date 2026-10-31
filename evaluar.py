"""Corre los tres pedidos de evaluación con y sin skills usando `claude -p`.

Cada corrida trabaja en una copia limpia del repositorio (con datos/, sin salidas/),
así se prueba también que las skills se encadenen. Escribe evaluacion/resultados.md.

Uso:
    uv run evaluar.py
"""

import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PEDIDOS = [
    ("¿Cuál fue la pobreza en Cusco en 2024?", "18.5 %"),
    ("Grafica la pobreza urbana y rural con la ENAHO 2024", "24.8 % y 39.3 %"),
    ("Haz un mapa de la pobreza por departamento con la ENAHO 2024", "Cajamarca 45.0 %, Ica 6.0 %"),
]
HERRAMIENTAS = "Bash,Read,Write,Edit,Glob,Grep,Skill"
COPIAR = [".claude", "datos", "pyproject.toml", "uv.lock"]
SALIDA = RAIZ / "evaluacion"


def correr(i: int, pedido: str, con_skills: bool) -> dict:
    modo = "con" if con_skills else "sin"
    carpeta = Path(tempfile.mkdtemp(prefix=f"enaho_{modo}_{i}_"))
    for nombre in COPIAR:
        origen = RAIZ / nombre
        (shutil.copytree if origen.is_dir() else shutil.copy2)(origen, carpeta / nombre)
    cmd = ["claude", "-p", pedido, "--allowedTools", HERRAMIENTAS,
           "--permission-mode", "acceptEdits", "--output-format", "stream-json", "--verbose"]
    if not con_skills:
        cmd += ["--disallowedTools", "Skill"]
    r = subprocess.run(cmd, cwd=carpeta, capture_output=True, text=True, encoding="utf-8")

    skills, respuesta = [], ""
    for linea in r.stdout.splitlines():
        try:
            ev = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for bloque in ev["message"].get("content", []):
                if bloque.get("type") == "tool_use" and bloque.get("name") == "Skill":
                    skills.append(bloque["input"].get("skill", "?"))
        if ev.get("type") == "result":
            respuesta = ev.get("result", "")

    (SALIDA / f"{modo}_{i}.jsonl").write_text(r.stdout, encoding="utf-8")
    # Guarda las figuras y mapas que produjo cada corrida.
    for sub in ("figuras", "mapas"):
        for png in (carpeta / sub).glob("*.png") if (carpeta / sub).exists() else []:
            shutil.copy2(png, SALIDA / f"{modo}_{i}_{png.name}")
    shutil.rmtree(carpeta, ignore_errors=True)
    return {"i": i, "modo": modo, "pedido": pedido, "skills": skills, "respuesta": respuesta}


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    trabajos = [(i, p, c) for i, (p, _) in enumerate(PEDIDOS, 1) for c in (True, False)]
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda t: correr(*t), trabajos))

    lineas = ["# Resultados de la evaluación", "",
              "| # | Pedido | Modo | Skills activadas | Esperado |", "|---|---|---|---|---|"]
    for r in res:
        esperado = PEDIDOS[r["i"] - 1][1]
        lineas.append(f"| {r['i']} | {r['pedido']} | {r['modo']} skills | "
                      f"{', '.join(r['skills']) or 'ninguna'} | {esperado} |")
    lineas += ["", "## Respuestas", ""]
    for r in res:
        lineas += [f"### {r['i']} · {r['modo']} skills · {r['pedido']}", "", r["respuesta"].strip(), ""]
    (SALIDA / "resultados.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas[:9]))
    print(f"\nDetalle en {SALIDA / 'resultados.md'}")


if __name__ == "__main__":
    main()
