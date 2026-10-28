# Aviso de procedencia, derechos y licencias

Este archivo dice de quién es cada cosa que hay en este repositorio y bajo qué
condiciones se puede usar. Se escribió porque el repositorio no lo decía en
ninguna parte: el único aviso de derecho de autor de BioRAM estaba escondido en
la portada de uno de los dos cuestionarios.

**No es una opinión legal.** Es un inventario de lo que se verificó archivo por
archivo, más lo que conviene decidir. Donde hay interpretación, se dice que es
interpretación.

---

## 1. De quién es BioRAM

BioRAM (Biosafety and Biosecurity Laboratory Risk Assessment Model) es de
**Sandia National Laboratories**. El aviso que viaja dentro del cuestionario de
bioprotección dice, literalmente:

> Derecho de autor 2007/2009 Sandia Corporation. Conforme los términos del
> contrato DE-AC04-94AL85000, se emitió una licencia sin exclusividad con
> respecto al uso de este trabajo a favor del Gobierno de los EE. UU. La
> exportación de este programa tal vez requiera una licencia del Gobierno de los
> Estados Unidos.

Y el de bioseguridad:

> SAND No: 2010-6487. Sandia es un laboratorio multiprograma operado por Sandia
> Corporation, una empresa de Lockheed Martin Company, para el Departamento de
> Administración de la Seguridad Nuclear de los Estados Unidos conforme al
> contrato DE-AC04-94AL85000.

Ese texto **no se debe quitar ni reescribir** en ningún archivo. Es el único
enunciado de derechos que tiene la herramienta.

Dos cosas que conviene no confundir al leerlo:

1. La licencia sin exclusividad que menciona se otorgó **al Gobierno de los
   Estados Unidos**, no al público ni a este laboratorio. Es la fórmula estándar
   de contratista del Departamento de Energía. Por sí sola no concede nada a
   terceros.
2. Hay una **advertencia de control de exportaciones**: exportar el programa
   puede requerir licencia del Gobierno de los EE. UU.

### Qué se verificó sobre la licencia

Lo que consta **a favor** del uso y la redistribución:

