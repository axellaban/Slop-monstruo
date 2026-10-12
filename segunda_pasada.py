#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Segunda pasada: un modelo de OTRA familia limpia las marcas que dejó el primero.

La regla: la pasada corre en una familia de modelos distinta de la que escribió el
borrador. Un modelo no escucha su propio acento; uno rival lo escucha enseguida.

Se corre desde la carpeta del repo:

    python3 segunda_pasada.py borrador.md --autor claude > limpio.md
    python3 segunda_pasada.py borrador.md --autor gpt > limpio.md
    python3 segunda_pasada.py borrador.md --autor claude --limite 240

Ruteo:
  --autor claude             → pasada de GPT con la CLI `codex`
  --autor gpt                → pasada de Claude con la CLI `claude`
  --autor gemini             → `codex` si está instalada; si no, `claude`
  sin la CLI rival           → imprime el prompt y el borrador para pegarlos a mano
                               en el chat de la otra familia, y sale con 127

La salida estándar es el texto editado; la salida de error, las notas de cambios.
Códigos: 0 bien · 66 borrador ilegible, no UTF-8 o vacío · 70 la CLI rival falló ·
124 se pasó del tiempo · 127 no hay CLI rival. Siempre volver a correr el checker sobre
el resultado:

    python3 slop_monstruo.py limpio.md
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROMPT = AQUI / 'prompts' / 'segunda-pasada.txt'

# La respuesta es: el texto, una línea centinela, y las notas. El texto va a stdout
# para que `> limpio.md` guarde SOLO prosa; las notas van a stderr para leerlas igual.
# No se corta en un `---` pelado: es una regla horizontal válida en Markdown y el
# delimitador de un frontmatter, así que cualquier borrador que lo tuviera se cortaba
# en el lugar equivocado y las notas terminaban puntuadas como si fueran prosa.
CENTINELA = '<<<SLOPMONSTRUO-NOTAS>>>'


def buscar_cli(nombre):
    ruta = shutil.which(nombre)
    if ruta:
        return ruta
    local = Path.home() / '.local' / 'bin' / nombre
    return str(local) if os.access(local, os.X_OK) else None


def separar(respuesta):
    """Devuelve (texto, notas). Sin centinela, todo es texto y se avisa.

    Falla ABIERTO sobre el contenido: una nota de más se ve y se borra; un último
    párrafo tragado en silencio, no.
    """
    lineas = respuesta.splitlines()
    if CENTINELA not in [linea.strip() for linea in lineas]:
        print(f'segunda-pasada: AVISO no hay línea {CENTINELA} en la respuesta.', file=sys.stderr)
        print('segunda-pasada: devuelvo todo como texto. Revisá el final antes de usarlo,',
              file=sys.stderr)
        print('segunda-pasada: porque las notas pueden quedar puntuadas como prosa.', file=sys.stderr)
        return respuesta.rstrip('\n') + '\n', ''
    i = [linea.strip() for linea in lineas].index(CENTINELA)
    texto = '\n'.join(lineas[:i]).rstrip('\n') + '\n'
    notas = '\n'.join(lineas[i + 1:]).strip('\n')
    return texto, notas


def extraer_codex(crudo):
    """codex envuelve la respuesta en banners: va entre la última línea `codex` y `tokens used`."""
    buf, dentro = [], False
    for linea in crudo.splitlines():
        if linea == 'codex':
            buf, dentro = [], True
        elif linea == 'tokens used':
            dentro = False
        elif dentro:
            buf.append(linea)
    cuerpo = '\n'.join(buf)
    return cuerpo if cuerpo.strip() else crudo


def correr(cmd, limite):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=limite, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        print(f'segunda-pasada: se cortó a los {limite}s', file=sys.stderr)
        sys.exit(124)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        # Un código fijo y no el de la CLI: si la CLI saliera con 127, se confundiría
        # con «no hay CLI rival», que promete el prompt en la salida estándar.
        print(f'segunda-pasada: la CLI salió con {r.returncode}', file=sys.stderr)
        sys.exit(70)
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description='Segunda pasada con un modelo de otra familia.')
    ap.add_argument('borrador', help='archivo con el borrador (markdown, html o texto)')
    ap.add_argument('--autor', choices=['claude', 'gpt', 'gemini'], default='claude',
                    help='familia de modelo que ESCRIBIÓ el borrador (por defecto: claude)')
    ap.add_argument('--limite', type=int, default=180, help='segundos máximos (por defecto: 180)')
    args = ap.parse_args()

    ruta = Path(args.borrador)
    # Sin esto, un nombre mal tipeado mandaba un borrador VACÍO a una llamada paga.
    try:
        borrador = ruta.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        print(f'segunda-pasada: no puedo leer {ruta}', file=sys.stderr)
        return 66
    if not borrador.strip():
        print('segunda-pasada: el borrador está vacío, no hay nada que limpiar', file=sys.stderr)
        return 66

    completo = f'{PROMPT.read_text(encoding="utf-8")}\n\n{borrador}'
    codex, claude = buscar_cli('codex'), buscar_cli('claude')

    if args.autor in ('claude', 'gemini') and codex:
        # Sandbox de sólo lectura: es una transformación de texto, no tiene por qué
        # escribir archivos.
        crudo = correr([codex, 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', completo],
                       args.limite)
        respuesta = extraer_codex(crudo)
    elif args.autor in ('gpt', 'gemini') and claude:
        respuesta = correr([claude, '-p', completo], args.limite)
    else:
        # Sólo está la CLI de la misma familia que escribió el borrador (o ninguna).
        # Correrla sería un modelo corrigiéndose la tarea a sí mismo, que es lo único
        # que este script existe para evitar.
        print('segunda-pasada: no hay CLI de la familia rival (un borrador de Claude necesita',
              file=sys.stderr)
        print('codex; uno de GPT necesita claude). Pegá lo de abajo en el chat de la otra familia.',
              file=sys.stderr)
        print(completo)
        return 127

    texto, notas = separar(respuesta)
    sys.stdout.write(texto)
    if notas:
        print('\nsegunda-pasada: qué cambió -', file=sys.stderr)
        print(notas, file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
