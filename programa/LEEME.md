# BioRAM LESP — el programa nuevo

Un solo programa para las dos evaluaciones, organizado como el laboratorio:

```
área  →  cepa  →  evaluación de bioseguridad
                  evaluación de bioprotección
```

Los dos cuestionarios viajan **dentro** del programa (`bioram/cuestionarios/`),
así que no hay archivos `.raml` sueltos que confundir. Todo el trabajo del
laboratorio se guarda en **un solo archivo** SQLite: respaldarlo es copiarlo.

Estado: **en prueba beta**, con ejecutable de Windows. Para correrlo desde el
código:

```
cd programa
python3 -m bioram.interfaz.app lab.db
```

La pantalla de inicio muestra las áreas y, de cada una, sus cepas como tarjetas
con las dos evaluaciones a la vista y su avance. Se entra a un cuestionario
haciendo clic en su botón de color: cian para bioseguridad, azul marino para
bioprotección. Dentro hay tres pestañas: contestar, resultados, y datos y
respaldo. Los créditos y la licencia están en **Ayuda ▸ Acerca de**, fuera del
camino de trabajo.

Está pensada para quien usa poco la computadora: letra grande, botones con
texto, colores que siempre significan lo mismo (verde completo, ámbar
empezado, gris sin empezar) y las respuestas se guardan solas. Los colores
salen del logotipo del laboratorio y están medidos para que se lean; ver
`bioram/interfaz/estilo.py`.

Al contestar, cada criterio del cuestionario es una opción de la lista: se
elige la frase y el número lo pone el programa. Se guarda exactamente lo mismo
que escribía el programa original.

### Las dos secciones

Las 105 preguntas se contestan de corrido, pero están separadas en dos
secciones con su propio avance:

- **Agente biológico** — lo que el agente es: cómo infecta, qué tan grave es y
  qué consecuencias trae. No cambia con lo que haga el laboratorio.
- **Instalaciones del laboratorio** — procedimientos, equipo, controles y
  medidas. Es donde el laboratorio puede actuar.

El reparto no es interpretación nuestra: el modelo inglés de BioRAM 4.0.5
divide cada cuestionario en un módulo «Facility» y otro «Agent», y
`bioram/secciones.py` repite ese corte. Las pruebas comprueban que los totales
coinciden con los del original: 52 y 53 en bioseguridad, 46 y 59 en
bioprotección.

En los resultados, cada número dice de qué sección depende, y cada gráfica
dice de qué depende cada eje. Eso sale del propio modelo, no de un supuesto:
la **consecuencia depende solo del agente**, mientras que la **probabilidad
depende del agente y de las instalaciones**. Es la lectura útil para el
laboratorio: sobre el eje vertical sí puede actuar.

## Probarlo

```
cd programa
python3 -m bioram.cli --datos lab.db area nueva "Bacteriología" --responsable "QFB Pérez"
python3 -m bioram.cli --datos lab.db cepa nueva 1 "Mycobacterium tuberculosis"
python3 -m bioram.cli --datos lab.db evaluacion nueva 1 bioseguridad
python3 -m bioram.cli --datos lab.db evaluacion nueva 1 bioproteccion --plantilla "Bacillus anthracis"
python3 -m bioram.cli --datos lab.db preguntas bioseguridad --detalle
python3 -m bioram.cli --datos lab.db responder 1 17 4
python3 -m bioram.cli --datos lab.db resultados 1
```

Para traer lo ya evaluado con el programa viejo, y para volver a él:

```
python3 -m bioram.cli --datos lab.db importar 1 evaluacion_anterior.raml
python3 -m bioram.cli --datos lab.db exportar 1 para_el_programa_viejo.raml
```

## Qué hay dentro

| Archivo | Para qué |
|---|---|
| `bioram/modelo.py` | Lee el cuestionario: preguntas, criterios, perfiles de resultados y gráficas. |
| `bioram/motor.py` | El cálculo. Reproduce el motor Java original, casos raros incluidos. |
| `bioram/datos.py` | El archivo del laboratorio: áreas, cepas, evaluaciones, respuestas e historial. |
| `bioram/intercambio.py` | Importar y exportar `.raml`. |
| `bioram/cli.py` | La línea de comandos, útil para revisar y para pruebas. |
| `bioram/secciones.py` | El reparto de las preguntas en agente e instalaciones. |
| `bioram/reporte.py` | Los reportes por cepa y por área, en HTML y CSV. |
| `bioram/interfaz/` | La ventana: inicio, captura, resultados, gráfica, créditos, respaldo y salidas. |
| `bioram/interfaz/estilo.py` | La paleta y la hoja de estilo. Todos los colores están medidos. |
| `bioram/interfaz/grafica.py` | El dibujo de la gráfica de riesgo y sus ajustes. |
| `bioram/ubicacion.py` | Dónde vive el archivo de datos, y dónde los archivos que viajan dentro del `.exe`. |
| `bioram/sin_pantalla.py` | Cómo trabaja Qt sin abrir ventanas. No es igual en Linux que en Windows. |

