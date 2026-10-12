#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Slop Monstruo: caza las marcas de escritura de IA en un texto en español.

Se corre desde la carpeta del repo:

    python3 slop_monstruo.py borrador.md
    python3 slop_monstruo.py notas.txt
    python3 slop_monstruo.py pagina.html
    python3 slop_monstruo.py pagina.html --vista view-site
    python3 slop_monstruo.py borrador --markdown
    python3 slop_monstruo.py --texto "un borrador para revisar"
    python3 slop_monstruo.py guion.md --permitir-prueba

Puntúa sobre 5, una categoría por punto: vocabulario, construcciones, puntuación,
ritmo de a tres y prueba posiblemente inventada. Debajo de 5 sale con 1, a propósito:
un texto "casi limpio" termina sonando como cualquier otro texto de IA.

.md y .markdown se leen como Markdown y .txt como texto plano. Cualquier otro archivo
se lee como HTML; --markdown fuerza la lectura como Markdown.

Sólo caza lo que una regex puede cazar. No sabe si una cifra es verdadera ni si el texto
suena a su autor: para eso está la revisión de SKILL.md y referencias/principios.md.
"""
import html as _html   # con alias: `texto_visible` recibe un parámetro llamado `html`
import os
import re
import sys
import unicodedata

# ── el catálogo ──────────────────────────────────────────────────────────────
# Todas las reglas se escriben SIN tildes y en minúscula, porque se comparan contra
# el texto pasado por `sin_acentos`. Así "sólo" y "solo", "imaginá" e "imagina",
# "revolucionó" y "revoluciono" caen en la misma regla sin duplicar cada patrón.
# La ñ también pierde la virgulilla: "diseñado" se escribe "disenado".

# Palabras con regex propia, porque el español flexiona por género, número y
# persona, y un recorte automático de sufijos rompe más de lo que arregla.
VOCABULARIO = [
    (r"sumer[gj]\w*", "sumergirse"),
    (r"profundicemos|vamos a profundizar", "profundicemos"),
    # sin "potencia" a secas: es también el sustantivo ("la potencia del motor")
    (r"potenci(?:ar|an|ando|ado|ada|ados|adas|amos|ate|alo|ala|e|en|o)", "potenciar"),
    (r"aprovech\w* al maximo", "aprovechar al máximo"),
    (r"sin fisuras|sin friccion(?:es)?|sin esfuerzo|sin complicaciones", "sin fisuras / sin esfuerzo"),
    (r"robust[oa]s?", "robusto"),
    (r"desbloque\w*", "desbloquear"),
    (r"desat(?:ar|a|an|ate|en|o|ando)|liber\w* (?:todo )?(?:el|tu|su) (?:poder|potencial)",
     "desatar / liberar el poder"),
    (r"empoder\w*", "empoderar"),
    (r"agiliz\w*", "agilizar"),
    (r"de vanguardia|de ultima generacion|de punta", "de vanguardia / de última generación"),
    # sin "revolucion" a secas: "la revolución industrial" es un hecho, no humo
    (r"revolucion(?:ar|a|an|ara|o|ario|aria|arios|arias)", "revolucionar / revolucionario"),
    (r"transformador(?:a|es|as)?|transformacion(?:es)?", "transformador / transformación"),
    (r"innovador(?:a|es|as)?|innovacion(?:es)?", "innovador / innovación"),
    (r"holistic[oa]s?", "holístico"),
    (r"sinergias?", "sinergia"),
    (r"paradigmas?", "paradigma"),
    (r"meticulos[oa]s?|meticulosamente", "meticuloso"),
    (r"tapiz", "tapiz"),
    # sin "testimonio" a secas: "testimonios de alumnos" es literal
    (r"(?:es|son) un (?:claro |verdadero )?testimonio de", "es un testimonio de"),
    (r"un faro de", "un faro de"),
    (r"sin precedentes|sin igual|inigualables?|incomparables?|sin parangon",
     "sin precedentes / inigualable"),
    (r"supercarg\w*|turbocarg\w*|al (?:siguiente|proximo|otro) nivel|a otro nivel",
     "llevar al siguiente nivel"),
    (r"cambia(?:r|ra|n)? las reglas del juego|game ?changer", "cambia las reglas del juego"),
    (r"esto lo cambia todo", "esto lo cambia todo"),
    (r"brutal(?:es|mente)?", "brutal"),
    (r"vertiginos[oa]s?", "vertiginoso"),
    (r"ecosistemas?", "ecosistema"),
    (r"solucion(?:es)? integral(?:es)?", "solución integral"),
    # segundo nivel: una vez en un texto largo pasa; en cada sección delata
    (r"crucial(?:es)?", "crucial"),
    (r"foment\w*", "fomentar"),
    (r"intuitiv[oa]s?|intuitivamente", "intuitivo"),
    (r"de clase mundial|de primer nivel|de primera clase|lider(?:es)? (?:en el sector|de la industria)",
     "de clase mundial"),
    (r"impresionantes?", "impresionante"),
]

# Frases fijas: se comparan tal cual (sin tildes), con borde de palabra a los dos lados.
EXACTAS = [
    "en el mundo de", "en la era de", "en el panorama", "panorama actual", "en el mundo actual",
    "en el mundo de hoy", "en un mundo cada vez mas", "en constante evolucion",
    "en constante cambio", "ritmo acelerado", "no busques mas", "embarcate", "embarcarse",
    "embarquemos", "abrochate el cinturon", "ingrediente secreto", "salsa secreta",
    "este viaje", "tu viaje", "nuestro viaje", "navegar por el", "el poder de la ia",
    "es importante destacar", "es importante tener en cuenta", "cabe destacar",
    "cabe mencionar", "vale la pena mencionar", "vale la pena destacar", "dicho esto",
    "sin lugar a dudas", "sin duda alguna", "la inteligencia artificial llego para",
    "secreto que nadie te cuenta",
]

# "no es solo / no solo / no es simplemente…", la negación que prepara un giro.
_NO_SOLO = (r"\bno\s+(?:es\s+|son\s+|se trata\s+)?"
            r"(?:solo|solamente|simplemente|unicamente|meramente|nada mas)\b")

# La cola del giro, alcanzada a través de una coma o un punto. En español el sujeto
# se cae ("no es solo una herramienta, es un sistema"), así que la cola arranca por el
# verbo o por un pronombre átono ("no solo lo arma, lo publica"). Sin artículos
# (la/los/las): "no es solo pasto, la tierra está seca" no es el giro.
_COLA = r"[^!?]{0,80}?[,.;]\s*(?:es|son|tambien|ahora|te|lo|le|les|me|nos|esto|eso)\b"

FRASES = [
    (_NO_SOLO + r"[^.!?]{0,80}\bsino\b", "la construcción «no solo X, sino Y»"),
    (_NO_SOLO + _COLA, "la construcción «no es solo X, es Y»"),
    # "ya seas" y no "ya sea": "ya sea por mail o por teléfono" es un conector común.
    (r"\bya sea que\b[^.!?]{0,60}\bo\b|\bya seas\b[^.!?]{0,60}\bo\b"
     r"|\btanto si\b[^.!?]{0,60}\bcomo si\b"
     r"|\bsi sos\b[^.!?,]{0,40}\bo (?:si )?(?:sos )?(?:un|una)\b",
     "la apertura «ya seas X o Y»"),
    (r"\bmas que (?:un|una) simple\b|\bmucho mas que (?:un|una)\b|\bmas que solo\b",
     "«más que un simple…»"),
    (r"\b(?:ahi|aqui|aca) es donde (?:entra|entran|aparece)\b", "«ahí es donde entra X»"),
    (r"\b(?:decile|deci|di|dile|diles|decirle) adios a\b", "«decile adiós a»"),
    (r"(?:^|[.!?]\s+|[¿¡])imagin(?:a|ate|emos)\s+(?:un|una|que|el|la)\b", "la apertura «imaginá un…»"),
    (r"\ben conclusion\b|\ben resumen\b|\bpara resumir\b|\bpara concluir\b", "cierre de ensayo"),
    (r"\bcuando se trata de\b", "relleno «cuando se trata de»"),
    (r"\bal final del dia\b|\ba fin de cuentas\b", "«al final del día»"),
    (r"\bla clave (?:es|esta)\b|\bla verdad es que\b|\blo cierto es que\b", "arranque de carraspeo"),
    (r"\b(?:puede|podria|pueden|podrian) ayudarte a\b|\bte (?:puede|podria|pueden) ayudar a\b",
     "beneficio con cobertura («puede ayudarte a…»)"),
    (r"\b(?:podria|puede|podrian|pueden) potencialmente\b|\bquizas posiblemente\b"
     r"|\btal vez posiblemente\b", "cautelas apiladas"),
    (r"\bmuy unic[oa]s?\b|\bsuper unic[oa]s?\b", "intensificador de relleno"),
    (r"\baca va la cosa\b|\bla cosa es asi\b|\bdesglosemos\w*|\bvamos a desglosar\w*"
     r"|\blo mejor de todo\b", "arranque de carraspeo"),
    (r"\blist[oa]s? para empezar\b|\bempecemos\b|\bmanos a la obra\b", "CTA de manual"),
    (r"(?:¿|\b)(?:el|la|lo)\s+(?:resultado|respuesta|trampa|truco|clave|mejor|peor|secreto)\?",
     "pregunta que se responde sola"),
    (r"\bsin \w+(?: \w+)?, sin \w+(?: \w+)?,? (?:solo|solamente|simplemente)\b",
     "la construcción «sin X, sin Y, solo Z»"),
]

# Compuestos con guion. En español son raros; cuatro en una oración es un modelo
# traduciendo autoridad que no tiene: "plataforma end-to-end, state-of-the-art…".
COMPUESTO = re.compile(r'\b[^\W\d_]{2,}-[^\W\d_]{2,}(?:-[^\W\d_]{2,})*\b')
PISO_COMPUESTOS = 4

# Prueba social inventada. Amplia a propósito: es el único error sin vuelta atrás,
# así que importa más no dejar pasar una que no molestar con una de más. Si el número
# es real y lo podés respaldar, pasá --permitir-prueba y la regla queda como aviso.
#
# El número acepta separadores de miles y decimales, pero nunca un punto final: si lo
# absorbiera, "desde 2001. Los clientes vuelven" se leería como una cifra de clientes.
# Un número y su sustantivo viven en la misma oración.
PRUEBA = re.compile(
    r"(?<![\w.,])(\d+(?:[.,]\d+)*)\s*\+?\s*"
    # hasta dos palabras en el medio: "10.000 usuarios", "3,5 millones de clientes"
    r"(?:\w+\s+){0,2}"
    r"(usuari[oa]s?|clientes?|alumn[oa]s?|estudiantes?|equipos?|miembros?|empresas?"
    r"|negocios?|suscriptor(?:es|as?)?|seguidor(?:es|as?)?|lector(?:es|as?)?|pacientes?"
    r"|proyectos?|sitios?|personas?|creador(?:es|as?)?|emprendedor(?:es|as?)?|marcas?"
    r"|agencias?|profesionales?)"
    # Cerrado con borde de palabra: sin esto, `sitios?` matchearía dentro de "sitiosweb"
    # y `marcas?` dentro de "marcadores".
    r"(?!\w)")


def sin_acentos(t):
    """Minúscula y sin tildes ni diéresis, para que las reglas no dupliquen variantes."""
    t = unicodedata.normalize('NFD', t.lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')


def normalizar(t):
    """Lleva las variantes tipográficas a las simples que las reglas esperan.

    Un guion no separable no es `-`, \\xa0 no es un espacio y un apóstrofo curvo no es
    `'`. Si se escapa alguno, las reglas dejan de matchear en texto real, porque el
    texto real es justamente de donde salen los caracteres lindos.
    """
    t = (t.replace('‑', '-').replace('\xa0', ' ').replace('’', "'")
         .replace('“', '"').replace('”', '"'))
    return re.sub(r'\s+', ' ', t).strip()


def texto_visible(html):
    """Lo que un visitante lee de verdad: sin script ni style, sin etiquetas."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    # Decodificar todas las entidades, no seis escritas a mano: cada `&#x27;` que se
    # filtraba como texto le regalaba un punto y coma falso a la regla de puntuación.
    t = _html.unescape(t)
    return normalizar(t)


