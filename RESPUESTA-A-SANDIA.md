# Respuesta a Sandia — Robert Sleeper, licencia BSD-3

Borrador de la contestación al correo de **Robert Sleeper JD, Licensing
Executive de Sandia National Laboratories** (`rdsleep@sandia.gov`), recibido el
28 de octubre de 2026, en el que confirma que BioRAM se publicó sin licencia
atribuida y se compromete a ponerle una BSD de 3 cláusulas.

Igual que la primera carta: primero la versión en inglés, que es la que se
manda, y después la traducción al español para que se revise antes de enviarla.

## A quién

| | |
|---|---|
| **Para** | `rdsleep@sandia.gov` — Robert Sleeper, es quien contestó |
| **Copia** | `sacaske@sandia.gov` — el autor, que es quien tiene que atribuir la licencia y a quien le tocan los tres defectos |
| **Copia** | `ContactGCBS@sandia.gov` — el buzón por el que entró la consulta, para que quede en el mismo hilo |
| **Asunto** | `Re: Seeking use of SCR1186.1 BioRAM v. 4.0 (Open Source)` — conservar el asunto para que no se pierda el hilo |

## Qué busca esta carta

Cuatro cosas concretas, en orden de importancia:

1. Que la licencia se le atribuya **al artefacto correcto**, y que nos avisen
   con qué año, para poder incluir el aviso exacto.
2. Permiso sobre el **nombre**. La tercera cláusula de la BSD-3 prohíbe usar el
   nombre del titular para respaldar o promocionar productos derivados sin
   permiso escrito. Nuestro programa se llama «BioRAM LESP» y su icono lleva
   escrita la palabra «BioRam». Más vale preguntarlo ahora que corregirlo
   después, y Sleeper es justo quien puede responderlo.
3. La **advertencia de control de exportaciones** de la portada, que quedó sin
   contestar y nos aplica directamente por ser un laboratorio mexicano.
4. Que los **tres defectos** lleguen al autor.

---

## Versión en inglés (la que se envía)

**Asunto:** Re: Seeking use of SCR1186.1 BioRAM v. 4.0 (Open Source)

Dear Mr. Sleeper,

Thank you — this is exactly the clarity we needed, and we appreciate how quickly
it came.

Your assumption is correct on both counts. We are working with **SCR1186.1
BioRAM v. 4.0, the open source one**, and not with the proprietary version. For
the record, everything we used came from Sandia's own public repository at
`github.com/sandialabs/BioRAM`: the `bioram-4.0.5.jar`, the `Biosafety.raml`
and `Biosecurity.raml` model files, and `historico/sandia/Java source.zip`, which `sacaske`
uploaded to that repository on 6 February 2018. We mention the specific files so
that the license you attach lands on the right artifact.

What we have built with it, briefly: a complete Mexican-Spanish version for
Windows, and a new program in Python that reuses your questionnaires and
reproduces your scoring engine. We did not re-derive the method — the method,
the questionnaires and the weights are yours. Our implementation reproduces your
Java engine with **zero difference across 7,600 compared values**, and ten of
the weights published in Appendix B of your user guide reproduce exactly.

We will go forward as you suggest, and we are keeping your note on file as the
permission in the meantime. Four things would help us close this out properly.

**1. When BSD-3 is attached, could you let us know — and with which year?**
The copyright line in your message has the year marked "tbd". We would like to
carry your notice verbatim, so the exact year matters to us. We will include the
full BSD-3 text alongside our own license as soon as it exists.

**2. A question about the name, which is why we are raising it with you.**
BSD-3's third clause reserves the use of the copyright holder's name for
endorsing or promoting derived products. Our program is called **"BioRAM LESP"**
and the icon our laboratory made for it carries the word **"BioRam"**. We are
not claiming any endorsement by Sandia, and our cover page, our reports and the
executable's file properties all state that the method and the questionnaires
are Sandia's, citing SAND No. 2010-6487. Even so, we would rather ask than
assume:

- Is Sandia comfortable with our using "BioRAM" in the name of the Spanish
  version, and with the word appearing in our icon?
- If you would prefer a different name, we will change it. It is a small change
  for us now and a large one later, which is why we ask before distributing.

