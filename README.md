# Slop Monstruo

Slop Monstruo revisa textos en español buscando marcas comunes de escritura de IA. Sirve
para cualquier texto que vaya a leer otra persona: un guion, la descripción de un video,
el texto de un Reel, una página de venta, un mail o un README.

Tiene dos partes. Un checker en Python marca coincidencias en cinco categorías y le pone
al texto un puntaje sobre 5. Un flujo de edición ([SKILL.md](SKILL.md)) le pide a un
agente de IA que revise el borrador para su lector, lo reescriba y pida otra pasada a una
familia de modelos distinta.

Un 5/5 significa que el checker no encontró coincidencias. Igual tenés que revisar si el
texto se entiende, si respalda lo que afirma y si le da al lector lo que vino a buscar.

Lo hizo [Axel Laban](https://www.youtube.com/@soyaxellaban) a partir de
[SlopMonster](https://github.com/ItsssssJack/SlopMonster), de Jack Roberts, que revisa
textos en inglés. Acá las reglas están reescritas para el español. Más abajo está
[qué cambia respecto del original](#qué-cambia-respecto-de-slopmonster).

## Uso rápido

El checker usa Python 3 y su biblioteca estándar. No necesita claves ni paquetes.

```
git clone https://github.com/axellaban/Slop-monstruo
cd Slop-monstruo

# Revisar un texto corto. Da 3/5 y sale con 1.
python3 slop_monstruo.py --texto "No es solo una herramienta, es un viaje revolucionario."

# Revisar un archivo
python3 slop_monstruo.py borrador.md
python3 slop_monstruo.py borrador.txt
python3 slop_monstruo.py pagina.html
```

Cada categoría con hallazgos resta un punto, sin importar cuántos tenga. Sale con 0 en
5/5 y con 1 debajo. La entrada vacía también falla. El archivo revisado queda igual.

En Markdown se saltean los bloques de código, el código en línea, las imágenes y los
ejemplos tachados. En HTML se sacan las etiquetas y el contenido de script y style. No
renderiza la página, así que el texto escondido por CSS puede entrar igual. Un `.txt` se
lee como texto plano.

## Usarlo como skill

En Claude Code, cloná el repo en tu carpeta de skills y llamalo con `/slop-monstruo` o
diciéndole "pasalo por Slop Monstruo":

```
git clone https://github.com/axellaban/Slop-monstruo ~/.claude/skills/slop-monstruo
```

Para un solo proyecto, clonalo en `.claude/skills/slop-monstruo/` dentro de ese proyecto.
Con Codex u otro agente, pedile que siga [SKILL.md](SKILL.md).

## Editar un borrador

Pasale al agente el archivo. Si no se deduce del texto, aclarale quién lo va a leer y
dónde va a aparecer.

1. Corre el checker para ver los patrones que reconoce.
2. Revisa el propósito y el orden. Un guion arranca por la promesa y la prueba. Una
   descripción de YouTube dice de qué trata el video antes de los links.
3. Reescribe los pasajes vagos o repetitivos y chequea que las afirmaciones coincidan con
   los datos que hay.
4. Pide una segunda pasada a otra familia de modelos, revisa los cambios y vuelve a
   correr el checker.

La segunda pasada usa [prompts/segunda-pasada.txt](prompts/segunda-pasada.txt). Con una
CLI de IA instalada y autenticada:

```
# Si el borrador lo escribió Claude, la pasada la hace GPT con la CLI codex.
python3 segunda_pasada.py borrador.md --autor claude > limpio.md

# Si lo escribió GPT, la pasada la hace Claude con la CLI claude.
python3 segunda_pasada.py borrador.md --autor gpt > limpio.md

# Leé el resultado y volvé a chequearlo.
python3 slop_monstruo.py limpio.md
```

`--autor` es la familia que escribió el borrador. El texto editado sale por la salida
estándar y las notas de cambios por la de error. Usa el modelo que tenga configurado la
CLI instalada.

Si falta la CLI rival, imprime el prompt y el borrador y sale con 127: pegalo en el chat
de la otra familia. Si se pasa del tiempo, sale con 124. Revisá el código de salida
antes de tratar lo que salió como un texto editado.

Otro modelo da otra pasada de edición. No garantiza mejor escritura. Revisá el resultado
buscando hechos cambiados y contexto perdido antes de aceptarlo.

## Qué marca el checker

| Categoría | Qué revisa |
|---|---|
| Vocabulario | Palabras como `sumergirse`, `potenciar` o `sin fisuras`, con sus flexiones, y frases hechas como `en el mundo de`. |
| Construcciones | Formas como `no es solo X, es Y`, `ya seas X o Y`, cautelas apiladas y preguntas que se responden solas. |
| Puntuación | Dos o más rayas o cuatro compuestos con guion en una ventana de 220 caracteres, y exceso de punto y coma. |
| Ritmo de a tres | Una enumeración triple que cierra la cláusula, como `rápido, simple y efectivo.` Las listas de nombres propios no cuentan. |
| Prueba posiblemente inventada | Números cerca de sustantivos como `usuarios`, `clientes` o `suscriptores`. No puede verificar el dato. |

Las reglas están en [slop_monstruo.py](slop_monstruo.py). El catálogo editorial más amplio
está en [referencias/senales-de-escritura-ia.md](referencias/senales-de-escritura-ia.md).
Algunas entradas del catálogo piden criterio editorial y no tienen chequeo automático.

Si una cifra marcada es real y la podés respaldar:

```
python3 slop_monstruo.py pagina.html --permitir-prueba
```

Sigue mostrando la cifra pero deja de restar. No verifica la evidencia.

## Qué cambia respecto de SlopMonster

SlopMonster busca patrones del inglés. Este texto en español le da 5/5, limpio, porque
ninguna de sus reglas coincide:

> ~~No es solo una herramienta, es un viaje revolucionario. Potenciamos tu negocio con
> una solución robusta y sin fisuras. Más de 10.000 usuarios felices. Es rápido, simple y
> efectivo.~~

Slop Monstruo le da 1/5: marca la construcción del arranque, cuatro palabras de
vocabulario, la terna del final y la cifra de usuarios sin respaldo.

Mantiene las cinco categorías y el flujo de edición del original, y cambia esto:

- **Vocabulario con flexiones.** El español cambia la palabra según el género, el número
  o la persona, así que cada palabra tiene su propia regex: `potenciamos`, `potenciado` y
  `potenciar` caen en la misma regla.
- **Sin tildes al comparar.** `sólo` y `solo`, `imaginá` e `imagina` matchean igual, sin
  duplicar cada patrón.
- **Construcciones del español.** El sujeto se cae (`no es solo una herramienta, es un
  sistema`) y el voseo aparece en frases como `decile adiós a` o `imaginá un mundo`.
- **Ritmo de a tres sin coma de Oxford.** En español la enumeración no lleva coma antes de
  la `y`. La regla marca la terna cuyo último ítem es corto y cierra la cláusula, acepta
  `e` como conjunción y deja pasar las listas de nombres propios.
- **Prueba inventada con sustantivos en español.** Suscriptores, alumnos, seguidores o
  clientes, con cifras como `10.000` o `3,5 millones`.
- **Segunda pasada en Python.** El original la hace con un script de bash. Esta versión
  corre con Python, no necesita bash y elige la familia rival con `--autor`.
- **La variante del autor se respeta.** El prompt de la segunda pasada mantiene el voseo,
  el tuteo o el usted del borrador, y deja `[DATO: …]` donde falta un dato en vez de
  inventarlo.

## Límites

Las reglas son de español y comparan sin tildes ni mayúsculas. El imperativo `potenciá`
queda igual que el sustantivo `potencia` y no se caza. Un texto en otro idioma puede dar
5/5 porque las reglas no coinciden.

Puede marcar lenguaje común y dejar pasar texto malo. No sabe quién escribió el texto,
no verifica datos y no juzga si un gancho le queda al público. Sus hallazgos son puntos
para revisar. Un 5/5 solo no prueba que el texto esté bien escrito.

## Control en CI

Como un puntaje debajo de 5/5 sale con error, podés correr el checker en la integración
continua de tu repo y hacer fallar el build cuando un texto publicado tiene marcas.

El [workflow de este repo](.github/workflows/slop.yml) corre las pruebas y revisa este
README y un texto de muestra. Copialo a tu repo y cambiá las rutas por los archivos que
publicás. Para bloquear un merge o un deploy tenés que configurar las reglas de tu repo.

```
python3 pruebas/test_slop_monstruo.py
python3 pruebas/test_segunda_pasada.py
python3 slop_monstruo.py README.md
```

## Ejemplos y fuentes

- [Antes y después](ejemplos/antes-despues.md): seis marcas típicas con su arreglo.
- [Principios de edición](referencias/principios.md): los chequeos que el puntaje no hace.
- [Fuentes](referencias/fuentes.md): el catálogo de Wikipedia, SlopMonster y los
  proyectos de código abierto en los que se basa.

## Licencia

[MIT](LICENSE). Slop Monstruo es de Axel Laban y parte de SlopMonster, de Jack Roberts,
que también es MIT. Si lo copiás o lo modificás, conservá el archivo `LICENSE` con los
dos avisos de copyright.

## In English

Slop Monstruo is a Spanish adaptation of Jack Roberts' SlopMonster by Axel Laban. The
checker rules are rewritten for Spanish grammar and the second pass runs in Python. MIT
license.
