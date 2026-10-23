# Carta a Sandia National Laboratories

Borrador de la carta para pedir a Sandia la aclaración de la licencia y el
permiso de uso, y para informarles de los defectos que encontramos en sus
archivos. Abajo está la versión en inglés, que es la que se envía, y la
traducción al español para revisarla antes de mandarla.

---

## A quién escribirle

**BioRAM** lo hace el programa **Global Chemical and Biological Security (GCBS)**
de Sandia National Laboratories. Sandia es un laboratorio nacional de Estados
Unidos que trabaja para la Administración Nacional de Seguridad Nuclear (NNSA)
del Departamento de Energía; existe desde 1949 y su sede está en Albuquerque,
Nuevo México. Desde 2017 lo opera National Technology & Engineering Solutions of
Sandia (NTESS), antes era Sandia Corporation, de Lockheed Martin — por eso los
avisos viejos dicen «Sandia Corporation».

El programa GCBS no es la parte nuclear: se dedica a bioseguridad y
bioprotección de laboratorios en todo el mundo, siguiendo las recomendaciones de
la OMS, y por eso publicó BioRAM traducido a once idiomas. BioRAM se desarrolló
primero con fondos internos de Sandia y después con apoyo del programa de
Agentes Selectos de los CDC y del Programa de Colaboración en Bioprotección del
Departamento de Estado. Es decir: es gente que hace exactamente lo mismo que
nosotros y que publicó la herramienta para que laboratorios como el nuestro la
usen.

| Destinatario | Dirección | Por qué |
|---|---|---|
| **Para** | `ContactGCBS@sandia.gov` | Es el buzón institucional del programa que hace BioRAM |
| **Copia** | `sacaske@sandia.gov` | Es el contacto que la propia portada del cuestionario publica |

Si no responden en unas semanas, la otra vía es abrir un *issue* en el
repositorio oficial, <https://github.com/sandialabs/BioRAM>, que es donde
publican la herramienta.

---

## Versión en inglés (la que se envía)

**Asunto:** BioRAM in Mexico — license question, and three findings in the
Spanish and English model files

---

Dear GCBS team,

I am writing from the **Laboratorio Estatal de Salud Pública de Nayarit (LESP
Nayarit)**, the state public health laboratory of Nayarit, Mexico. We sit under
the state health commission for sanitary risk protection (CESPRISNAY) and the
Nayarit state health services (SSN).

First, thank you. We have been deploying BioRAM for our biosafety and
biosecurity risk assessments, and it has given us something we did not have
before: a structured, repeatable way to compare the risks of the different
agents we handle, area by area. The fact that you published it openly, and that
you went to the trouble of translating it into eleven languages, is the reason a
laboratory of our size can do this work at all. We are grateful for it.

Over the past weeks we translated the interface into Mexican Spanish, starting
from your own official Spanish `.raml` files, and we verified our work against
the original Java engine. During that verification we found three things we
think you will want to know about. We are reporting them because they affect
every laboratory using these files, not only us.

**1. A scoring reference is missing from the official Spanish Biosafety model.**

In the profile *Likelihood Ingestion Individual*, the category
`cef76a48-db4c-4b3b-b84a-010a6ae70e01` (raw weight 0.86, `normalizeChildren` set
to false) contains two question references in the English model and only one in
the Spanish. The missing one is:

```xml
<ResultQuestion>
    <questionUUID>8e15e478-850c-4136-b1b0-5f6ef7d00265</questionUUID>
    <rawWeight>0.13</rawWeight>
</ResultQuestion>
```

that is, *"Are all biological agents in this laboratory inventoried?"*

Because that category does not normalize its children, the missing term lowers
the result. Measured over 3,000 randomized response sets, the Spanish model
scores lower in **77.4 %** of cases, by 0.19 on the 0–4 scale on average (about
16 % relative, up to 0.91), and the effect propagates to *Likelihood of Secondary
Transmission Human* in a further 10.7 % of cases. Every difference is in the same
direction: **the Spanish model understates the likelihood of infection by
ingestion.** Restoring the single node makes the Spanish model numerically
identical to the English one — zero difference across 7,600 computed values.

We have restored it in our copy and documented the change, but the file you
distribute still has it, and we assume other Spanish-speaking laboratories are
affected.

**2. Both question modules in `Biosecurity.raml` share the same root UUID.**

In the English `Biosecurity.raml`, the *Facility* and *Agent* modules both carry
`QuestionSetRoot` UUID `576988d3-4795-4710-9ac9-966ee6c0fba7`. Since
`RamFileMarshal.addResponsesToModel` matches a saved response set to its module
by that UUID, the response sets of both modules load into both, and the last one
processed wins.

The practical consequence is that **answers to the 46 Facility questions cannot
be recovered after saving and reloading.** We reproduced it by answering all 105
questions, saving, reloading and selecting the saved set: 0 of 46 Facility
answers came back, while all 59 Agent answers did. `Biosafety.raml`, whose two
modules have distinct root UUIDs, does not have the problem. We also reproduced
it with the 4.0.6 build in `CDC BioRAM.zip`, so it is in the model data rather
than in the code. The same duplicate UUID is present in the Spanish file and in
`BiosecurityAugust2015.raml`.

