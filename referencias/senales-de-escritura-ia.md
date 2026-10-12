# Señales de escritura de IA: el catálogo

Este catálogo lista patrones para revisar al editar. Es la versión en español del
catálogo de SlopMonster, de Jack Roberts, que se basa en *Signs of AI writing* de
Wikipedia (mantenido por WikiProject AI Cleanup) y en los proyectos de
[fuentes.md](fuentes.md). Estos patrones también aparecen en textos escritos por
personas.

Los cinco grupos corresponden a las categorías que puntúa el checker, pero algunos
consejos piden criterio editorial y no tienen chequeo automático. Leé los hallazgos en
contexto. Las reglas automáticas completas están en `slop_monstruo.py`.

---

## 1 · Vocabulario

Revisá estas palabras cuando aparecen en un uso vago o promocional. Dejá los términos
técnicos necesarios y los sentidos literales que le quedan al texto, y reportá lo que
siga marcado.

**Palabras y frases para revisar:**
`sumergirse` · `profundicemos` · `potenciar` · `aprovechar al máximo` · `sin fisuras` ·
`sin esfuerzo` · `robusto` · `desbloquear` · `desatar` · `liberar el poder` ·
`empoderar` · `de vanguardia` · `de última generación` · `revolucionario` ·
`transformador` · `innovador` · `holístico` · `sinergia` · `paradigma` · `meticuloso` ·
`tapiz` · `es un testimonio de` · `un faro de` · `sin precedentes` · `inigualable` ·
`llevar al siguiente nivel` · `cambia las reglas del juego` · `esto lo cambia todo` ·
`brutal` · `vertiginoso` · `ecosistema` · `solución integral`

**Frases hechas:**
`en el mundo de` · `en la era de` · `en el panorama actual` · `en un mundo cada vez más…` ·
`en constante evolución` · `no busques más` · `embarcate` · `abrochate el cinturón` ·
`el ingrediente secreto` · `este viaje` · `navegar por el` · `el poder de la IA` ·
`es importante destacar` · `cabe destacar` · `vale la pena mencionar` · `dicho esto` ·
`sin lugar a dudas` · `la inteligencia artificial llegó para`

**Para revisar en contexto (segundo nivel):**
`crucial` · `fomentar` · `intuitivo` · `de clase mundial` · `de primer nivel` ·
`impresionante` · `agilizar`

El checker no da tolerancia por frecuencia: con una sola aparición ya marca. Cambiá la
palabra vaga por una explicación de lo que pasa. Muchas veces alcanza con un verbo
simple como `usar` o `armar`.

**Límite conocido:** el checker compara sin tildes, así que el imperativo `potenciá`
queda igual que el sustantivo `potencia` y no se caza. Las demás formas del verbo
(`potenciamos`, `potenciar`, `potenciado`) sí.

## 2 · Construcciones (las formas)

Revisá la forma de las oraciones además de las palabras sueltas:

| Forma | Ejemplo | Arreglo |
|---|---|---|
| `no es solo X, es Y` | `No es solo un curso, es un viaje` | Cortá la primera cláusula, quedate con la afirmación |
| `no solo X, sino Y` | `No solo edita, sino que publica` | Igual |
| `sin X, sin Y, solo Z` | `Sin código, sin servidores, solo un prompt` | Decí qué hace Z |
| `más que un simple…` | `Más que un simple editor` | Decí qué es |
| `ya seas X o Y` | `Ya sea que estés empezando o seas experto…` | Nombrá al lector que tenés en mente |
| `ahí es donde entra X` | `Ahí es donde entra Claude` | Decí qué hace X |
| `decile adiós a` | `Decile adiós a las planillas` | Nombrá lo que las reemplaza |
| `imaginá un…` | `Imaginá un mundo donde…` | Mostralo |
| beneficio con cobertura | `puede ayudarte a` | Describí el beneficio con la certeza que da la evidencia |
| cautelas apiladas | `podría potencialmente` | Sacá la cautela de más sin borrar la incertidumbre real |
| pregunta que se responde sola | `¿El resultado? Un canal que crece.` | Una oración |
| cierre de ensayo | `En conclusión`, `En resumen` | Cortalo o cerrá con lo que el lector hace después |
| arranque de carraspeo | `La clave está en…`, `La verdad es que…` | Empezá por la idea |
| CTA de manual | `¿Listo para empezar?`, `Manos a la obra` | Un solo llamado a la acción, concreto, dicho una vez |

Revisá también oraciones vecinas que repiten una metáfora, fabrican un contraste entre
públicos o meten un segundo gancho antes de explicar el primero. Esos problemas piden
leer el párrafo entero.

Sacá comentarios sobre el propio proceso y resúmenes repetidos. Usá el formato para que
el lector pueda escanear. Dejá que el largo de párrafos y oraciones siga al material.

**Para revisar a mano (sin regla automática):**
- Títulos con Mayúscula En Cada Palabra, calcados del inglés. En español va mayúscula
  sólo al principio y en nombres propios.
- Comillas inglesas y anglicismos de traducción (`aplicar` por `postularse`, `en orden
  a`, `basado en` repetido).
- Un cambio de variante a mitad del texto: voseo en un párrafo y tuteo en el
  siguiente, o `ustedes` mezclado con `vosotros`.

## 3 · Cadencia de puntuación

- Rayas (—) repetidas en una oración. Fijate si las interrupciones la hacen más difícil
  de seguir. El checker usa ventanas de 220 caracteres.
- Compuestos con guion apilados (`end-to-end`, `state-of-the-art`): cuatro en una misma
  ventana.
- Densidad de punto y coma, con un umbral que crece con el largo del texto.

La puntuación puede ser correcta aunque dispare una regla. Revisá la lectura y dejá las
salvedades necesarias para la exactitud.

## 4 · Ritmo

El checker reconoce la enumeración de a tres que cierra una cláusula, como `rápido,
simple y efectivo.` Una lista de nombres propios (`Canva, Figma y Blender`) no cuenta.
Revisá si cada ítem aporta información. Dejá una lista útil con su largo natural. La
cantidad de ítems no dice quién la escribió.

## 5 · Prueba inventada

Nunca inventes cantidades de clientes, suscriptores, alumnos ni otra evidencia. El
checker marca números cerca de ciertos sustantivos, pero no puede saber si están
respaldados. Verificá el dato con el autor o con su fuente antes de usar
`--permitir-prueba`, que deja el aviso y saca la penalidad. Revisá también fechas y
especificaciones, aunque ninguna regla las marque.

---

## Revisá el borrador completo

Usá [principios.md](principios.md) para chequear el lector y el propósito, la
apertura, el recorrido entre oraciones, la evidencia y la voz. Sacar los patrones
reconocidos es sólo una parte de la edición. No metas fragmentos ni opiniones a la
fuerza para que parezca personal.