def leer_utf8(ruta):
    """Lee el archivo como UTF-8, diga lo que diga la configuración regional.

    open() sin encoding= usa la de la máquina, que en un Windows de fábrica es cp1252.
    Un texto UTF-8 se decodifica entonces con basura, las rayas y las tildes no
    matchean, y el mismo texto da 4/5 por --texto y 5/5 LIMPIO desde un archivo.
    Un control que aprueba porque no sabe leer es peor que no tener control.
    """
    with open(ruta, encoding='utf-8', errors='replace') as f:
        return f.read()


def prosa_markdown(md):
    """La prosa de un Markdown, sin los especímenes.

    Un literal no es texto publicado. Un documento que menciona `sumergirse` no usó la
    palabra, la citó. Así que cuatro cosas salen antes de puntuar:

      bloques cercados  ```…```      comandos y código, nunca prosa
      código en línea   `sumergirse`  el espécimen que se nombra
      tachado           ~~antes~~     la línea que se muestra mal a propósito
      imágenes          ![alt](src)   el texto alternativo es metadato

    El texto de los links queda, porque se lee como parte de la oración. El resto se
    puntúa igual: esto saca marcado, no ablanda ni una regla.
    """
    md = re.sub(r'```.*?```', ' ', md, flags=re.S)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' . ', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    # Reemplazos, no borrados. Borrar `[DATO: …]` del todo pega la cláusula a la
    # siguiente y puede inventar un ritmo de a tres. "algo" no matchea ninguna regla.
    md = re.sub(r'`[^`]*`', ' algo ', md)
    md = re.sub(r'~~.*?~~', ' algo ', md, flags=re.S)
    # Títulos, celdas y filas son textos separados, no una oración larga.
    md = re.sub(r'^\s{0,3}#{1,6}\s*(.*)$', r' . \1 . ', md, flags=re.M)
    md = re.sub(r'\|', ' . ', md)
    # Cada viñeta es su propia línea: juntas, dos ítems con una raya cada uno se leen
    # como una cadencia de máquina que nadie escribió.
    md = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', ' . ', md, flags=re.M)
    md = re.sub(r'^\s*>\s?', ' . ', md, flags=re.M)
    md = re.sub(r'[*_>]', ' ', md)
    return normalizar(md)


