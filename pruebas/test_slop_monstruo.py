#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de regresión del checker. Se corren desde la carpeta del repo:

    python3 pruebas/test_slop_monstruo.py

Van en dos direcciones, y la segunda es la que importa. Es fácil ensanchar una regex
hasta que caza todo, así que cada ensanche va con un caso que tiene que seguir limpio
y que se rompería si la regla se pusiera golosa.
"""
import os
import re
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
HERRAMIENTA = os.path.join(os.path.dirname(AQUI), 'slop_monstruo.py')
sys.path.insert(0, os.path.dirname(AQUI))
from slop_monstruo import (VOCABULARIO, EXACTAS, PRUEBA, auditar, texto_visible,  # noqa: E402
                          prosa_markdown, sin_acentos)

fallas = []


def chequear(nombre, condicion, detalle=''):
    if not condicion:
        fallas.append(f'{nombre}: {detalle}')


def grupos(texto):
    return {k for k, v in auditar(texto).items() if v}


def correr(*args):
    return subprocess.run([sys.executable, HERRAMIENTA, *args], capture_output=True,
                          text=True, encoding='utf-8', errors='replace')


# ── cada frase exacta se detecta en una oración ─────────────────────────────
for f in EXACTAS:
    chequear(f'frase exacta «{f}»', 'vocabulario' in grupos(f'Hoy {f} pasa algo.'), 'no detectada')

# ── cada regla de vocabulario compila y matchea su propia etiqueta o un ejemplo ─
for patron, etiqueta in VOCABULARIO:
    try:
        re.compile(patron)
    except re.error as e:
        chequear(f'regex «{etiqueta}»', False, str(e))

# ── flexiones y tildes: la misma regla con y sin acento ─────────────────────
# Límite conocido: el imperativo «potenciá» sin tilde es «potencia», igual que el
# sustantivo, así que no se caza. Las otras formas del verbo sí.
for mala in ('Potenciamos tu flujo con IA.',
             'Vamos a sumergirnos en el tema.',
             'Desbloqueá todo tu potencial.',
             'Una solución robusta para tu negocio.',
             'Un enfoque revolucionario.',
             'Esto revolucionó la industria.',
             'Empoderamos a los creadores.',
             'Llevá tu canal al siguiente nivel.',
             'Una propuesta innovadora.',
             'Una experiencia sin fisuras.'):
    chequear('vocabulario detectado', 'vocabulario' in grupos(mala), mala)

# ── sentidos literales que NO tienen que saltar ─────────────────────────────
for ok in ('La potencia del motor es de 90 caballos.',
           'La revolución industrial empezó en Inglaterra.',
           'Leí los testimonios de los alumnos.',
           'Ató el caballo antes de cargar el carro.'):
    chequear('sentido literal limpio', 'vocabulario' not in grupos(ok), ok)

# ── construcciones ─────────────────────────────────────────────────────────
for mala in ('No es solo una herramienta, es un sistema.',
             'No es sólo una herramienta. Es un sistema.',
             'No solo arma el guion, sino que lo revisa.',
             'No solo lo arma, lo publica.',
             'Ya sea que estés empezando o seas experto, esto te sirve.',
             'Ya seas principiante o experto, esto te sirve.',
             'Si sos principiante o un experto, arrancá acá.',
             'Ahí es donde entra Claude.',
             'Decile adiós a las planillas.',
             'Imaginá un mundo sin planillas.',
             '¿El resultado? Un canal que crece.',
             'Más que un simple editor de video.',
             'En conclusión, conviene probarlo.',
             'La clave está en el proceso.',
             'Esta app puede ayudarte a ordenar tu semana.',
             'Sin código, sin servidores, solo un prompt.',
             '¿Listo para empezar?'):
    chequear('construcción detectada', 'frases' in grupos(mala), mala)

for ok in ('No es solo cuestión de plata.',
           'No te creas solo lo que digo.',
           'El lote no es solo pasto, la tierra está seca.',
           'Fijate si sos el dueño o no.',
           'Ya sea por mail o por teléfono, avisame.',
           'Me imaginaba otra cosa.',
           'No pudimos quedarnos ahí. La lluvia seguía.'):
    chequear('construcción limpia', 'frases' not in grupos(ok), ok)

# ── ritmo de a tres ────────────────────────────────────────────────────────
chequear('enumeración de a tres', 'ritmo' in grupos('Es rápido, simple y efectivo.'))
chequear('enumeración con «e»', 'ritmo' in grupos('Es rápido, simple e intuitivo.'))
chequear('tercer ítem corto que cierra', 'ritmo' in grupos('Confiable, rápido y hecho para durar.'))
chequear('lista de servicios no es adorno',
         'ritmo' not in grupos('Inspección, reparación y reemplazo para casas y edificios comerciales.'))
chequear('complemento al frente no es enumeración',
         'ritmo' not in grupos('El martes, publicamos el lanzamiento y nos fuimos.'))
chequear('ítems cortos no cuentan', 'ritmo' not in grupos('Sol, mar y luz.'))
chequear('lista de nombres propios no cuenta',
         'ritmo' not in grupos('Lo armé con Canva, Figma y Blender, en ese orden.'))
chequear('mayúscula de inicio de oración no salva el adorno',
         'ritmo' in grupos('Simple, rápido y para vos.'))
chequear('lista con «o» no cuenta',
         'ritmo' not in grupos('No hacemos canaletas, revestimientos, ventanas o techos.'))

# ── prueba inventada ───────────────────────────────────────────────────────
for mala in ('Más de 10.000 usuarios felices.', 'Lo usan +500 empresas.', '10 mil personas ya lo usan.',
             'Elegido por 25 negocios.', 'Más de 3,5 millones de clientes.', 'Tengo 120 suscriptores.'):
    chequear('prueba detectada', 'prueba' in grupos(mala), mala)
for ok in ('Techos, y sólo techos, desde 2001. Los clientes vuelven.',
           'Versión 2.0. Los lectores pueden saltearla.',
           'Generamos 12 sitiosweb de prueba.',
           'Compré 3 marcadores.'):
    chequear('prueba no cruza el punto ni matchea dentro de otra palabra', 'prueba' not in grupos(ok), ok)

# ── entidades HTML decodificadas, no filtradas ─────────────────────────────
t = texto_visible('<p>No es solo una herramienta, es un sistema&#x21;</p>')
chequear('entidades decodificadas', 'sistema!' in t, repr(t))
chequear('las entidades no regalan punto y coma', t.count(';') == 0, repr(t))
chequear('frase vista a través de entidades', 'frases' in grupos(t))
chequear('nbsp pasa a espacio', texto_visible('<p>a&nbsp;b</p>') == 'a b')

# ── el control: entrada vacía falla, archivo inexistente falla sin traceback ─
r = correr('--texto', '')
chequear('entrada vacía sale distinto de 0', r.returncode != 0, f'salida {r.returncode}')
r = correr('/no/existe.html')
chequear('archivo inexistente sale distinto de 0', r.returncode != 0, f'salida {r.returncode}')
chequear('archivo inexistente sin traceback', 'Traceback' not in r.stderr, r.stderr[:80])

# ── los archivos se leen como UTF-8, por .html, .md y .txt ─────────────────
_dir = tempfile.mkdtemp()
_marcas = ('No es sólo una herramienta, es un sistema. Ya sea que seas creador '
           'o agencia, publicamos rápido — muy rápido — cada semana.')
for nombre, cuerpo in (('utf8.html', f'<html><body><p>{_marcas}</p></body></html>'),
                       ('utf8.md', _marcas), ('utf8.txt', _marcas)):
    ruta = os.path.join(_dir, nombre)
    with open(ruta, 'w', encoding='utf-8') as fh:
        fh.write(cuerpo)
    r = correr(ruta)
    chequear(f'{nombre} no da LIMPIO', r.returncode != 0, r.stdout[:140])
    chequear(f'{nombre}: salta la regla de construcciones', 'construcciones' in r.stdout, r.stdout[:140])
    chequear(f'{nombre}: salta la regla de rayas', 'rayas' in r.stdout, r.stdout[:140])

# ── la extensión se lee sin importar mayúsculas; --markdown fuerza Markdown ──
_bloque = 'Intro.\n```\ndesbloqueá tu potencial sin fisuras\n```\nCierre.\n'
for nombre, extra in (('MAYUS.MD', ()), ('largo.markdown', ()), ('sin-extension', ('--markdown',))):
    ruta = os.path.join(_dir, nombre)
    with open(ruta, 'w', encoding='utf-8') as fh:
        fh.write(_bloque)
    r = correr(ruta, *extra)
    chequear(f'{nombre} se lee como Markdown', r.returncode == 0, r.stdout[-140:])

r = correr(os.path.join(_dir, 'utf8.html'), '--vista')
chequear('--vista sin id sale distinto de 0', r.returncode != 0, f'salida {r.returncode}')
chequear('--vista sin id sin traceback', 'Traceback' not in r.stderr, r.stderr[-160:])

_cjk = os.path.join(_dir, 'cjk.html')
with open(_cjk, 'w', encoding='utf-8') as fh:
    fh.write('<p>Nuestra plataforma robusta 你好 — 世界 — sin fisuras.</p>')
r = correr(_cjk)
chequear('caracteres raros no dan traceback', 'Traceback' not in r.stderr, r.stderr[-160:])
chequear('caracteres raros igual puntúan', 'puntaje' in r.stdout, r.stdout[:140])

# ── texto humano limpio sigue en 5/5 ───────────────────────────────────────
for ok in ('Seis clavos por teja, en cada teja.',
           'Te paso el alcance por escrito y un precio cerrado antes de que nadie suba al techo.',
           'Armé el agente un domingo y el lunes se me rompió dos veces.',
           'El brief tiene que caber en una pantalla.'):
    chequear('texto limpio sigue limpio', not grupos(ok), f'{ok} -> {grupos(ok)}')

# ── markdown: un literal no es texto publicado ─────────────────────────────
md = prosa_markdown('Usá `sumergirse` acá. Mirá [la guía](u.md) para más.')
chequear('el código en línea no se puntúa', 'sumergirse' not in md, repr(md))
chequear('el texto del link sobrevive', 'la guía' in md, repr(md))
chequear('la prosa alrededor sobrevive', 'para más' in md, repr(md))

md = prosa_markdown('> ~~Confiable, rápido y hecho para durar.~~\n> **Seis clavos por teja.**')
chequear('el espécimen tachado no se puntúa', 'ritmo' not in grupos(md), repr(md))
chequear('la línea publicada sobrevive', 'Seis clavos por teja' in md, repr(md))

md = prosa_markdown('Intro.\n```\ndesbloqueá tu potencial sin fisuras\n```\nCierre.')
chequear('el bloque cercado no se puntúa', not grupos(md), repr(md))
chequear('la prosa alrededor del bloque sobrevive', 'Intro' in md and 'Cierre' in md, repr(md))

md = prosa_markdown('Si falta la cifra, poné `[DATO: suscriptores]` y seguí.')
chequear('sacar código no inventa enumeraciones', 'ritmo' not in grupos(md), repr(md))

md = prosa_markdown('| a | **3/5** — una cosa |\n| b | **5/5** — otra cosa |')
chequear('las filas de una tabla no se juntan', 'puntuacion' not in grupos(md), repr(md))

md = prosa_markdown('## Recibos, no promesas\nUna corrida real sobre siete oraciones.')
chequear('el título no se pega al cuerpo', 'promesas Una' not in md, repr(md))

md = prosa_markdown('Potenciamos tu negocio con una solución robusta y de vanguardia.')
chequear('markdown no ablanda el vocabulario', 'vocabulario' in grupos(md), repr(md))
md = prosa_markdown('No es solo una herramienta, es un viaje.')
chequear('markdown no ablanda las construcciones', 'frases' in grupos(md), repr(md))

md = prosa_markdown('- Nivel 1 — borrar al verla\n- Nivel 2 — casi siempre se corta')
chequear('las viñetas no se juntan', 'puntuacion' not in grupos(md), repr(md))
md = prosa_markdown('- Nuestro equipo — capacitado, certificado y local — te ayuda.')
chequear('dos rayas dentro de una viñeta saltan', 'puntuacion' in grupos(md), repr(md))

# ── compuestos con guion: el apilado, no el guion ──────────────────────────
pila = 'Una plataforma end-to-end, state-of-the-art, AI-powered, best-in-class para vos.'
chequear('cuatro compuestos apilados saltan', 'puntuacion' in grupos(pila), pila)
chequear('un compuesto suelto queda limpio',
         'puntuacion' not in grupos('Un acuerdo franco-alemán y una relación costo-beneficio razonable.'))

# ── sin_acentos ────────────────────────────────────────────────────────────
chequear('sin_acentos saca tildes y ñ', sin_acentos('Sólo DISEÑÉ') == 'solo disene')
chequear('PRUEBA compila', PRUEBA.search('500 equipos') is not None)

if fallas:
    print(f'{len(fallas)} FALLARON\n')
    for f in fallas:
        print(f'  · {f}')
    sys.exit(1)
print('todas las pruebas pasaron')
