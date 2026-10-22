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

### Lo que este laboratorio hace y el riesgo de cada cosa

| Acción | Respaldo |
|---|---|
| **Usarla** internamente | Respaldo expreso: la guía la declara código abierto y Sandia la publica para este propósito |
| **Traducirla y rearmarla** | Lo mismo, y además Sandia ya publicó traducciones oficiales a once idiomas. El `.jar` traducido y el programa en Python son **obra derivada**, y hay que conservar los avisos de Sandia (lo hacemos) |
| **Redistribuirla públicamente** | Coherente con «código abierto», pero **sin licencia escrita no se sabe con qué condiciones**. Y sigue vigente la advertencia de exportación de la portada |

**Lo que conviene hacer, en orden de utilidad:**

1. **Escribir a Sandia** (`sacaske@sandia.gov`, el contacto que la propia
   herramienta publica) para pedir dos cosas concretas: que confirmen por escrito
   bajo qué licencia se libera BioRAM, y que confirmen que la traducción al
   español y su redistribución están permitidas. Es un correo corto y resuelve el
   único punto abierto.
2. **Mientras llega la respuesta**, se puede seguir usando y trabajando con
   normalidad. La redistribución pública ya está respaldada por la declaración de
   código abierto de la guía; lo que no está es precisado. Conservar todos los
   avisos de Sandia, como se hace hoy, es lo que corresponde en cualquier caso.
3. **Dejar constancia** de la advertencia de exportación. México es extranjero
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

### Licencia del código propio

**Pendiente de decidir por el laboratorio.** Hoy el programa en Python no declara
titular ni licencia en ninguna parte. Conviene declarar al laboratorio como
titular del código nuevo y elegir una licencia para esa parte (por ejemplo MIT o
GPL), dejando escrito que esa licencia cubre **solo el código nuevo** y no los
cuestionarios de Sandia que lleva dentro.

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

| Pendiente | Quién decide |
|---|---|
| Escribir a Sandia para que confirmen por escrito bajo qué licencia se libera BioRAM y que la traducción y su redistribución están permitidas | Laboratorio |
| Elegir licencia para el código propio en Python | Laboratorio |
| Cambiar el contacto de soporte de la portada por uno del laboratorio | Laboratorio |
| Quitar las rutas internas de Sandia del código fuente publicado | Técnico, trivial |
| Corregir `Built-By` en el `.jar` en español | Técnico, trivial |
| Agregar el texto LGPL de JFreeChart si se va a redistribuir | Técnico, trivial |
| Poner datos de versión en los `.exe` (hoy están vacíos: sin empresa, producto, versión ni copyright, lo que además contribuye al aviso de SmartScreen) | Técnico, al empaquetar |
| Declarar al laboratorio como autor en los commits en lugar de la herramienta | Laboratorio |
