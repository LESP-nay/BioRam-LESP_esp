# BioRAM LESP — el programa nuevo

Un solo programa para las dos evaluaciones, organizado como el laboratorio:

```
área  →  cepa  →  evaluación de bioseguridad
                  evaluación de bioprotección
```

Los dos cuestionarios viajan **dentro** del programa (`bioram/cuestionarios/`),
así que no hay archivos `.raml` sueltos que confundir. Todo el trabajo del
laboratorio se guarda en **un solo archivo** SQLite: respaldarlo es copiarlo.

Estado: **etapa 1 terminada** (motor de cálculo, almacén de datos, importación y
línea de comandos). La ventana es la etapa 2.

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
| `bioram/cli.py` | La línea de comandos de esta etapa. |

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

## Decisiones que quedan pendientes

- **Herencia de respuestas por área.** Hoy cada evaluación guarda sus propias
  respuestas y se pueden copiar de otra con `--copiar-de`. Falta decidir si las
  preguntas del laboratorio (prácticas, equipo, procedimientos) se responden una
  vez por área y se heredan en sus cepas.
- **Empaquetado en un `.exe`.** Es la etapa 4. Se puede con PyInstaller sobre
  Windows o con GitHub Actions; conviene decidirlo al llegar.
