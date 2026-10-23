# Verificación contra el programa original

Este documento guarda las comprobaciones hechas sobre la versión en español y
sobre el programa nuevo, con los números que las sostienen. Está escrito para
poder mostrarse en una auditoría: cada afirmación dice qué se ejecutó y qué
resultado dio.

La guía de usuario de Sandia advierte, en su sección 1.2:

> *"Any versions that have been modified by users may not reflect the same
> results."*

Este laboratorio modificó la herramienta (la tradujo, unió módulos y reescribió
el programa). Lo que sigue es la respuesta concreta a esa advertencia.

---

## 1. El cálculo es el mismo que el del programa original

| Comprobación | Resultado |
|---|---|
| 1,180 valores de referencia tomados del motor Java original, recalculados con el programa nuevo | **0 diferencias** a 10 decimales |
| 57 valores de un escenario de mitigaciones variables, Java contra Python | **0 diferencias** |
| Archivos `.raml` exportados por el programa nuevo, abiertos con el programa Java original | **mismos puntajes** |
| Unión de los dos módulos de cada cuestionario, antes y después | **ningún número cambió** (40 valores comparados) |

Los valores de referencia están en `programa/pruebas/referencias/` y las pruebas
que los comparan corren con `python3 -m pytest` dentro de `programa/`.

---

## 2. Orden y agrupación frente al original en inglés

Se comparó el árbol completo de los dos cuestionarios: módulos, categorías,
subcategorías, preguntas, pesos, límites y criterios de puntuación.

### Bioprotección: es el mismo modelo

| Comparación | Resultado |
|---|---|
| Identificadores de pregunta compartidos | **105 de 105** |
| Orden de las preguntas | **idéntico** |
| Pesos de pregunta distintos | 0 |
| Límites distintos | 0 |
| Criterios de puntuación distintos | 0 |
| Estructura de las tres categorías de primer nivel | **idéntica** (46 / 28 / 31 preguntas) |
| Nodos de los perfiles de resultados | **idénticos** (8 perfiles, 118 categorías, 324 referencias a preguntas) |

La única diferencia es deliberada: el español tiene **un** módulo donde el inglés
tiene dos. Ver la sección 5, que explica por qué eso era necesario.

### Bioseguridad: es una revisión distinta, hecha por Sandia

Aquí sí hay diferencias, y conviene tener claro de dónde vienen.

| Archivo | Módulos | Preguntas | Perfiles | Categorías de resultado | Referencias a preguntas | Identificadores en común con el español |
|---|---:|---:|---:|---:|---:|---:|
| Inglés **vigente** (`Biosafety.raml`, en la raíz) | 2 | 105 | 19 | 155 | 276 | **0 de 105** |
| Inglés **de 2014** (dentro de `Java source.zip`) | 1 | 105 | 19 | **182** | **285** | **105 de 105** |
| Español oficial de Sandia | 1 | 105 | 19 | 182 | 284 | — |
| Corregido por el laboratorio | 1 | 105 | 19 | 182 | 284 | — |
| El que se entrega | 1 | 105 | 19 | 182 | 284 | — |
| El del programa en Python | 1 | 105 | 19 | 182 | 284 | — |

Aquí está la explicación completa, y es importante leer la tabla entera:

**El español no se tradujo del `Biosafety.raml` que está en la raíz.** Se tradujo
de otra revisión, la que viene dentro de `Java source.zip` en
`models/Biosafety/Biosafety.raml`, fechada en 2014. Con esa revisión el español
comparte **los 105 identificadores de pregunta**; con la de la raíz, **ninguno**.
Por eso la comparación válida es contra 285, no contra 276.

Contra esa revisión de 2014, el español es idéntico en todo: mismo orden de las
105 preguntas, misma jerarquía, mismos pesos, mismos límites, mismos criterios,
las mismas 50 categorías. Con **una** excepción, que es la siguiente sección.

Las cuatro filas en español son idénticas entre sí. Ninguna diferencia la
introdujo la traducción hecha aquí ni la corrección del laboratorio.