## Lo que ya hace mejor que el programa actual

- **Guarda que una respuesta es aproximada.** El original lo mostraba en
  pantalla pero no lo escribía en el archivo, así que se perdía al cerrar.
- **Guarda quién, cuándo y el historial.** Se puede archivar una versión de una
  evaluación y volver a ella.
- **Avisa de lo que no cuadra al importar.** Si un archivo trae respuestas que
  no corresponden a ninguna pregunta del cuestionario, lo dice en vez de
  tragárselas.
- **Una cepa lleva sus dos evaluaciones**, y las respuestas se pueden copiar de
  otra cepa del área para no capturar dos veces lo mismo.

## Cómo se comprueba que las cuentas son las de siempre

Esta es la parte que no puede fallar: un cambio de programa no puede cambiar el
resultado de una evaluación de riesgo.

```
cd programa && python3 -m pytest pruebas -q
```

Las pruebas comparan contra **1,180 valores calculados con el motor Java real**:

- 380 de bioseguridad y 160 de bioprotección: 20 escenarios por cuestionario que
  cubren las 105 preguntas, con algunas sin responder a propósito.
- 640 de los 80 agentes que trae el cuestionario de bioprotección
  (*Bacillus anthracis*, *Yersinia pestis*…), que son datos reales y no
  inventados.

Todos coinciden hasta el décimo decimal. Las referencias están en
`pruebas/referencias/` y se regeneran con el arnés Java descrito ahí mismo.

También se comprueba la compatibilidad en los dos sentidos: un archivo del
programa original se importa completo, y lo que este programa exporta lo abre el
programa original y da los mismos puntajes.

## Reportes

Desde la ventana, el botón **«Guardar reporte…»** de cada evaluación genera:

- **PDF** — listo para el expediente. Lleva los datos de la evaluación, el
  avance por sección, los resultados, las gráficas y las 105 preguntas con la
  respuesta que se eligió y si fue una estimación.
- **Página web (HTML)** — lo mismo, para ver en pantalla o pegar en un oficio.
- **Hoja de cálculo (CSV)** — una fila por pregunta, para analizar aparte.

En la pantalla de inicio, **«Resumen del área…»** genera el consolidado: el
estado de todas las cepas del área y una tabla que compara sus resultados.

También desde la línea de comandos:

```
python3 -m bioram.cli --datos lab.db reporte 1 --archivo evaluacion.html
python3 -m bioram.cli --datos lab.db reporte 1 --csv --archivo evaluacion.csv
python3 -m bioram.cli --datos lab.db reporte 1 --area --archivo resumen.html
```

Dos cosas que costaron y conviene no deshacer: el PDF **no** debe fijar el
tamaño del documento (si se fija, Qt mete las 18 páginas en una sola hoja
kilométrica), y la tipografía del reporte es Arial y su equivalente libre,
porque con otras Qt escribe los dos puntos y las rayas en un código privado y
el texto del PDF no se puede copiar ni buscar. Hay una prueba que lo vigila.

## Las instalaciones se contestan una vez por área

Las preguntas de **instalaciones del laboratorio** son las mismas para todas las
cepas que se trabajan en un área: el edificio, los gabinetes, los controles de
acceso y los procedimientos no cambian de una cepa a otra. Las del **agente
biológico** sí cambian con cada cepa.

Por eso no hay que contestarlas una vez por cepa:

1. Abra la evaluación de la primera cepa del área y contéstele las preguntas de
   instalaciones.
2. En la pestaña **Datos y respaldo**, oprima **«Guardar estas respuestas para el
   área»**.
3. Cada cepa nueva de esa área arranca con esas respuestas ya contestadas. El
   programa lo dice en la misma pestaña: *«Las 52 respuestas de instalaciones de
   esta evaluación son las del área»*.