- La **guía de usuario oficial de Sandia** (`BioRAM UserGuide SAND.pdf`, agosto de
  2021, 80 páginas) lo dice de forma expresa:

  > *"The BioRAM software tool was developed as **open source software** per the
  > requirements from the tool's funding agencies. The tool, provided directly
  > from Sandia National Laboratories or downloaded from the software repository
  > (https://github.com/sandialabs/BioRAM) contains the values and assumptions
  > provided in this manual."*

  Es decir: no es una deducción nuestra, es Sandia diciendo que la herramienta se
  desarrolló como software de código abierto porque así lo exigieron quienes la
  financiaron (el programa de Agentes Selectos de los CDC, el Programa de
  Colaboración en Bioprotección del Departamento de Estado y Sandia misma).
- El repositorio oficial es `github.com/sandialabs/BioRAM`, en la cuenta
  institucional de Sandia. Este repositorio es una copia de aquel: el historial
  arranca con los 14 commits de `sacaske`, la misma persona cuyo correo aparece
  en la portada del cuestionario.
- La guía cita el registro: *"BioRAM falls under copyright 1186.1 Biosecurity
  Risk Assessment Methodology (BioRAM) v. 4.0, 2019."*
- El README original invita a usarla: *"You can use either the excel version or
  the Java versions"*, *"Source code is availble in the .zip file"*.
- Sandia distribuyó **traducciones oficiales a once idiomas**, español entre
  ellas, dentro de un programa llamado *International Biological Threat
  Reduction*, cuyo propósito es que laboratorios de otros países la usen.

Lo que **falta**, y es un detalle de forma, no de fondo:

- **No viaja ningún archivo `LICENSE`, `NOTICE`, `AUTHORS` ni `COPYING`** propio
  de BioRAM: ni dentro del `.jar`, ni en el repositorio (verificado con
  `git ls-files` y en todo el historial), ni como bloque `<licenses>` en el
  `pom.xml`. Sandia dice en la guía que es código abierto, pero **no declaró en
  los archivos cuál licencia** (MIT, BSD, Apache…). Eso deja sin precisar qué
  obligaciones tiene quien redistribuye: a qué atribución obliga, si hay que
  conservar avisos, etc.

  Esto **lo confirmó la propia Sandia** el 28 de octubre de 2026, y además
  explicó por qué: el producto se creó *«en una época en la que Sandia no tenía
  buen control de su oferta de código abierto»*. Ver más abajo.

### Lo que este laboratorio hace y el riesgo de cada cosa

| Acción | Respaldo |
|---|---|
| **Usarla** internamente | Respaldo expreso: la guía la declara código abierto y Sandia la publica para este propósito |
| **Traducirla y rearmarla** | Lo mismo, y además Sandia ya publicó traducciones oficiales a once idiomas. El `.jar` traducido y el programa en Python son **obra derivada**, y hay que conservar los avisos de Sandia (lo hacemos) |
| **Redistribuirla públicamente** | Coherente con «código abierto», y desde el 28/10/2026 con permiso expreso por correo de la persona que lleva las licencias en Sandia, que se compromete a atribuir una BSD-3. **Pero la licencia todavía no está puesta**, y sigue vigente la advertencia de exportación de la portada |

### La respuesta de Sandia, 28 de octubre de 2026

Se escribió a Sandia y **contestaron**. Responde **Robert Sleeper JD, Licensing
Executive de Sandia National Laboratories** (`rdsleep@sandia.gov`). Lo que dice,
en sus palabras:

> *"It appears that the above was created at a time when Sandia didn't have
> great control of our OS offerings and this particular product has **no attached
> OPEN SOURCE license**. We will move to attach one asap so we can give you the
> proper permissions. Probably BDS3. **I think you can go forward based on
> that** and I will reach out to the author and update it asap for BDS3 which
> will allow you to **use, modify, and distribute** software for any
> purpose—including commercial applications—as long as you follow a few basic
> rules."*

Con el enlace a <https://opensource.org/license/bsd-3-clause> y el texto del
aviso que llevará, encabezado por:

> *Copyright (c) &lt;YEAR tbd&gt; NATIONAL TECHNOLOGY AND ENGINEERING SOLUTIONS
> OF SANDIA, LLC.*

«BDS3» está escrito así dos veces, pero el enlace que da es el de la licencia
**BSD de 3 cláusulas**: es un desliz de tecleo, no otra licencia.

**Es exactamente nuestro archivo, no otro producto.** Sleeper encabeza su correo
con *«SCR1186.1 Biosecurity Risk Assessment Methodology (BioRAM) v. 4.0 (Open
Source)»*, y el número de registro coincide con el que cita la guía oficial:
*«BioRAM falls under copyright 1186.1 Biosecurity Risk Assessment Methodology
(BioRAM) v. 4.0, 2019»*. Además advierte que existe **una versión propietaria
aparte**, y supone que no es la que nos interesa. No lo es, y se puede demostrar:
todo lo que este laboratorio usó —el `.jar`, los cuestionarios y `Java
source.zip`— lo subió `sacaske` al repositorio público `sandialabs/BioRAM`, el 6
de febrero de 2018, en el segundo commit de ese repositorio. Este repositorio
arranca con esos mismos commits.

**Qué queda resuelto y qué no.** Conviene no confundirlo:

| | |
|---|---|
| Resuelto | La herramienta **sí** es la de código abierto, y Sandia lo confirma por escrito |
| Resuelto | Sandia **se compromete** a atribuirle una licencia, probablemente BSD-3 |
| Resuelto | Hay permiso expreso, de la persona que lleva las licencias, para **seguir adelante** mientras tanto |
| **Sin resolver** | **Hoy sigue sin haber ninguna licencia atribuida.** El permiso es un correo, no una licencia |
| **Sin resolver** | El año del aviso de derecho de autor está «tbd», y la licencia es «probably» BSD-3 |
| **Sin resolver** | No contestó sobre la **advertencia de control de exportaciones** de la portada |
| **Sin resolver** | No contestó los **tres defectos** que se le reportaron. Es natural: lleva licencias, no ingeniería, y dice que hablará con el autor |

**Qué implica si queda en BSD-3.** La BSD de 3 cláusulas es permisiva y
**compatible con la GPL v3** que este laboratorio eligió para su propio código:
se puede combinar sin conflicto. A cambio obliga a dos cosas, y las dos nos
tocan:

1. **Conservar el aviso de derecho de autor, la lista de condiciones y el
   descargo de garantía**, tanto en el código como en lo que se distribuya en
   binario. Los avisos de Sandia ya se conservan; faltará agregar el texto
   completo de la BSD-3 en cuanto exista, con su año.
2. **La cláusula de no-respaldo**: no se pueden usar los nombres del titular ni
   de los colaboradores para respaldar o promocionar productos derivados sin
   permiso previo por escrito. Esto cae justo sobre la pregunta del nombre
   «BioRam» en el icono del programa, que quedó planteada más abajo. Ahora hay
   motivo concreto para preguntárselo a Sleeper, que es además la persona
   indicada.

**Mientras tanto** se puede seguir usando y trabajando con normalidad, con más
respaldo que antes. Guarde el correo de Sleeper: hasta que la licencia esté
atribuida, ese correo **es** el permiso, y conviene que esté en el expediente.

**Lo que conviene hacer, en orden de utilidad:**

1. **Contestarle a Sleeper** (borrador listo en
   [`RESPUESTA-A-SANDIA.md`](RESPUESTA-A-SANDIA.md)): agradecer, decirle con
   precisión qué artefacto se usó para que la licencia se atribuya al correcto,
   preguntarle por el nombre y el icono, y pedir que avise cuando la BSD-3 esté
   puesta y con qué año.
2. **Dejar constancia** de la advertencia de exportación. México es extranjero
   para efectos de ese aviso. En la práctica se trata de una herramienta de
   evaluación de riesgos publicada abiertamente por Sandia en GitHub y traducida
   por Sandia misma a once idiomas para laboratorios de otros países, lo que es
   difícil de conciliar con un control de exportación efectivo; pero el aviso
   está ahí y lo prudente es no borrarlo ni ignorarlo.

### Una advertencia de Sandia que sí nos aplica directamente

La misma guía dice, en la misma página:

> *"Any versions that have been modified by users may not reflect the same
> results."*

Esa frase apunta exactamente a lo que hizo este laboratorio: modificar la
herramienta. Por eso importa lo que está verificado y documentado en el
[`README.md`](README.md): los 1,180 valores de referencia tomados del motor
original se reproducen con cero diferencias a diez decimales, y los archivos que
exporta el programa nuevo se abren en el programa original y dan los mismos
puntajes. Es la respuesta concreta a esa advertencia, y conviene poder mostrarla
en una auditoría.

---

## 2. Librerías de terceros que van dentro del `.jar`

El programa Java empaqueta librerías ajenas. Se contaron las clases de cada una:

| Paquete | Clases | Qué es | Licencia | ¿Se usa? |
|---|---:|---|---|---|
| `org/bouncycastle` | 1436 | Criptografía y correo cifrado S/MIME | MIT-like (BouncyCastle) | **No**. Ningún código lo llama |
| `org/apache` | 1082 | Velocity (plantilla del informe) y commons-compress | Apache 2.0 | Sí |
| `org/jfree` | 965 | JFreeChart y JCommon (las gráficas) | **LGPL** | Sí |
| `com/sun`, `javax/xml`, `org/w3c`, `org/xml`, `org/jvnet` | 1479 | JAXB y xml-commons | Apache 2.0 / CDDL, con partes de IBM, Sun y W3C | Sí |
| `com/lowagie` | 471 | iText (generar PDF) | MPL 1.1 / LGPL | **No**. Nadie lo referencia |
| `javax/activation` | 31 | Tipos MIME | CDDL | De arrastre |
| `com/keypoint` | 1 | PngEncoder | — | De arrastre |
| `gov/sandia` | 229 | **BioRAM** | Ver sección 1 | Sí |

Textos de licencia que **sí** viajan dentro del `.jar` y que **no hay que
quitar** (su licencia obliga a conservarlos al redistribuir):

- `META-INF/LICENSE.txt`, `META-INF/NOTICE.txt`, `META-INF/LICENSE`,
  `META-INF/NOTICE` — Apache 2.0
- `license/LICENSE`, `license/NOTICE`, `license/LICENSE.dom-*.txt`,
  `license/LICENSE.sax.txt` — xml-commons
- `com/lowagie/text/MPL-1.1.txt`, `lgpl.txt`, `apache_license.txt`,
  `misc_licenses.txt` — iText

**Hueco heredado:** falta el texto de la licencia **LGPL de JFreeChart y
JCommon**, que sí van incluidos como código. Ese hueco ya venía del paquete
original de Sandia, no lo introdujo la traducción; pero el obligado a subsanarlo
es quien redistribuye. Es de arreglo trivial si se va a redistribuir.

Dato de tamaño, por si alguien se pregunta por qué el `.jar` pesa tanto: iText y
BouncyCastle juntos son unos 11 MB de los 21 MB sin comprimir, y **ninguno de los
dos se usa**. BioRAM en sí son 1.2 MB.

---

### Lo que va dentro del ejecutable de Windows

El programa en Python se distribuye como un solo `.exe` que lleva dentro a Qt,
a través de PySide6. Qt y PySide6 son de The Qt Company y se usan bajo la
**LGPL versión 3**, que es lo que permite distribuirlos junto a un programa
propio. Se incluye además `programa/bioram/media/qtbase_es.qm`, la traducción
al español de los textos que Qt pone por su cuenta —los botones «Cerrar»,
«Cancelar», «Sí», «No» y los menús de los campos de texto—. Es parte de Qt y
viaja bajo la misma licencia; está en el repositorio porque la distribución de
PySide6 para Windows no la trae, aunque la de Linux sí.

## 3. Qué es obra propia de este laboratorio

Lo siguiente lo hizo el Laboratorio Estatal de Salud Pública de Nayarit y no
viene de Sandia:

- `programa/` — el programa nuevo en Python: la interfaz, el almacenamiento en
  SQLite, el modelo de áreas → cepas → evaluaciones, los reportes y las pruebas.
  **Pero** lleva dentro los cuestionarios de Sandia (ver la advertencia abajo).
- `traduccion/` — las herramientas de traducción y verificación, el punto de
  arranque en español (`MainEs.java`) y el empaquetado.
- `BioRAM-es/` — los lanzadores, el `LEEME.txt` y el `.jar` rearmado.
- `LEEME.md`, este `AVISO.md` y la parte en español del `README.md`.
- La imagen institucional: el logotipo del laboratorio en la portada de los
  cuestionarios y de los reportes, la paleta de colores, y el icono del programa
  (`programa/bioram/media/bioram.ico`), que el laboratorio aportó.

### Una cosa que conviene pensar antes de publicar: el nombre en el icono

El icono del programa lleva escrita la palabra **BioRam**. Eso merece una
decisión consciente, no un descuido, por dos razones:

1. «BioRAM» es el nombre con el que Sandia National Laboratories distribuye su
   herramienta. La licencia GPL cubre el **código**; los nombres y las marcas
   no se licencian con él. Un programa distinto que se presenta con el mismo
   nombre y con logotipo propio puede dar a entender que lo publica Sandia, o
   que Sandia lo avala, y ninguna de las dos cosas es cierta.
2. Es justo lo que se le está preguntando a Sandia en `CARTA-A-SANDIA.md`. Lo
   prudente es esperar su respuesta antes de usar el nombre en material que
   salga del laboratorio.

Mientras tanto no hay problema de uso interno: el programa se llama **BioRAM
LESP**, dice en su portada, en sus reportes y en las propiedades del ejecutable
de quién es el método y bajo qué número SAND, y no se presenta como producto de
Sandia. Si Sandia pidiera otro nombre, cambiarlo es cosa de un rato: está en un
solo sitio en cada archivo.

### Advertencia importante sobre el programa en Python

**El programa en Python no es un sustituto independiente de BioRAM.** Lleva
dentro, en `programa/bioram/cuestionarios/`, los cuestionarios completos de
Sandia: las 105 preguntas de cada evaluación, sus pesos, sus criterios de
puntuación, los perfiles de resultados y las portadas, que muestra tal cual. Es
**obra derivada** exactamente igual que el `.jar` traducido. Que esté reescrito
en otro lenguaje no lo libera de los derechos de Sandia.

Lo que sí es nuevo y propio es el programa alrededor: cómo se guardan los datos,
cómo se capturan las respuestas, los reportes y la organización por áreas y
cepas.

### Licencia del código propio: GPL versión 3

El laboratorio decidió liberar su código bajo la **Licencia Pública General de
GNU, versión 3 o posterior**, conservando el crédito al autor del método
original.

- El texto completo de la licencia está en [`LICENSE`](LICENSE).
- El titular del código nuevo es el **Laboratorio Estatal de Salud Pública de
  Nayarit**.
- Cada archivo de código lleva el aviso correspondiente, y
  `programa/bioram/__init__.py` reúne los créditos completos.

Lo que esa licencia cubre y lo que no, dicho sin rodeos:

| | |
|---|---|
| **Sí cubre** | El código escrito por el laboratorio: la interfaz, el almacenamiento en SQLite, el modelo de áreas → cepas → evaluaciones, los reportes, el motor reimplementado en Python, las herramientas de traducción y los lanzadores. |
| **No cubre** | Los cuestionarios de Sandia que el programa lleva dentro (`programa/bioram/cuestionarios/`): las 105 preguntas de cada evaluación, sus pesos, sus criterios, los perfiles de resultados y las portadas. Eso sigue siendo de Sandia, con los avisos de la sección 1. |

La GPL v3 obliga a quien redistribuya el programa, o una versión modificada de
él, a entregar también el código fuente bajo la misma licencia y a conservar los
avisos de derechos. Es lo que el laboratorio pide a cambio del trabajo que
regala.

---

## 4. Sobre la versión de los cuestionarios en español

Un dato que conviene tener anotado para cualquier auditoría futura.

Las portadas declaran la misma versión en los dos idiomas:

- bioseguridad: *"RAM de Bioseguridad, Versión 1.0, Septiembre de 2010"*,
  SAND No. 2010-6487
- bioprotección: *"Modelo de riesgos relacionados con la bioprotección 2010
  (BioRAM 2.0) Prototipo"*

Sin embargo, al comparar los archivos:

- En **bioprotección**, el archivo español y el inglés son el mismo modelo: los
  105 identificadores de pregunta coinciden, en el mismo orden, con los mismos
  pesos, los mismos límites y los mismos perfiles de resultados.
- En **bioseguridad**, no: ninguno de los 105 identificadores coincide, la
  organización interna es distinta y los perfiles de resultados del español
  tienen más nodos (182 categorías y 284 referencias a preguntas, contra 155 y
  276 del inglés). **Esa diferencia viene del archivo oficial de Sandia en
  español**, no de la traducción hecha aquí: se verificó que el archivo oficial,
  el corregido por el laboratorio y el que se entrega tienen exactamente los
  mismos conteos.

Es decir: el español de bioseguridad es una **revisión distinta del mismo modelo
nominal**, publicada por Sandia con el mismo número de versión. Conviene saberlo
porque significa que los resultados de la versión en español no tienen que
coincidir número por número con los de la versión en inglés.

---

## 5. Datos de personas que viajan en los archivos

Se revisó qué datos personales y de origen contienen los archivos. Resumen:

**Lo que se conserva, porque es atribución legítima:**

- `@author danbowe` y `@author Greg Briggs` en los comentarios del código fuente:
  es el crédito de quien escribió el programa y de un fragmento de terceros. Los
  comentarios no se compilan, así que no viajan en el `.jar`.
- `sacaske@sandia.gov` y `SAND No. 2010-6487` en la portada: el número SAND es lo
  que permite rastrear y citar la metodología.
- El historial de los 14 commits de `sacaske`: es la cadena de procedencia y
  sostiene el argumento de que el código viene del repositorio que Sandia publicó.

**Lo que conviene corregir** (ninguno de estos datos se ve en pantalla, pero
viaja en los archivos que el laboratorio distribuye):

- Rutas de la computadora de los desarrolladores de Sandia:
  `C:/Users/danbowe/Documents/testModel.raml` (en 8 archivos `.java`, compilado en
  9 `.class` de los dos `.jar`), `C:/Users/danbowe/Desktop/im.gif` y
  `C:/Users/danbowe/Desktop/`. Están dentro de métodos `main()` de clases de
  prueba que nunca se ejecutan, así que quitarlas no cambia nada.
- `C:\Users\cehines\AppData\Roaming\NetBeans\8.0.2\build.properties` y
  `file:/Y:/Analytical/BioRAM 4.0/...` en `nbproject/private/`: archivos privados
  del entorno de desarrollo que nunca debieron publicarse. El propio `.gitignore`
  del proyecto ya los excluye, pero el `.zip` del código fuente los lleva.
- `\\snl\Collaborative\IBTR\Analytical\BioRAM 4.0\...` en
  `build/built-jar.properties`: revela la topología de la red interna de Sandia
  (servidor, recurso compartido, programa). **Es el primero que conviene quitar.**
- Manifiesto del `.jar` en español: `Built-By: danbowe`,
  `Build-Jdk: 1.7.0_07`, `Created-By: Apache Maven 3.0.5`. En el `.jar` original
  es cierto y hay que dejarlo; en el rearmado por este laboratorio ya es falso.

**Contacto de soporte.** La portada de bioseguridad dirige las preguntas a
`sacaske@sandia.gov`. Quien trabaje en Nayarit y escriba ahí pidiendo soporte
probablemente no obtenga ayuda útil. Conviene poner el contacto del laboratorio y
dejar el crédito a Sandia en una línea aparte. No se debe borrar sin poner un
contacto propio, porque entonces el usuario se queda sin a quién preguntar.

---

## 6. Red, envío de información e informes

Se auditó específicamente si los programas acceden a Internet, envían informes o
mandan información a algún lado. **No lo hacen.** Lo verificado:

- **Programa en Python:** cero código de red. No importa `socket`, `urllib`,
  `http`, `requests`, `smtplib`, `QtNetwork` ni `QDesktopServices`, y no llama a
  `openUrl`, `subprocess`, `eval` ni `exec`. La lista completa de lo que importa
  son módulos estándar de Python y `PySide6.QtCore/QtGui/QtWidgets`.
- **Programa Java:** se ejecutaron los dos `.jar` (el original y el traducido)
  generando un informe completo, con las llamadas de red vigiladas. Resultado:
  **cero conexiones a cualquier dirección IP**. Los únicos sockets que aparecen
  son el sondeo de IPv6 que hace la máquina virtual de Java al arrancar, idéntico
  al de un programa de tres líneas que no hace nada de red. Con un vigilante de
  seguridad instalado, el único permiso de red solicitado en todo el recorrido fue
  `SocketPermission "vm" "resolve"`, y proviene del subsistema de tipografías de
  Java, que nombra su archivo de caché con el nombre del equipo. No sale del
  equipo.
- En las 229 clases compiladas de BioRAM: cero referencias a `Socket`,
  `ServerSocket`, `InetAddress`, `HttpURLConnection`, `openConnection`,
  `openStream`, `javax.mail`, `Runtime.exec` o `ProcessBuilder`. Todos los usos de
  `java.net.URL` son `getResource` para leer archivos de dentro del propio `.jar`.
- El botón "Crear informe" del Java abre el navegador, pero con una dirección
  `file://` a un archivo del propio disco. El informe generado solo referencia
  imágenes de su misma carpeta; el único `http://` que contiene es la declaración
  de espacio de nombres `http://www.w3.org/1999/xhtml`, que los navegadores no
  descargan.
- Velocity, la librería que arma el informe, se configura a propósito para leer
  plantillas **solo de dentro del programa**
  (`resource.loader=class`), aunque la librería sea capaz de descargarlas por
  http.
- Las portadas de los cuatro cuestionarios no contienen ninguna URL ni ninguna
  imagen remota.
- Los cuatro `.exe` no importan ninguna biblioteca de red de Windows.

**Lo único que conviene saber:** el programa Java deja los informes que genera en
la carpeta temporal del sistema (`%TEMP%` en Windows) y **nunca los borra**. Cada
informe deja ahí una copia completa, con los datos de la evaluación. No se envía a
ningún lado, pero en una computadora compartida conviene vaciar `%TEMP%` de vez en
cuando. El programa en Python no tiene este problema: guarda donde el usuario
indica.

---

## 7. Lo que falta por decidir o corregir

Al 28 de octubre de 2026.

| Pendiente | Estado | Quién decide |
|---|---|---|
| Que Sandia atribuya la licencia BSD-3 al producto, con su año | **En curso en Sandia.** Sleeper se comprometió a hacerlo «asap». Mientras tanto, su correo es el permiso | Sandia |
| Contestarle a Sleeper: qué artefacto usamos, el nombre «BioRam» del icono, y el control de exportaciones | Borrador listo en `RESPUESTA-A-SANDIA.md` | Laboratorio |
| Agregar el texto completo de la BSD-3 con su año, junto al `LICENSE` de la GPL v3 | Cuando Sandia la publique | Técnico |
| Usar o no el nombre «BioRam» en el icono fuera del laboratorio | A la espera de la respuesta sobre la cláusula de no-respaldo | Laboratorio |
| Los tres defectos reportados a Sandia (referencia faltante, UUID de módulo duplicado, divergencia con la revisión de 2014) | Reportados; Sleeper dice que hablará con el autor | Sandia |
| Traducir la encuesta de 2022 (BioRisk) | Decidido para después | Laboratorio |
| Quitar las rutas internas de Sandia del código fuente publicado | Pendiente | Técnico, trivial |
| Corregir `Built-By` en el `.jar` en español | Pendiente | Técnico, trivial |
| Agregar el texto LGPL de JFreeChart si se va a redistribuir el `.jar` | Pendiente | Técnico, trivial |
| Firma de código para el `.exe`, que quitaría el aviso de SmartScreen | Requiere comprar un certificado | Laboratorio |

### Ya resuelto

| | Cuándo |
|---|---|
| Preguntarle a Sandia bajo qué licencia se libera BioRAM | Contestado el 28/10/2026: ninguna atribuida todavía; será BSD-3 |
| Elegir licencia para el código propio en Python | GPL v3, y es compatible con la BSD-3 que viene |
| Cambiar el contacto de soporte de la portada por uno del laboratorio | Hecho |
| Datos de versión en el `.exe` | Hechos: empresa, producto, versión y copyright |
| Declarar al laboratorio como autor en los commits | Hecho |