**3. The export-control notice.** The Biosecurity cover page carries a notice
that exporting the program may require a license from the U.S. Government. We
are a Mexican state public health laboratory, so we are the foreign party in
that sentence. We note that Sandia itself published the tool openly and
translated it into eleven languages for laboratories in other countries, which
seems hard to reconcile with an operative export restriction — but the notice is
there, we have not removed it, and we would rather hear from you than draw our
own conclusion. Does it affect our use, our translation, or our redistribution
of the Spanish version?

**4. The three defects.** Our earlier message reported three findings in the
model files — a missing scoring reference in the Spanish Biosafety model, a
duplicate `QuestionSetRoot` UUID in `Biosecurity.raml` that makes the 46
Facility answers unreachable, and a divergence between the Spanish files and the
2014 English revision. They are engineering rather than licensing, so please
pass them to the author when you reach him. We are glad to contribute the
corrections back in whatever form suits Sandia: a pull request, corrected files,
or just our verification notes.

While preparing this reply we noticed one more small thing, which is yours
rather than ours: `historico/sandia/Java source.zip` contains two NetBeans `private.properties`
files under `gov/sandia/bioram/` that carry an internal path from a developer's
machine (`C:\Users\cehines`). We have not altered your archive and do not intend
to — we mention it only in case you would rather it not be in a public
repository.

**One thing we want to be transparent about.** Our own additions — the
interface, the storage, the reports — we are releasing under the GNU GPL v3,
which is compatible with BSD-3 and keeps your notices intact. If Sandia would
rather we use a different license for our own work, tell us and we will discuss
it.

Thank you again. BioRAM is doing real work in a public health laboratory in
western Mexico, and the fact that Sandia published it is the reason that is
possible.

With appreciation,

[nombre]
[cargo]
Laboratorio Estatal de Salud Pública de Nayarit
Comisión Estatal para la Protección contra Riesgos Sanitarios de Nayarit
Servicios de Salud de Nayarit · Tepic, Nayarit, México
[correo] · [teléfono]

---

## Traducción al español (para revisar antes de enviar)

**Asunto:** Re: Seeking use of SCR1186.1 BioRAM v. 4.0 (Open Source)

Estimado Sr. Sleeper:

Gracias: es justo la claridad que necesitábamos, y agradecemos la rapidez.

Su suposición es correcta en los dos puntos. Trabajamos con **SCR1186.1 BioRAM
v. 4.0, la de código abierto**, y no con la versión propietaria. Para que quede
constancia, todo lo que usamos salió del repositorio público de Sandia,
`github.com/sandialabs/BioRAM`: el `bioram-4.0.5.jar`, los archivos de modelo
`Biosafety.raml` y `Biosecurity.raml`, y `historico/sandia/Java source.zip`, que `sacaske` subió
a ese repositorio el 6 de febrero de 2018. Mencionamos los archivos concretos
para que la licencia que atribuyan caiga sobre el artefacto correcto.

Lo que hicimos con ello, en corto: una versión completa en español de México
para Windows, y un programa nuevo en Python que reutiliza sus cuestionarios y
reproduce su motor de cálculo. No rehicimos el método: el método, los
cuestionarios y los pesos son de ustedes. Nuestra implementación reproduce su
motor en Java con **cero diferencia en 7 600 valores comparados**, y diez de los
pesos publicados en el Apéndice B de su guía se reproducen exactamente.

Seguiremos adelante como nos indica, y mientras tanto conservamos su correo como
el permiso. Cuatro cosas nos ayudarían a cerrarlo bien.

**1. Cuando quede atribuida la BSD-3, ¿nos avisan, y con qué año?** La línea de
derecho de autor de su mensaje trae el año como «tbd». Queremos llevar su aviso
al pie de la letra, así que el año exacto nos importa. Incluiremos el texto
completo de la BSD-3 junto a nuestra propia licencia en cuanto exista.

**2. Una pregunta sobre el nombre, y por eso se la hacemos a usted.** La tercera
cláusula de la BSD-3 reserva el uso del nombre del titular para respaldar o
promocionar productos derivados. Nuestro programa se llama **«BioRAM LESP»** y
el icono que hizo el laboratorio lleva escrita la palabra **«BioRam»**. No
pretendemos ningún respaldo de Sandia, y nuestra portada, nuestros reportes y
las propiedades del ejecutable dicen todos que el método y los cuestionarios son
de Sandia, citando el SAND No. 2010-6487. Aun así, preferimos preguntar:

