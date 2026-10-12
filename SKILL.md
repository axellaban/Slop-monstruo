---
name: slop-monstruo
description: Revisa un texto en español para su lector, caza las marcas de escritura de IA con un checker, lo reescribe, pide una segunda pasada a un modelo de otra familia y vuelve a chequear. Se activa con /slop-monstruo, "pasalo por Slop Monstruo", "sacale el slop", "humanizá esto", "¿esto suena a IA?", "arreglá este texto".
---

# Slop Monstruo

Editá el borrador en español para su lector y su propósito: un guion, la descripción de
un video, el texto de un Reel, una página de venta, un mail o un README. El checker marca
patrones conocidos. La revisión en contexto la hacés vos. Un 5/5 significa que no saltó
ninguna regla, no que el texto sea claro o verdadero.

Las rutas de este archivo son relativas a la carpeta del skill, la que tiene este
SKILL.md. Si lo instalaste en `~/.claude/skills/slop-monstruo/`, el checker es
`~/.claude/skills/slop-monstruo/slop_monstruo.py`.

Si el proyecto donde trabajás tiene reglas propias de voz o de estilo (un `CLAUDE.md`,
una guía de marca), esas mandan sobre lo de acá.

## Paso 1: Contexto y checker

Identificá el lector, el formato y qué necesita sacar del texto. Usá el pedido y el
propio borrador. Preguntá sólo cuando el contexto que falta cambiaría la edición.

Un README explica qué hace el proyecto, cómo se usa y sus límites. Un guion arranca por
la promesa y la prueba. Una página de venta puede necesitar plantear el problema antes
de la oferta. Un mail puede necesitar arrancar por el pedido.

```
python3 slop_monstruo.py borrador.md
python3 slop_monstruo.py borrador.txt
python3 slop_monstruo.py pagina.html
python3 slop_monstruo.py pagina.html --vista view-inicio
python3 slop_monstruo.py --texto "un párrafo corto"
```

Puntúa cinco categorías: vocabulario, construcciones, puntuación, enumeraciones de a
tres y prueba posiblemente inventada. Cada categoría con hallazgos resta un punto.
Debajo de 5/5 sale con 1. La entrada vacía también falla. Para Markdown usá la ruta del
archivo, así el código y los ejemplos tachados no se puntúan. Un archivo con otra
extensión se lee como HTML: si es Markdown sin extensión, agregá `--markdown`. En HTML,
`--vista` puntúa un solo elemento: desde su `id` hasta el siguiente `id="view-…"`.

Las reglas son de español: un texto en otro idioma puede dar 5/5 sin estar limpio.

## Paso 2: Revisar y reescribir

Leé [referencias/principios.md](referencias/principios.md) (chequeos editoriales) y
[referencias/senales-de-escritura-ia.md](referencias/senales-de-escritura-ia.md)
(catálogo).

Recorré el borrador en este orden:

1. **Propósito y estructura.** Respondé temprano la primera pregunta del lector. Sacá
   ganchos duplicados y misterios que demoran la explicación.
2. **Sentido y evidencia.** Cada oración agrega información y sigue a la anterior.
   Sacá contrastes vacíos y metáforas repetidas. Respetá los hechos y la postura del autor.
3. **Palabras y ritmo.** Revisá los hallazgos del checker y cambiá lo vago por lo
   directo. Leé oraciones vecinas juntas buscando formas repetidas.

Respetá la variante del español del autor: si escribe con voseo, con tuteo o de usted,
la edición sigue igual. No la pases a español neutro ni a otra variante.

No fabriques personalidad agregando opiniones, errores, fragmentos o una cuota de
oraciones cortas. No agregues un número a cada afirmación. Usá sólo datos que dio el
autor o que verificaste en una fuente adecuada. Si falta uno, dejá `[DATO: …]` y
preguntá.

El checker puede marcar lenguaje válido. Mirá el hallazgo antes de tocarlo. Nunca
escondas prosa en formato de código para subir el puntaje. Si una frase necesaria sigue
disparando una regla, explicalo.

## Paso 3: Segunda pasada con otra familia de modelos

Una familia distinta de la que escribió el borrador revisa con el mismo lector y
propósito. Revisá sus sugerencias antes de aceptarlas.

| Borrador escrito con | Comando |
|---|---|
| Claude | `python3 segunda_pasada.py borrador.md --autor claude > limpio.md` |
| GPT / Codex / ChatGPT | `python3 segunda_pasada.py borrador.md --autor gpt > limpio.md` |
| Gemini | `--autor gemini` usa la CLI rival que esté instalada |

El texto editado sale por la salida estándar y las notas por la de error.

Códigos de salida:

- 66: el borrador no se puede leer, no está en UTF-8 o está vacío.
- 70: la CLI rival falló. Su error sale por la salida de error.
- 124: se cortó por tiempo.
- 127: no hay CLI rival. Lo que salió es el prompt con el borrador, **no** un texto
  editado: pegalo en el chat de la otra familia.

Si no hay acceso a un segundo modelo, decí que la pasada no se hizo y seguí con la
revisión editorial y el checker.

El modelo separa las notas con `<<<SLOPMONSTRUO-NOTAS>>>`. Si aparece un aviso de que
falta el marcador, puede haber notas mezcladas en el texto: revisalo.

## Paso 4: Comparar y volver a chequear

Compará el resultado con el original. Revisá hechos y comandos, que los links y los
marcadores `[DATO: …]` hayan sobrevivido, y leé la apertura en contexto.

```
python3 slop_monstruo.py limpio.md
```

Resolvé los hallazgos sin cambiar el sentido. Reportá las excepciones justificadas. La
revisión editorial final va siempre, aunque dé 5/5.

Si cambiás una regex, corré `python3 pruebas/test_slop_monstruo.py`. Si cambiás la
segunda pasada, corré `python3 pruebas/test_segunda_pasada.py`.

## Cifras y afirmaciones

Nunca inventes evidencia: clientes, usuarios, suscriptores, vistas, alumnos,
testimonios o resultados. La regla de prueba sólo ve un número al lado de un sustantivo.
No sabe si es verdad. Usá `--permitir-prueba` sólo después de verificar la cifra con el
autor o con su fuente: deja el aviso y saca la penalidad.

## Qué entregás

El texto reescrito, o el archivo guardado donde se pidió. Después, hasta cinco notas
cortas con los cambios importantes y el resultado del checker. Decí si la segunda
pasada se hizo. Dejá a la vista las cifras sin resolver y los hallazgos que quedan. No
digas que la edición prueba autoría humana.