Y contra el inglés **vigente** el español difiere mucho, legítimamente, porque
son dos revisiones distintas del modelo: la revisión nueva reponderó el árbol de
resultados (los guantes, la ropa, la protección ocular y el calzado pesan 0.0 en
la nueva y pesaban 0.16, 0.09, 0.09 y 0.04 en la vieja; los aerosoles pasan de
1.0 a 0.36; el punzocortante de 1.0 a 0.55). Con 2.000 escenarios al azar
difieren 17 de los 19 perfiles, con diferencias de hasta 3.38 en una escala de 0
a 4.

**Qué significa para el laboratorio:** sus resultados de bioseguridad no son
comparables con los de alguien que use el `Biosafety.raml` inglés de hoy. No es
un defecto de la traducción; son dos revisiones. Bioprotección no tiene este
problema: ahí el archivo inglés del proyecto es byte por byte el mismo que el del
código fuente, así que el español corresponde a la revisión vigente.

La organización también difiere respecto del inglés vigente:

- El inglés agrupa en módulos «Facility» (52 preguntas) y «Agent» (53). El
  español pone las cuatro categorías de primer nivel en un solo módulo y en otro
  orden: infección (16), exposición (15), mitigaciones (37), consecuencias (37),
  mientras el inglés va exposición, mitigaciones, consecuencias, infección. En la
  práctica el español pregunta primero por el agente y luego por el laboratorio.
- En «Probabilidad de infección» el español añade una categoría envolvente,
  «Transmisibilidad», que el inglés no tiene, y mueve la vía «Ingestión» del
  primer lugar al último dentro de «Seres humanos» y «Animales».
- En «Consecuencias» el español reordena las subcategorías y reparte las
  consecuencias secundarias en dos categorías de primer nivel en vez de
  anidarlas.
- Al alinear las categorías equivalentes, tres de las cuatro coinciden pregunta
  por pregunta en pesos, límites y criterios; la de consecuencias difiere.

**Las dos portadas declaran la misma versión**: «RAM de Bioseguridad, Versión
1.0, Septiembre de 2010», SAND No. 2010-6487. El número de versión no distingue
las dos revisiones, así que conviene anotar en los expedientes del laboratorio
que se usa la revisión española oficial de Sandia, y no el archivo inglés de este
repositorio.

---

## 2 bis. La traducción oficial de Sandia perdió una referencia de puntuación

Éste es el hallazgo más importante de toda la verificación, y **está sin
resolver**: necesita una decisión del laboratorio.

Comparando el español contra la revisión inglesa de la que se tradujo (la de
2014), los 19 perfiles de resultados coinciden salvo uno:

| Perfil | Referencias a preguntas en el inglés de 2014 | En el español |
|---|---:|---:|
| **Probabilidad por ingestión (individuo)** | 21 | **20** |
| Los otros 18 perfiles | — | iguales |

La referencia que falta es:

> pregunta `8e15e478-850c-4136-b1b0-5f6ef7d00265`, con peso 0.13
> «¿Todos los agentes biológicos de este laboratorio figuran en los inventarios?»
> (*Are all biological agents in this laboratory inventoried?*), colgada de la
> categoría «Exposición por contacto».

Está en el inglés de 2014 y **no está en ninguna de las cuatro variantes
españolas**, incluida la oficial de Sandia. Es decir: la pérdida ocurrió en la
traducción que hizo Sandia, no aquí.

### Qué efecto tiene

El efecto es medible y **va siempre en la misma dirección: el español puntúa más
bajo**.

| | |
|---|---|
| Diferencia máxima | **1.072** en una escala de 0 a 4 |
| Con todas las respuestas iguales | 9.72 % más bajo |
| En relativo, en escenarios mezclados | hasta 30.89 % más bajo |
| Escenarios afectados (de 2.000 al azar) | **77.5 %** |
| Perfiles afectados | «Probabilidad por ingestión (individuo)» y, de rebote, «Probabilidad de transmisión secundaria (seres humanos)» (hasta 0.199) |

Dicho en claro: **el cuestionario en español subestima la probabilidad de
infección por ingestión**. En una herramienta de bioseguridad, ésa es la
dirección que importa, porque hace ver el riesgo menor de lo que el modelo
original calcula.

