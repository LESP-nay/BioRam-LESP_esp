# Plan para la beta 2

Al 28 de octubre de 2026. **Esto es un plan, no trabajo hecho.** Nada de lo que
aquí se describe se ha tocado todavía: se espera a tres cosas, y ninguna depende
de nosotros.

| Se espera | De quién | Para qué |
|---|---|---|
| Los fallos y las mejoras de la primera beta | Del laboratorio | Son lo único que dice si el programa sirve para trabajar |
| Que Sandia suba la licencia BSD-3 a GitHub | De Sandia | Hasta entonces no se puede escribir el aviso exacto |
| La respuesta sobre el nombre y el icono | De Sandia | Decide si hay que renombrar, y renombrar tarde cuesta más |

---

## 1. Cumplir al 100% con lo que Sandia pidió

Sandia dijo que la BSD-3 permite usar, modificar y distribuir *«as long as you
follow a few basic rules»*. Esas reglas son tres, y conviene tenerlas separadas
porque dos son mecánicas y la tercera es una decisión.

### 1.1 Conservar el aviso en el código  → mecánico

Cuando la licencia aparezca en `github.com/sandialabs/BioRAM`:

1. Copiarla **literal**, con el año que Sandia ponga, a un archivo propio:
   `LICENCIA-BioRAM-Sandia.txt`. No reescribirla ni resumirla.
2. Dejar el `LICENSE` actual como está: es la GPL v3 del código de este
   laboratorio, y son dos cosas distintas que no se mezclan.
3. Que `AVISO.md` diga, en una línea, cuál archivo cubre qué. Hoy ya lo explica,
   pero sin el texto de la licencia delante.

### 1.2 Conservar el aviso en lo que se distribuye en binario  → mecánico

La BSD-3 exige que el aviso, las condiciones y el descargo de garantía viajen
también *«in the documentation and/or other materials provided with the
distribution»*. En cristiano: el `.exe` no puede ir solo.

| Dónde | Qué falta |
|---|---|
| El `.zip` que baja del armado | Agregar `LICENCIA-BioRAM-Sandia.txt` a la lista que ya lleva `LEEME.md`, `AVISO.md`, `VERIFICACION.md` y `LICENSE` |
| **Ayuda ▸ Acerca de**, dentro del programa | Hoy muestra la portada con los avisos de Sandia. Falta el descargo de garantía completo de la BSD-3, que es parte de lo que obliga a conservar |
| Propiedades del `.exe` | Ya cita el SAND No. 2010-6487. No hace falta tocarlo |

Un detalle que importa: el descargo de garantía va **en mayúsculas y entero**.
Es el que dice que el programa se entrega «AS IS» y que el titular no responde
por daños. Resumirlo sería incumplir.

### 1.3 La cláusula de no-respaldo  → decisión, y es la única delicada

La tercera cláusula de la BSD-3 no prohíbe decir de dónde viene el programa:
**eso lo exige**. Prohíbe usar el nombre del titular para *respaldar o
promocionar* un producto derivado. Son dos cosas distintas y conviene no
confundirlas:

| | |
|---|---|
| **Se queda, pase lo que pase** | «El método y los cuestionarios son de BioRAM, de Sandia National Laboratories, SAND No. 2010-6487». Es atribución, y es obligatoria |
| **Está en duda** | Que *nuestro producto* se llame «BioRAM LESP», y que nuestro icono lleve escrita la palabra «BioRam» |

**Si Sandia dice que sí:** guardar su respuesta por escrito en `AVISO.md` y no
tocar nada. La cláusula pide «specific prior written permission», y eso sería.

**Si Sandia dice que no, o no contesta:** hay que renombrar. Está medido para
que no sea una sorpresa:

- **69 apariciones de «BioRAM LESP» en 42 archivos.** De ellas, **34 son la
  línea de encabezado** que llevan todos los archivos de código. Esas 34 se
  cambian de una pasada.
