#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de la separación texto/notas de la segunda pasada. No llama a ningún modelo.

    python3 pruebas/test_segunda_pasada.py
"""
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(AQUI), 'segunda_pasada.py')
sys.path.insert(0, os.path.dirname(AQUI))
from segunda_pasada import CENTINELA, extraer_codex, separar  # noqa: E402

fallas = []


def chequear(nombre, condicion, detalle=''):
    if not condicion:
        fallas.append(f'{nombre}: {detalle}')


# ── el centinela separa texto de notas ─────────────────────────────────────
texto, notas = separar(f'Primer párrafo.\n\n---\n\nSegundo párrafo.\n\n{CENTINELA}\n- saqué «sumergirse»\n')
chequear('el texto conserva la regla horizontal', '---' in texto and 'Segundo párrafo.' in texto, repr(texto))
chequear('las notas no quedan en el texto', 'sumergirse' not in texto, repr(texto))
chequear('las notas salen aparte', 'sumergirse' in notas, repr(notas))

# ── sin centinela, todo es texto (falla abierto) ───────────────────────────
texto, notas = separar('Un párrafo.\nOtro párrafo.')
chequear('sin centinela no se traga nada', 'Otro párrafo.' in texto and notas == '', repr(texto))

# ── extracción de la respuesta de codex ────────────────────────────────────
crudo = 'banner\nsesión 123\ncodex\n\nRespuesta editada.\ntokens used\n1.234\n'
chequear('codex: se extrae la respuesta', extraer_codex(crudo).strip() == 'Respuesta editada.',
         repr(extraer_codex(crudo)))
chequear('codex: sin marcas devuelve el crudo', extraer_codex('sin banners') == 'sin banners')


def correr(*args, path=None):
    env = dict(os.environ)
    if path is not None:
        env['PATH'] = path
        env['HOME'] = tempfile.mkdtemp()   # que tampoco encuentre ~/.local/bin
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True,
                          encoding='utf-8', errors='replace', env=env)


_dir = tempfile.mkdtemp()
vacio = os.path.join(_dir, 'vacio.md')
with open(vacio, 'w', encoding='utf-8') as fh:
    fh.write('   \n')
chequear('borrador vacío sale con 66', correr(vacio).returncode == 66)
chequear('borrador inexistente sale con 66', correr(os.path.join(_dir, 'no.md')).returncode == 66)
latin1 = os.path.join(_dir, 'latin1.md')
with open(latin1, 'wb') as fh:
    fh.write('Un borrador con tildes: canción.\n'.encode('latin-1'))
r = correr(latin1)
chequear('borrador que no es UTF-8 sale con 66', r.returncode == 66, f'salida {r.returncode}')
chequear('borrador que no es UTF-8 sin traceback', 'Traceback' not in r.stderr, r.stderr[-160:])

borrador = os.path.join(_dir, 'borrador.md')
with open(borrador, 'w', encoding='utf-8') as fh:
    fh.write('No es solo una herramienta, es un sistema.\n')
r = correr(borrador, '--autor', 'claude', path=_dir)
chequear('sin CLI rival sale con 127', r.returncode == 127, f'salida {r.returncode}')
chequear('sin CLI rival imprime el prompt y el borrador',
         'TEXTO PARA EDITAR' in r.stdout and 'es un sistema' in r.stdout, r.stdout[-160:])

# ── si la CLI rival falla, sale con 70 y no con el código de la CLI ──────
# Un 127 de la CLI se confundiría con «no hay CLI rival». Sólo en sistemas con /bin/sh.
if os.name != 'nt':
    _bin = tempfile.mkdtemp()
    for cli, codigo in (('codex', 3), ('claude', 127)):
        falsa = os.path.join(_bin, cli)
        with open(falsa, 'w', encoding='utf-8') as fh:
            fh.write(f'#!/bin/sh\necho falla >&2\nexit {codigo}\n')
        os.chmod(falsa, 0o755)
    for autor in ('claude', 'gpt'):
        r = correr(borrador, '--autor', autor, path=_bin)
        chequear(f'CLI rival que falla sale con 70 (--autor {autor})', r.returncode == 70,
                 f'salida {r.returncode}')

if fallas:
    print(f'{len(fallas)} FALLARON\n')
    for f in fallas:
        print(f'  · {f}')
    sys.exit(1)
print('todas las pruebas pasaron')
