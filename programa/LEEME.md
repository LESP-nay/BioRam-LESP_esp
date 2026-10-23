# BioRAM LESP — el programa nuevo

Un solo programa para las dos evaluaciones, organizado como el laboratorio:

```
área  →  cepa  →  evaluación de bioseguridad
                  evaluación de bioprotección
```

Los dos cuestionarios viajan **dentro** del programa (`bioram/cuestionarios/`),
así que no hay archivos `.raml` sueltos que confundir. Todo el trabajo del
laboratorio se guarda en **un solo archivo** SQLite: respaldarlo es copiarlo.

Estado: **etapas 1, 2 y 3 terminadas**. Hay ventana:

```
cd programa
python3 -m bioram.interfaz.app lab.db
```

La pantalla de inicio muestra las áreas y, de cada una, sus cepas como tarjetas
con las dos evaluaciones a la vista y su avance. Se entra a un cuestionario
haciendo clic en su botón de color: verde para bioseguridad, azul para
bioprotección. Dentro hay cuatro pestañas: contestar, resultados, portada, y
datos y respaldo.

Está pensada para quien usa poco la computadora: letra grande, botones con
texto, colores que siempre significan lo mismo (verde completo, ámbar
empezado, gris sin empezar) y las respuestas se guardan solas.

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
| `bioram/interfaz/` | La ventana: inicio, captura, resultados, portada, respaldo y salidas. |

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

## Lo que falta

- **Etapa 4**: empaquetar en un solo `.exe`. En espera, como se acordó.

## Decisiones que quedan pendientes

- **Herencia de respuestas por área.** Hoy cada evaluación guarda sus propias
  respuestas y se pueden copiar de otra con `--copiar-de`. Falta decidir si las
  preguntas del laboratorio (prácticas, equipo, procedimientos) se responden una
  vez por área y se heredan en sus cepas.
- **Empaquetado en un `.exe`.** Es la etapa 4. Se puede con PyInstaller sobre
  Windows o con GitHub Actions; conviene decidirlo al llegar.