- ¿A Sandia le parece bien que usemos «BioRAM» en el nombre de la versión en
  español, y que la palabra aparezca en nuestro icono?
- Si prefieren otro nombre, lo cambiamos. Hoy es un cambio chico y después sería
  grande, y por eso preguntamos antes de distribuir.

**3. El control de exportaciones.** La portada de bioprotección trae la
advertencia de que exportar el programa puede requerir licencia del Gobierno de
los Estados Unidos. Somos un laboratorio estatal de salud pública de México, así
que somos la parte extranjera de esa frase. Notamos que Sandia misma publicó la
herramienta abiertamente y la tradujo a once idiomas para laboratorios de otros
países, lo que parece difícil de conciliar con una restricción de exportación
operante; pero la advertencia está ahí, no la hemos quitado, y preferimos
oírlo de ustedes que sacar nuestra propia conclusión. ¿Afecta a nuestro uso, a
la traducción o a la redistribución de la versión en español?

**4. Los tres defectos.** En nuestro mensaje anterior reportamos tres hallazgos
en los archivos del modelo: una referencia de puntuación faltante en el modelo
de bioseguridad en español, un UUID de `QuestionSetRoot` duplicado en
`Biosecurity.raml` que deja inalcanzables las 46 respuestas de instalaciones, y
una divergencia entre los archivos en español y la revisión inglesa de 2014. Son
de ingeniería y no de licencias, así que le pedimos que se los pase al autor
cuando lo contacte. Con gusto aportamos las correcciones de vuelta en la forma
que a Sandia le acomode: un pull request, los archivos corregidos, o
simplemente nuestras notas de verificación.

Al preparar esta respuesta notamos una cosa más, que es de ustedes y no
nuestra: `historico/sandia/Java source.zip` trae dos archivos `private.properties` de NetBeans
bajo `gov/sandia/bioram/` con una ruta interna de la computadora de un
desarrollador (`C:\Users\cehines`). No hemos modificado su archivo ni
pensamos hacerlo; lo mencionamos sólo por si prefieren que no esté en un
repositorio público.

**Algo que queremos transparentar.** Lo que agregamos nosotros —la interfaz, el
almacenamiento, los reportes— lo liberamos bajo la GNU GPL v3, que es compatible
con la BSD-3 y mantiene sus avisos intactos. Si Sandia prefiere que usemos otra
licencia para nuestro propio trabajo, dígannoslo y lo platicamos.

Gracias de nuevo. BioRAM está haciendo trabajo real en un laboratorio de salud
pública del occidente de México, y que Sandia lo haya publicado es la razón de
que eso sea posible.

Con aprecio,

[nombre]
[cargo]
Laboratorio Estatal de Salud Pública de Nayarit
Comisión Estatal para la Protección contra Riesgos Sanitarios de Nayarit
Servicios de Salud de Nayarit · Tepic, Nayarit, México
[correo] · [teléfono]

---

## Antes de enviarla

- [ ] Llenar nombre, cargo, correo y teléfono al pie, igual que en la primera.
- [ ] Contestar **respondiendo al correo de Sleeper**, no en uno nuevo, para que
      el hilo y su asunto se conserven.
- [ ] Decidir si se pone en copia a `sacaske@sandia.gov`. Conviene: es el autor,
      es quien tiene que atribuir la licencia y es a quien le tocan los tres
      defectos.
- [ ] Guardar el correo de Sleeper en el expediente del laboratorio. Hasta que
      la licencia esté atribuida, **ese correo es el permiso**.

## Lo que NO conviene hacer todavía

- **No poner el texto de la BSD-3 en el repositorio aún.** La licencia no está
  atribuida y el año no está decidido. Ponerla ahora sería afirmar algo que no
  es cierto todavía. Se agrega el día que Sandia la publique.
- **No usar el icono con la palabra «BioRam» en material que salga del
  laboratorio** hasta que conteste el punto 2. De uso interno no hay problema.