### Qué se puede hacer

Reponer la referencia es una línea en el archivo, y está comprobado que con eso
la diferencia cae a **0.000000000000 exacto sobre 38.000 valores**: el español
queda idéntico a la revisión inglesa de la que se tradujo.

**No se ha hecho**, porque cambia los puntajes de dos perfiles y ésa es una
decisión del laboratorio, no técnica. Las dos opciones son defendibles:

| Opción | A favor | En contra |
|---|---|---|
| **Reponerla** | El cálculo queda igual al del modelo original; deja de subestimar | Los resultados ya emitidos con la versión actual no serán comparables con los nuevos |
| **Dejarla como está** | Se mantiene idéntico al archivo oficial que Sandia publicó en español | Se conserva un defecto conocido que subestima el riesgo |

En cualquiera de los dos casos conviene **avisar a Sandia**, porque la errata es
de su traducción y afecta a todos los laboratorios hispanohablantes que usen ese
archivo.

---

## 3. Las ponderaciones, contra la tabla publicada por Sandia

El apéndice B de la guía de usuario publica la ponderación de cada pregunta de
bioprotección. Se midió la ponderación efectiva de cada pregunta en el modelo que
usa el laboratorio (perturbando una respuesta a la vez y observando el cambio en
cada perfil) y se comparó.

**Coinciden exactamente**, con el valor publicado al segundo decimal:

| Pregunta | Publicado | Medido |
|---|---:|---:|
| Frecuencia de muerte en humanos (mortalidad) | 33.75 % | **33.75 %** |
| Morbilidad esperada en animales | 11.25 % | **11.25 %** |
| Tratamientos post-exposición para humanos | 9.20 % | **9.20 %** |
| Tratamientos post-exposición para animales | 9.00 % | **9.00 %** |
| Pruebas diagnósticas para humanos | 5.40 % | **5.40 %** |
| Medidas preventivas para humanos | 5.40 % | **5.40 %** |
| Pruebas diagnósticas para animales | 5.20 % | **5.20 %** |
| Medidas preventivas para animales | 5.20 % | **5.20 %** |
| Condiciones de largo plazo | 2.70 % | **2.70 %** |
| Duración de la infección | 1.13 % | **1.13 %** |

Que diez valores tan particulares coincidan al centésimo confirma que el modelo
que usa el laboratorio es el que la guía documenta.

En el bloque de seguridad, normalizando dentro de cada bloque para que la
comparación no dependa de la escala, coinciden dentro de 0.25 puntos
porcentuales **21 de 35** preguntas para el adversario interno y **16 de 26**
para el externo.

Las que no coinciden son diferencias reales entre la tabla publicada y el modelo
Java, heredadas de Sandia e idénticas en inglés y en español:

| Pregunta | Publicado | Medido |
|---|---:|---:|
| ¿Se portan credenciales? (adversario externo) | 8.00 % | 0.15 % |
| Áreas de almacenamiento con control de acceso (externo) | 6.00 % | 11.46 % |
| El edificio limita el acceso cuando está desocupado (externo) | 10.80 % | 8.02 % |
| Evaluación y respuesta a alarmas (externo) | 3.60 % | 5.73 % |
| Credenciales con foto y devolución de credenciales (interno) | 3.60 % | 1.37 % |

El caso de las credenciales merece una nota: la guía le asigna 8.00 % para el
adversario externo, que sería el peso más alto de toda su sección de
confiabilidad del personal, mientras todas las demás filas de esa sección valen
0.00 % para el externo. Puede ser una errata de la guía. En cualquier caso, el
modelo Java le da un peso casi nulo.

**Conclusión:** la guía documenta la versión en Excel y .NET de BioRAM Security
v4.0; el modelo Java 4.0.5 es la misma metodología y en su mayor parte las mismas
ponderaciones, pero no es la misma revisión. Si alguna vez hay que defender un
número frente a la guía publicada, conviene saberlo.

---

## 4. El ejemplo publicado de *Bacillus anthracis*

La guía trae un ejemplo resuelto (sección 3.1.1): las respuestas pregunta por
pregunta para un aislado de *Bacillus anthracis* y el resultado publicado,
**0.73 de consecuencia para humanos y 0.74 para animales**.