def auditar(texto):
    hallazgos = {'vocabulario': [], 'frases': [], 'puntuacion': [], 'ritmo': [], 'prueba': []}
    bajo = sin_acentos(texto)

    for patron, etiqueta in VOCABULARIO:
        n = len(re.findall(rf"(?<!\w)(?:{patron})(?!\w)", bajo))
        if n:
            hallazgos['vocabulario'].append((etiqueta, n))

    for frase in EXACTAS:
        n = len(re.findall(rf"(?<!\w){re.escape(frase)}(?!\w)", bajo))
        if n:
            hallazgos['vocabulario'].append((frase, n))

    for patron, etiqueta in FRASES:
        encontrados = re.findall(patron, bajo)
        if encontrados:
            hallazgos['frases'].append((etiqueta, len(encontrados)))

    # Rayas: dos o más en una oración se leen como cadencia de máquina. Acotado a una
    # ventana de 220 caracteres: los textos de interfaz (menús, opciones, etiquetas) no
    # llevan punto final, y un corte ingenuo por oraciones junta toda la página en una
    # sola "oración" y la regla salta siempre. Un control que grita lobo se apaga.
    for o in re.split(r'(?<=[.!?])\s+', texto):
        for i in range(0, max(1, len(o)), 220):
            ventana = o[i:i + 220]
            if ventana.count('—') >= 2:
                hallazgos['puntuacion'].append(('dos o más rayas (—) en una oración',
                                                ventana[:70].strip()))
                break
    for o in re.split(r'(?<=[.!?])\s+', texto):
        for i in range(0, max(1, len(o)), 220):
            ventana = o[i:i + 220]
            encontrados = COMPUESTO.findall(ventana)
            if len(encontrados) >= PISO_COMPUESTOS:
                hallazgos['puntuacion'].append((f'{len(encontrados)} compuestos con guion apilados '
                                                'en una oración', ', '.join(encontrados[:4])))
                break

    # Piso de 3: dos punto y coma en una página técnica larga es estilo, no una marca.
    if texto.count(';') > max(3, len(texto) // 1200):
        hallazgos['puntuacion'].append(('demasiados punto y coma para texto web',
                                        f"{texto.count(';')} encontrados"))

    # Ritmo de a tres: el reflejo de la enumeración triple ("rápido, simple y efectivo").
    # En español no hay coma de Oxford, así que lo que separa un adorno retórico de una
    # lista común es que el tercer ítem (una a tres palabras) CIERRA la cláusula.
    # "Inspección, reparación y reemplazo para casas y edificios comerciales" son tres
    # cosas reales, su tercer ítem es largo, y marcarlo sería gritar lobo.
    # Una lista de nombres propios ("Canva, Figma y Blender") nombra herramientas, no
    # adorna: si los dos primeros ítems arrancan en mayúscula, no cuenta.
    for m in re.finditer(r'\b(\w{4,}),\s+(\w{4,})\s+[ye]\s+((?:\w+\s+){0,2}\w+)\s*[.!?,;:]', texto):
        if m.group(1)[0].isupper() and m.group(2)[0].isupper():
            continue
        hallazgos['ritmo'].append(('enumeración de a tres', m.group(0)[:60]))

    for m in PRUEBA.finditer(bajo):
        hallazgos['prueba'].append(m.group(0).strip())

    return hallazgos


TITULOS = {
    'vocabulario': 'vocabulario de IA',
    'frases': 'construcciones de IA',
    'puntuacion': 'cadencia de puntuación',
    'ritmo': 'ritmo de a tres',
    'prueba': 'prueba posiblemente inventada',
}


def informar(hallazgos, etiqueta='', permitir_prueba=False):
    pesos = {'vocabulario': 1, 'frases': 1, 'puntuacion': 1, 'ritmo': 1, 'prueba': 1}
    if permitir_prueba:
        # La única regla que una regex no puede juzgar: ve un número al lado de un
        # sustantivo, no si lo podés respaldar. --permitir-prueba sigue mostrando los
        # hallazgos, pero deja de restar por una cifra verdadera y verificada.
        pesos['prueba'] = 0
    fallidas = [k for k, v in hallazgos.items() if v]
    puntaje = max(0, 5 - sum(pesos[k] for k in fallidas))

    if etiqueta:
        print(f'── {etiqueta}')
    for k in ('prueba', 'frases', 'vocabulario', 'puntuacion', 'ritmo'):
        if not hallazgos[k]:
            continue
        print(f'  {TITULOS[k]}:')
        for item in hallazgos[k][:8]:
            if isinstance(item, tuple):
                print(f'    · {item[0]}  ({item[1]})')
            else:
                print(f'    · {item}')
        if len(hallazgos[k]) > 8:
            print(f'    · …y {len(hallazgos[k]) - 8} más')

    print(f'\n  puntaje {puntaje}/5', end='  ')
    print('LIMPIO' if puntaje == 5 else 'necesita una pasada')
    return puntaje


def main(args):
    if not args:
        sys.exit(__doc__)

    permitir_prueba = '--permitir-prueba' in args
    args = [a for a in args if a != '--permitir-prueba']
    como_md = '--markdown' in args
    args = [a for a in args if a != '--markdown']
    if not args:
        sys.exit(__doc__)

    if args[0] == '--texto':
        texto = ' '.join(args[1:])
        texto = prosa_markdown(texto) if como_md else normalizar(texto)
    else:
        ruta = args[0]
        try:
            crudo = leer_utf8(ruta)
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            sys.exit(f'slop-monstruo: no puedo leer {ruta}: {e.strerror}')
        extension = os.path.splitext(ruta)[1].lower().lstrip('.')
        if extension in ('md', 'markdown') or como_md:
            texto = prosa_markdown(crudo)
        elif extension == 'txt':
            texto = normalizar(crudo)
        else:
            if '--vista' in args:
                # puntuar un solo elemento: desde su id= hasta el siguiente id="view-…"
                i = args.index('--vista')
                if i + 1 >= len(args):
                    sys.exit('slop-monstruo: --vista necesita un id, por ejemplo --vista view-inicio')
                vid = args[i + 1]
                inicio = crudo.find(f'id="{vid}"')
                if inicio < 0:
                    sys.exit(f'slop-monstruo: no hay ningún elemento con id "{vid}"')
                siguiente = crudo.find('id="view-', inicio + 1)
                crudo = crudo[inicio:siguiente if siguiente > 0 else len(crudo)]
            texto = texto_visible(crudo)

    # Nada que puntuar es un fallo, no un aprobado. Una segunda pasada que se corta deja
    # un archivo vacío, y un control que lo sella LIMPIO reporta slop como limpio justo
    # cuando el proceso se rompió.
    if not texto.split():
        sys.exit('slop-monstruo: no hay texto visible para puntuar (entrada vacía)')

    print(f'{len(texto.split())} palabras de texto visible\n')
    return 0 if informar(auditar(texto), permitir_prueba=permitir_prueba) == 5 else 1


if __name__ == '__main__':
    # Una consola cp1252 no puede imprimir cualquier carácter: reemplazar en vez de
    # cortar con un traceback. Nombrar la marca es el trabajo; repetirla byte a byte, no.
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