**3. The Spanish Biosafety translation tracks an earlier revision of the model.**

The Spanish Biosafety file shares all 105 question UUIDs with
`models/Biosafety/Biosafety.raml` inside `Java source.zip` (dated 2014), and none
with the current `Biosafety.raml` in the repository root. The two revisions
differ substantially in the result-profile weights, so Spanish-speaking and
English-speaking users of BioRAM are not currently producing comparable biosafety
scores. Both files declare "Version 1.0, September 2010", so the version string
does not distinguish them. This may well be intentional; we mention it in case it
is not.

We also found three wording errors in the official Spanish translation where a
negation was lost — in one of them the best available answer reads the same as
the worst, so a laboratory that does have written material-control procedures has
no correct option to choose. We can send the list if it is useful.

**Our questions**

The BioRAM Security User Guide (August 2021) states that "the BioRAM software
tool was developed as open source software per the requirements from the tool's
funding agencies". We would like to honor that properly, and two points are not
clear to us from the distributed files:

1. **Under which license is BioRAM released?** No `LICENSE` or `NOTICE` file
   accompanies the repository, the `.jar` or the source archive, so we cannot
   tell what attribution or redistribution terms apply.
2. **Do you consent to what we have done?** Specifically: translating the
   interface into Mexican Spanish, correcting the errors above in our copy,
   rebuilding the `.jar`, and reimplementing the calculation engine in Python so
   that both assessments can run in a single tool organized by laboratory area
   and strain. We have kept your copyright notices, the SAND number and the
   export-control notice intact, and our documentation states plainly that the
   method, the questionnaires and the weights are yours.

We would also ask about the export-control notice on the Biosecurity cover page,
since we are outside the United States and would like to be sure we are not
overstepping.

If it is useful to you, we are glad to contribute our corrections back, in
whatever form suits you — a pull request on `sandialabs/BioRAM`, corrected files,
or simply our verification notes. Our Python reimplementation reproduces your
engine exactly: 1,180 reference values taken from the original Java engine with
zero difference to ten decimal places, and ten of the weights published in
Appendix B of your user guide reproduce exactly to the hundredth.

Thank you again for making this tool available. It is doing real work in a public
health laboratory in western Mexico.

With appreciation,

[nombre]
[cargo]
Laboratorio Estatal de Salud Pública de Nayarit
Comisión Estatal para la Protección contra Riesgos Sanitarios de Nayarit
Servicios de Salud de Nayarit · Tepic, Nayarit, México
[correo] · [teléfono]

---

## Traducción al español (para revisar antes de enviar)

**Asunto:** BioRAM en México — consulta sobre la licencia y tres hallazgos en los
archivos del modelo en español y en inglés

Estimado equipo del GCBS:

Les escribo desde el **Laboratorio Estatal de Salud Pública de Nayarit (LESP
Nayarit)**, en México. Dependemos de la Comisión Estatal para la Protección
contra Riesgos Sanitarios de Nayarit (CESPRISNAY) y de los Servicios de Salud de
Nayarit (SSN).

Antes que nada, gracias. Hemos estado implantando BioRAM para nuestras
evaluaciones de riesgos de bioseguridad y bioprotección, y nos ha dado algo que
no teníamos: una forma estructurada y repetible de comparar los riesgos de los
distintos agentes que manejamos, área por área. Que lo hayan publicado
abiertamente, y que se hayan tomado el trabajo de traducirlo a once idiomas, es
la razón por la que un laboratorio de nuestro tamaño puede hacer este trabajo.
Se los agradecemos.

En las últimas semanas tradujimos la interfaz al español de México, partiendo de
sus propios archivos `.raml` oficiales en español, y verificamos nuestro trabajo
contra el motor Java original. Durante esa verificación encontramos tres cosas
que creemos que les va a interesar conocer. Se las informamos porque afectan a
todos los laboratorios que usan esos archivos, no sólo a nosotros.

**1. Al modelo oficial de bioseguridad en español le falta una referencia de
puntuación.** En el perfil *Likelihood Ingestion Individual*, la categoría
`cef76a48-…` (peso 0.86, `normalizeChildren` en falso) tiene dos referencias a
preguntas en el modelo inglés y sólo una en el español. Falta la de la pregunta
`8e15e478-…` con peso 0.13, «¿Todos los agentes biológicos de este laboratorio
figuran en los inventarios?».

Como esa categoría no normaliza los pesos de sus hijos, el sumando que falta baja
el resultado. Medido sobre 3.000 juegos de respuestas al azar, el modelo español
puntúa más bajo en el **77.4 %** de los casos, 0.19 de la escala 0–4 en promedio
(unos 16 % en relativo, hasta 0.91), y el efecto se propaga al perfil de
transmisión secundaria en otro 10.7 %. Todas las diferencias van en el mismo
sentido: **el modelo español subestima la probabilidad de infección por
ingestión.** Reponer ese único nodo deja el modelo español numéricamente
idéntico al inglés: cero diferencia en 7.600 valores calculados.