Se reprodujo con el modelo del laboratorio. Hay una complicación que es ella
misma un hallazgo: **la guía y el cuestionario invierten la escala en las
preguntas de mitigación**. La guía pregunta «¿Existen pruebas diagnósticas
efectivas?» y anota «Sí (valor 1)»; el cuestionario pregunta lo mismo pero sus
criterios son «0 = Sí, 2 = Se desconoce, 4 = No». Por eso el ejemplo se calculó
de las dos maneras posibles:

| Lectura | Humanos | Animales |
|---|---:|---:|
| Por el **texto** de la respuesta elegida | 0.6325 | 0.6595 |
| Por el **valor numérico** que imprime la guía | 0.8208 | 0.8478 |
| **Publicado por Sandia** | **0.73** | **0.74** |

El valor publicado queda entre las dos lecturas y ninguna lo reproduce exacto.
Es lo que cabía esperar de la sección 3: la guía documenta la versión en Excel,
cuyo conjunto de preguntas no es idéntico al del modelo Java. Por ejemplo, la
guía incluye una pregunta sobre signos clínicos que el modelo Java no tiene, y el
modelo Java coloca «impacto social» y «estabilidad del agente» en una rama
distinta de la que usa la guía.

Lo que sí importa para el uso diario, y está resuelto: **el programa muestra en
pantalla los criterios del propio cuestionario**, con su texto y su número, así
que quien contesta no puede equivocarse de dirección aunque haya leído la guía
antes.

---

## 5. El defecto de los dos módulos: causa raíz

Se había observado que, en bioprotección, 46 respuestas se perdían al guardar y
recargar. Ahora está localizada la causa exacta.

En el archivo del modelo, los dos módulos **comparten el mismo identificador de
raíz**:

```
Biosecurity.raml
  576988d3-4795-4710-9ac9-966ee6c0fba7  «Facility»
  576988d3-4795-4710-9ac9-966ee6c0fba7  «Agent»     <- el mismo
```

`RamFileMarshal.addResponsesToModel` localiza el módulo al que pertenece cada
conjunto de respuestas comparando ese identificador. Al estar repetido, los
conjuntos de los dos módulos se cargan en los dos, y el último procesado
sobrescribe al anterior: el módulo «Facility» acaba con los conjuntos del módulo
«Agent» y sus propias 46 respuestas quedan inalcanzables.

Comprobación directa, contestando las 105 preguntas, grabando, recargando y
seleccionando el conjunto guardado:

| Archivo | Módulos | Respuestas recuperadas |
|---|---:|---|
| `Biosecurity.raml` (inglés, dos módulos con el **mismo** identificador) | 2 | **0 de 46** y 59 de 59 |
| `Biosafety.raml` (inglés, dos módulos con identificadores **distintos**) | 2 | 52 de 52 y 53 de 53 |
| `BioRAM-es/Biosecurity_es.raml` (módulos unidos aquí) | 1 | **105 de 105** |
| `BioRAM-es/Biosafety_es.raml` (un solo módulo) | 1 | **105 de 105** |

El archivo se graba bien: el conjunto escrito contiene las 46 y las 59
respuestas. Lo que falla es la carga.

Dos consecuencias prácticas:

1. **Unir los módulos no fue un rodeo, fue el arreglo correcto.** Un módulo, un
   identificador, sin colisión.
2. **La versión 4.0.6 no lo corrige.** Dentro de `CDC BioRAM.zip` de este
   repositorio hay un `bioram-4.0.6.exe` (de septiembre de 2016, compilado por
   otra persona de Sandia) que añade una clase `ResponseSetGroup` y cambia justo
   las clases implicadas. Se probó con el mismo arnés: da exactamente el mismo
   resultado, 0 de 46. El problema está en los datos del modelo, no en el código.

El defecto afecta igual al archivo inglés, al español oficial de Sandia y a la
versión del CDC de 2015: los tres traen el identificador repetido.

---

## 6. Cómo se leen los resultados

Esto no es un detalle de programación: es lo que hay que saber para no leer mal
un resultado.

### La escala

