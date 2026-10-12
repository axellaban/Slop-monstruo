# Fuentes

Slop Monstruo es la versión en español de
[SlopMonster](https://github.com/ItsssssJack/SlopMonster), de Jack Roberts, publicado
con licencia MIT. De ahí vienen las cinco categorías del puntaje, el flujo de edición
en cuatro pasos y la idea de pedir la segunda pasada a otra familia de modelos. Axel
Laban reescribió las reglas con construcciones propias del español y portó la segunda
pasada a Python.

El catálogo de patrones del original se armó con los recursos de abajo.

## Catálogo de patrones de escritura

[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
mantenido por WikiProject AI Cleanup, da ejemplos para revisar textos. Que un pasaje
coincida con un patrón no prueba quién lo escribió.

Estos proyectos de código abierto alimentaron la implementación original:

| Proyecto | Qué aportó |
|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | Categorías de patrones tomadas del catálogo de Wikipedia. |
| [harshaneel/humanize](https://github.com/harshaneel/humanize) | Referencias de investigación y patrones de puntuación. |
| [lguz/humanize-writing-skill](https://github.com/lguz/humanize-writing-skill) | Un flujo de edición en varias pasadas y listas de vocabulario. |
| [haidrrrry/humanize-ai-writing](https://github.com/haidrrrry/humanize-ai-writing) | Instrucciones que sirven como prompt de edición independiente. |

Cada proyecto tiene su propia documentación y licencia. Las reglas de
[slop_monstruo.py](../slop_monstruo.py) definen el puntaje. El catálogo de
[senales-de-escritura-ia.md](senales-de-escritura-ia.md) incluye chequeos que piden
criterio editorial.

## Guía editorial

*No me hagas pensar* (*Don't Make Me Think*), de Steve Krug, está detrás del énfasis en
que la información se entienda fácil. Los ejemplos de marketing se apoyaron en el orden
de presentación que arranca por el problema, de Daniel Priestley, y en el trabajo de
Alex Hormozi sobre ofertas y respaldo de afirmaciones.

[principios.md](principios.md) aplica esa guía según el propósito del texto. Un guion
arranca por la promesa y la prueba. Una página de venta puede necesitar plantear el
problema antes de la oferta. Ningún enfoque justifica inventar evidencia.

## Revisión con un segundo modelo

`segunda_pasada.py` manda el borrador a una familia de modelos distinta con una CLI
instalada. Usa el modelo que esa CLI tenga configurado y no fija una versión.

Nada en esta herramienta prueba que un segundo modelo edite mejor. Compará la salida con
el borrador buscando cambios de sentido y volvé a correr el checker. La herramienta no
dice probar autoría humana ni esquivar detectores de IA.