Si en una cepa alguna cambia, se modifica en su evaluación y queda como respuesta
de esa cepa: **no toca las del área ni las de las demás cepas**. La pestaña avisa
cuántas quedaron distintas.

Hay dos botones más para cuando hace falta:

| Botón | Qué hace |
|---|---|
| **Traer las del área** | Reemplaza las respuestas de instalaciones de esta evaluación con las del área. Las del agente no se tocan. |
| **Limpiar y empezar de cero** | Borra las respuestas de instalaciones de **esta** evaluación para contestarlas desde el principio. Las del área quedan guardadas. |

Desde la línea de comandos:

```
python -m bioram.cli area instalaciones 1 bioseguridad                      # ver
python -m bioram.cli area instalaciones 1 bioseguridad --de-evaluacion 3    # fijar
python -m bioram.cli area instalaciones 1 bioseguridad --limpiar            # borrar
python -m bioram.cli evaluacion nueva 5 bioseguridad --sin-heredar          # sin heredar
```

## Con qué revisión del cuestionario se calculó un resultado

El programa **no guarda los puntajes: los recalcula** a partir de las respuestas
cada vez que abre una evaluación o genera un reporte. Eso es lo correcto —así
nunca hay un puntaje viejo pegado a unas respuestas nuevas— pero tiene una
consecuencia: si el cuestionario se corrige, un reporte impreso antes y otro
impreso después pueden no coincidir.

Para que eso nunca quede sin explicación, cada cuestionario tiene una **huella de
revisión** de ocho caracteres, calculada sólo sobre lo que afecta al cálculo. Y:

- cada evaluación guarda con qué revisión se capturaron sus respuestas;
- todos los reportes la imprimen al pie, junto al número SAND;
- si una evaluación se capturó con una revisión y se reporta con otra, el
  reporte lo avisa.

Las revisiones hasta hoy:

| Cuestionario | Huella | Qué es |
|---|---|---|
| Bioseguridad | `53c8ebff` | Traducción de Sandia tal cual. En uso hasta el 23/10/2026 |
| Bioseguridad | `fc20862a` | Con la referencia de ingestión repuesta. Es la que se usa |
| Bioprotección | `e94994e1` | Sandia, sin cambios |

Si alguna vez un reporte suyo no cuadra con otro, lo primero que hay que mirar
es esa línea del pie.

## Para quien va a probar la beta

Si le tocó probar el programa, la guía de qué probar y cómo reportar está en
**[`PRUEBA-BETA.md`](PRUEBA-BETA.md)**.

## El ejecutable: cómo armarlo e instalarlo

El programa se entrega como **un solo archivo**, `BioRAM LESP.exe`, sin
instalador. Se copia a donde se vaya a usar y se le da doble clic.

### Dónde guarda el trabajo

La primera vez que se abre crea su archivo de datos, `bioram.db`, siguiendo esta
regla:

1. **Junto al ejecutable**, si ahí se puede escribir. Es el modo portátil: se
   copia la carpeta completa a una memoria USB y el trabajo viaja dentro.
2. Si no se puede escribir ahí —por ejemplo si quedó instalado en «Archivos de
   programa»— en **Documentos\BioRAM LESP\bioram.db**.

El menú **Archivo ▸ ¿Dónde se guarda mi trabajo?** dice siempre la ruta exacta.

> **Para respaldar, cierre primero el programa.** Mientras está abierto, junto a
> `bioram.db` hay dos archivos de apoyo (`-wal` y `-shm`) con los últimos
> cambios. Si se copia sólo `bioram.db` con el programa abierto, se pueden
> perder. Con el programa cerrado basta con copiar `bioram.db`.

### Armarlo en una computadora con Windows

Es el camino más directo si tienen Windows a la mano. Hace falta **Python 3.11 o
posterior**, de <https://www.python.org/downloads/>, marcando **«Add python.exe
to PATH»** al instalarlo.