Todas las preguntas van de **0 a 4** en los dos cuestionarios (verificado: los
105 límites de cada archivo son `0.0`–`4.0`). Los resultados salen en la misma
escala. **Más alto es peor.**

La guía añade algo que el programa ya permite: *"the user of the tool can answer
any question with a continuous value between 0 and 1, but they should use the
defined discrete values to help guide their final number"*. Es decir, se puede
contestar con un valor intermedio, usando los criterios como guía. En el programa
nuevo eso es la opción «Otro valor…».

### La dirección de cada pregunta no es la misma

Dentro de la sección del laboratorio hay dos tipos de pregunta:

- **Exposición**: 4 significa más exposición, o sea peor. «Hay muchas
  posibilidades de que se generen aerosoles» = 4.
- **Mitigación**: 4 significa que **no** hay medida. «Ninguna existe» = 4,
  «Existen medidas efectivas» = 0.

Las dos direcciones conviven en el mismo cuestionario, y el criterio de cada
pregunta lo dice. Por eso el programa muestra siempre el texto del criterio junto
al número.

### El modelo es multiplicativo, no una suma de puntos

Esto explica un resultado que parece un error y no lo es. La metodología de
Sandia es:

```
Riesgo = PA × (1 − PE) × C
```

donde PA es la probabilidad de ataque, PE la efectividad del sistema de seguridad
y C la consecuencia. Al ser un producto, **el aporte de cada pregunta depende de
las demás**. Comprobado:

- En bioprotección, una misma pregunta aporta +0.0515 cuando todo lo demás está en
  0 y +0.0257 cuando todo lo demás está en 2: exactamente la mitad, como
  corresponde a un producto.
- En bioseguridad hay preguntas que aportan **0.0000** con todo lo demás en 0 y
  +0.4963 con todo lo demás en 2.

De ahí la consecuencia que más confunde: **si se contestan todas las preguntas
del laboratorio con 0, el riesgo sale 0.0000**. No es una falla. «Todo en 0»
describe un laboratorio donde no hay ninguna vía de exposición: sin exposición no
hay probabilidad de infección, por buenas o malas que sean las medidas. Para
describir un laboratorio malo hay que dejar la exposición alta (el procedimiento
es el que es) y bajar las mitigaciones.

Hecho así, el modelo se mueve en la dirección correcta. Mismo agente peligroso y
mismo procedimiento, cambiando solo las medidas del laboratorio:

| Resultado | Medidas buenas | Medidas a medias | Sin medidas |
|---|---:|---:|---:|
| Probabilidad por inhalación (individuo) | 0.9381 | 2.9052 | 4.0000 |
| Probabilidad percutánea (individuo) | 1.0119 | 2.9175 | 4.0000 |
| Probabilidad por contacto (individuo) | 1.6149 | 2.9926 | 3.8473 |
| Probabilidad por inhalación (comunidad) | 0.2828 | 2.8355 | 4.0000 |
| Consecuencia de la enfermedad para los seres humanos | 0.7990 | 0.7990 | 0.7990 |

Los 57 valores de esta tabla coinciden entre el Java original y el programa
nuevo, sin diferencias.

La última fila no cambia, y está bien que no cambie: la consecuencia de la
enfermedad depende del agente, no del laboratorio. El programa lo dice en el
reporte, en la columna «De qué depende».

### Que los resultados son relativos, no absolutos

La guía insiste en esto y conviene repetirlo:

> *"While the results of the tool are quantitative, this model is not intended to
> provide an assessment of absolute risk but rather provide a structured method
> for the comparison of the relative risks posed by laboratory practices and by
> biological material present at a facility."*

Sirven para comparar entre cepas, entre áreas y entre antes y después de una
mejora. No son una probabilidad de que algo pase.

---

## 7. Red, envío de información y datos de origen

Auditado y documentado en [`AVISO.md`](AVISO.md), secciones 5 y 6. En resumen:
ninguno de los dos programas abre conexiones de red, envía informes ni manda
información a ningún lado. El único punto a corregir, que no es de red, es que el
programa Java deja los informes que genera en la carpeta temporal del sistema sin
borrarlos.