Nosotros ya lo repusimos en nuestra copia y lo documentamos, pero el archivo que
ustedes distribuyen sigue igual, y suponemos que hay otros laboratorios
hispanohablantes afectados.

**2. Los dos módulos de `Biosecurity.raml` comparten el mismo identificador de
raíz.** Los módulos *Facility* y *Agent* llevan los dos el UUID
`576988d3-…`. Como `RamFileMarshal.addResponsesToModel` localiza el módulo de un
conjunto de respuestas por ese identificador, los conjuntos de ambos se cargan en
ambos y el último procesado sobrescribe al anterior.

La consecuencia práctica es que **las respuestas de las 46 preguntas de
«Facility» no se pueden recuperar después de guardar y recargar.** Lo
reprodujimos contestando las 105 preguntas, grabando, recargando y seleccionando
el conjunto guardado: volvieron 0 de 46 respuestas de «Facility» y las 59 de
«Agent» completas. `Biosafety.raml`, cuyos dos módulos tienen identificadores
distintos, no lo sufre. También lo reprodujimos con la versión 4.0.6 de
`CDC BioRAM.zip`, así que está en los datos del modelo y no en el código. El
mismo identificador repetido está en el archivo español y en
`BiosecurityAugust2015.raml`.

**3. La traducción de bioseguridad al español corresponde a una revisión
anterior del modelo.** El archivo español comparte los 105 identificadores de
pregunta con `models/Biosafety/Biosafety.raml` de dentro de `Java source.zip`
(de 2014) y ninguno con el `Biosafety.raml` actual de la raíz del repositorio.
Las dos revisiones difieren bastante en los pesos de los perfiles de resultados,
así que hoy los usuarios en español y en inglés no producen puntajes de
bioseguridad comparables. Los dos archivos declaran «Versión 1.0, septiembre de
2010», de modo que el número de versión no los distingue. Puede ser
intencional; lo mencionamos por si no lo es.

También encontramos tres errores de redacción en la traducción oficial al
español donde se perdió una negación. En uno de ellos la mejor opción disponible
dice lo mismo que la peor, así que un laboratorio que sí tiene procedimientos
escritos de control de materiales no tiene ninguna opción correcta que elegir.
Podemos enviarles la lista si les sirve.

**Nuestras preguntas**

La *BioRAM Security User Guide* (agosto de 2021) dice que «the BioRAM software
tool was developed as open source software per the requirements from the tool's
funding agencies». Queremos respetarlo como corresponde, y hay dos puntos que
los archivos distribuidos no nos aclaran:

1. **¿Bajo qué licencia se libera BioRAM?** No viene ningún archivo `LICENSE` ni
   `NOTICE` con el repositorio, el `.jar` ni el código fuente, así que no podemos
   saber qué condiciones de atribución o redistribución aplican.
2. **¿Están de acuerdo con lo que hicimos?** En concreto: traducir la interfaz al
   español de México, corregir en nuestra copia los errores de arriba, rearmar el
   `.jar`, y reimplementar el motor de cálculo en Python para poder correr las dos
   evaluaciones en una sola herramienta, organizada por área del laboratorio y por
   cepa. Conservamos íntegros sus avisos de derecho de autor, el número SAND y el
   aviso de control de exportaciones, y nuestra documentación dice con claridad
   que el método, los cuestionarios y las ponderaciones son de ustedes.

También quisiéramos preguntarles por el aviso de control de exportaciones de la
portada de bioprotección, ya que estamos fuera de Estados Unidos y queremos estar
seguros de no excedernos.

Si les resulta útil, con gusto les devolvemos nuestras correcciones en la forma
que prefieran: una solicitud de cambios en `sandialabs/BioRAM`, los archivos
corregidos, o simplemente nuestras notas de verificación. Nuestra
reimplementación en Python reproduce su motor exactamente: 1.180 valores de
referencia tomados del motor Java original con cero diferencia a diez decimales,
y diez de las ponderaciones publicadas en el apéndice B de su guía de usuario se
reproducen exactas al centésimo.

Gracias de nuevo por poner esta herramienta a disposición de todos. Está haciendo
trabajo real en un laboratorio de salud pública del occidente de México.

Con aprecio,

[nombre]
[cargo]
Laboratorio Estatal de Salud Pública de Nayarit
Comisión Estatal para la Protección contra Riesgos Sanitarios de Nayarit
Servicios de Salud de Nayarit · Tepic, Nayarit, México
[correo] · [teléfono]

---

## Antes de enviarla

- [ ] Llenar nombre, cargo, correo y teléfono al pie.
- [ ] Confirmar que Tepic es la sede que quieren poner.
- [ ] Decidir si se adjunta `VERIFICACION.md`. Yo lo adjuntaría: respalda todo
      lo que la carta afirma y les ahorra pedirlo.
- [ ] Si quieren, agregar la lista de las tres erratas de redacción en lugar de
      ofrecerla. Está en `traduccion/corregir_erratas.py`, con el texto en inglés
      de cada una.