Después, doble clic a `programa\empaquetar\construir.bat`. El guion instala lo
que necesita, **corre las pruebas y sólo arma el ejecutable si todas pasan**, y
lo deja en `programa\dist\`.

### Armarlo sin tener Windows

El repositorio trae un flujo de GitHub que lo arma en una máquina con Windows de
verdad, porque PyInstaller no compila cruzado: un `.exe` de Windows sólo se
arma desde Windows.

1. En GitHub, pestaña **Actions**.
2. Entrar a la ejecución más reciente de **«Ejecutable de Windows»**.
3. Abajo, en **Artifacts**, descargar **BioRAM-LESP-windows**.

Viene en un `.zip` con el ejecutable y los documentos. Ese flujo corre las
pruebas en Linux y en Windows, arma el programa, lo abre para comprobar que
arranca y que crea su archivo de datos, y verifica que lleve los datos de
versión. Si algo falla, no publica nada.

### Si Windows o el antivirus lo bloquean

Es normal con ejecutables sin firma digital: aparece «Windows protegió tu PC»
(SmartScreen). Elija **Más información ▸ Ejecutar de todas formas**. A
diferencia de las versiones anteriores, éste sí trae datos de versión —empresa,
producto, versión y copyright, visibles en Propiedades ▸ Detalles—, lo que
ayuda, pero no lo evita del todo. Evitarlo por completo requiere un certificado
de firma de código, que se compra.

## Para quien vaya a modificar el programa

Lo que conviene saber antes de tocar nada, porque son las reglas que no se
pueden romper y cada una tiene una prueba que la vigila.

**1. El cálculo es el de Sandia y no se toca.** `bioram/motor.py` reproduce el
motor Java original, con sus rarezas incluidas: divisiones entre cero que dan
infinito, potencias de base negativa que dan NaN, el cero con signo. Las
pruebas lo comparan contra valores sacados del motor Java de verdad, guardados
en `pruebas/referencias/`. Si una prueba de `test_motor.py` falla, lo más
probable es que el cambio esté mal, no la prueba.

**2. Lo que es dibujo no puede cambiar un puntaje.** El laboratorio puede
quitar un resultado de la gráfica o renombrarlo; el puntaje se sigue calculando
y se sigue reportando. `test_grafica.py` lo comprueba sobre los 19 resultados.

**3. Los colores se miden, no se eligen a ojo.** `test_estilo.py` calcula el
contraste con la fórmula de las WCAG y falla si alguien mete un color que no se
lee, si la barra de desplazamiento se queda sin estilo, o si la paleta deja un
hueco que el tema oscuro de Windows pueda llenar de negro.

**4. Un archivo de datos viejo tiene que seguir abriendo.** El esquema va por
número (`VERSION_ESQUEMA` en `datos.py`) y cada versión nueva agrega columnas
con `ALTER TABLE` al abrir. Dos trampas conocidas: los comentarios no pueden ir
dentro de un `CREATE TABLE` —SQLite reescribe el DDL en un `ALTER TABLE` y falla
con «incomplete input»— y hay una prueba que abre un archivo del esquema
anterior y comprueba que no se pierde nada.

**5. Cada evaluación recuerda con qué revisión del cuestionario se capturó.**
Si el cuestionario cambia de forma que afecte al cálculo, su huella cambia y el
reporte avisa. Eso permite corregir un cuestionario sin que un reporte viejo
mienta. La huella se calcula sólo sobre lo que afecta al cálculo: cambiar la
portada no la mueve.

**6. Lo que tiene que viajar dentro del `.exe` se comprueba.** El icono, la
palomita de las casillas y la traducción al español de los botones de Qt están
en el repositorio y `test_empaquetado.py` verifica que existan, que sirvan y
que la receta de PyInstaller los mencione. La rueda de PySide6 para Windows no
trae la traducción, así que no se puede confiar en la biblioteca instalada.

**7. Qt sin pantalla no se configura igual en los dos sistemas.** En Linux va
con la plataforma «offscreen»; en Windows NO, porque ahí offscreen deja a Qt
sin tipografías y el PDF sale sin texto que se pueda copiar. Está resuelto en
un solo lugar, `bioram/sin_pantalla.py`, con la explicación.

### Cómo se trabaja

```
cd programa
python3 -m pytest -q              # las 129 pruebas, unos 8 segundos
python3 -m bioram.interfaz.app lab.db
```

El ejecutable de Windows **no se arma aquí**: PyInstaller no compila cruzado.
Lo arma GitHub Actions en una máquina con Windows en cada empujón que toque
`programa/`; ver `.github/workflows/ejecutable-windows.yml`. La receta está en
`empaquetar/bioram_lesp.spec`.

### Dónde está el resto del contexto

| Para saber… | Lea |
|---|---|
| De quién es cada cosa y qué se puede redistribuir | `../AVISO.md` |
| Las comprobaciones contra el programa original | `../VERIFICACION.md` |
| Qué sigue y qué está detenido esperando a alguien | `../PLAN-BETA-2.md` |
| Qué probar en la beta y cómo reportar | `PRUEBA-BETA.md` |