- Quedan unas 15 donde el nombre se ve de verdad: el título de la ventana, el
  menú «Acerca de», el pie de los reportes, el nombre interno del `.exe`, el
  nombre de la aplicación en la barra de tareas.
- **El icono** hay que rehacerlo sin la palabra. El dibujo del carnero no tiene
  problema: es obra del laboratorio.
- **Y una trampa que conviene ver antes de caer en ella:** cuando el programa no
  puede escribir junto al `.exe`, guarda el archivo de datos en
  `Documentos\BioRAM LESP\`. Si el nombre cambia, un laboratorio que ya venía
  usando la beta **dejaría de encontrar su trabajo**. El renombrado tiene que
  incluir que el programa siga mirando también en la carpeta vieja. Es poco
  código, pero si se olvida se pierde trabajo de verdad.

Un nombre alterno que no toca la marca de Sandia y describe lo mismo:
**«Evaluación de Riesgo Biológico — LESP Nayarit»**, de uso corto *ERB-LESP*. Se
propone para tenerlo listo, no para adoptarlo.

### 1.4 No dar a entender un respaldo que no existe  → revisión de una tarde

Repasar con ese ojo la portada, el pie de los reportes y el `README.md`. Hoy
dicen que el método es de Sandia, que es lo correcto. Lo que hay que verificar
es que en ningún lado se lea como que Sandia avala, revisó o acompaña **esta**
versión, porque no lo hizo.

---

## 2. Obligaciones de terceros, independientes de Sandia

Estas no esperan a nadie, pero sí dependen de una decisión del laboratorio.

### 2.1 JFreeChart y la LGPL — **la más seria de las pendientes**

El `.jar` en español que este laboratorio rearmó y redistribuye lleva dentro
**1 075 clases de JFreeChart**, que es LGPL. La LGPL obliga a incluir su texto y
a permitir que alguien sustituya esa biblioteca por otra versión. Hoy **no se
incluye ningún texto LGPL**: ni en `historico/java-es/`, ni en el `.jar`.

Esto se arregla de dos maneras, y la segunda es mejor:

1. Agregar el texto de la LGPL y una nota de cómo sustituir la biblioteca.
2. **Preguntarse si todavía hace falta redistribuir el `.jar`.** El programa en
   Python ya hace lo mismo, reproduce el cálculo sin diferencias y no lleva
   JFreeChart dentro. Si la versión en Java se deja de distribuir y queda sólo
   como referencia de verificación, esta obligación desaparece sola, junto con
   la siguiente.

Es una decisión del laboratorio, no mía, y conviene tomarla antes de publicar.

### 2.2 `Built-By: danbowe` en el `.jar` en español

El `.jar` que rearmamos dice que lo construyó `danbowe`, que es quien construyó
el de Sandia. O sea: **nuestra obra derivada va firmada con el nombre de una
persona de Sandia**. No es grave, pero es justo el tipo de cosa que la cláusula
de no-respaldo mira con malos ojos, y es falso además. Debe decir el
laboratorio. Desaparece si se deja de distribuir el `.jar`.

### 2.3 La ruta interna de Sandia — **no es nuestra, y no hay que tocarla**

Dentro de `historico/sandia/Java source.zip` hay dos archivos `private.properties` de NetBeans
con la ruta `C:\Users\cehines`, de una computadora de Sandia. Estaba anotado
como pendiente «técnico, trivial», y al revisarlo resulta que **no era nuestro**:
ese zip es de Sandia, tal como ellos lo subieron, y nuestro código Python no
tiene ninguna ruta así. Modificar el archivo de ellos sería peor que dejarlo.
Lo que corresponde es **avisarles**, junto con los tres defectos. Queda agregado
a la carta.

---

## 3. Lo técnico que queda

| Pendiente | Por qué no está hecho | Costo |
|---|---|---|
| **Los fallos de la beta 1** | Se esperan | Desconocido: es lo que define el tamaño de la beta 2 |
| Firma de código del `.exe` | Requiere comprar un certificado | Dinero, no trabajo. Mientras tanto, Windows seguirá avisando al abrirlo |
| Traducir la encuesta BioRisk de 2022 | Decidido para después; la traduce el laboratorio | Grande, y no bloquea nada |
| Aportar las correcciones de vuelta a Sandia | Ofrecido en la carta; esperando al autor | Chico: ya están hechas y verificadas |

### Dos decisiones chicas que quedaron en su cancha

1. **El verde de «ya está completo».** Es el único color verde que queda. Se
   dejó a propósito porque verde significa terminado en todas partes. Si
   prefiere que se vaya, es un renglón.
2. **«Muy alto» o «Crítico»** para la zona de mayor riesgo de la gráfica. Hoy
   dice «Muy alto», que es el nombre del original. También es un renglón.

---

## 4. Problemas generales, dichos sin adornos

Lo que yo vigilaría, en orden de lo que más podría doler:

**El permiso es un correo, no una licencia.** Sandia se comprometió, y la
persona que lo escribió es quien lleva las licencias, así que vale. Pero hasta
que el archivo esté en GitHub, lo que respalda la redistribución pública es un
mensaje de correo. Para uso interno no cambia nada; para publicar, yo esperaría.

**El control de exportaciones sigue sin respuesta.** La portada de bioprotección
advierte que exportar el programa puede requerir licencia del Gobierno de los
Estados Unidos. Sleeper no contestó eso. No parece conciliable con que Sandia
misma publique la herramienta y la traduzca a once idiomas para laboratorios de
otros países, pero la advertencia está escrita y una conclusión propia no
sustituye una respuesta suya.

**Los tres defectos están en cancha de Sandia.** La referencia de puntuación
faltante ya se repuso aquí y quedó documentada en el historial, así que el
cálculo de este laboratorio es correcto. Lo que no se sabe es si Sandia los
corregirá, y si lo hace, **las huellas de revisión de los cuestionarios
cambiarán**. El programa ya está preparado: cada evaluación guarda con qué
revisión se capturó y el reporte avisa si no coincide. Pero habrá que decidir
qué hacer con las evaluaciones viejas, y esa decisión es del laboratorio.

**El archivo de datos en carpeta de red.** Todo el trabajo vive en un solo
archivo SQLite. Está bien para una o dos personas, y el programa avisa si no
puede guardar. Pero SQLite sobre una carpeta compartida de Windows es conocido
por corromperse cuando dos computadoras escriben a la vez. Si el laboratorio
piensa trabajar así, hay que probarlo a propósito en la beta —está en la guía—
y si va a ser lo normal, conviene hablarlo antes de que haya datos que perder.

**Respaldos.** El programa dice dónde está su archivo y advierte que se cierre
antes de copiarlo, pero no respalda solo. Si el expediente va a ser oficial,
alguien tiene que tener una rutina de respaldo, y eso es del laboratorio.

**Nadie más conoce el programa.** Está escrito en español, comentado explicando
el porqué, y tiene 129 pruebas automáticas que corren solas en cada cambio.
Eso es lo que se puede hacer desde adentro. Lo que no se puede resolver desde
aquí es que hoy sólo este laboratorio lo usa.

---

## 5. En qué orden, el día que lleguen las tres cosas

1. Leer los fallos de la beta y ordenarlos. Mandan ellos.
2. Si Sandia contestó sobre el nombre: aplicar la decisión **antes** de tocar
   otra cosa, porque si hay renombrado conviene que entre limpio y no encima de
   otros cambios.
3. Poner la licencia de Sandia: archivo, `.zip` del armado y «Acerca de».
4. Decidir si se sigue distribuyendo el `.jar`. Si no, cierra JFreeChart y
   `Built-By` de un plumazo.
5. Corregir lo que haya salido en la beta.
6. Armar la beta 2 y volver a probar.

Nada de esto empieza hasta que usted lo diga.
