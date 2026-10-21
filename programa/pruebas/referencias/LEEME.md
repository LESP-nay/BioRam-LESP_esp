# Valores de referencia

Los calculó el **motor Java real** de BioRAM, no este programa. Son la prueba de
que la reimplementación en Python no cambia ni un resultado.

| Archivo | Qué es |
|---|---|
| `escenarios_*.json` | 20 juegos de respuestas por cuestionario, deterministas, que cubren las 105 preguntas y dejan algunas sin responder. |
| `bioseguridad.tsv`, `bioproteccion.tsv` | El puntaje de cada perfil en cada escenario, según el motor Java. |
| `agentes_bioproteccion.tsv` | Lo mismo para los 80 agentes que trae el cuestionario: datos reales. |
| `BiosafetyTestResponses.raml` | Archivo de respuestas del programa original, para probar la importación. |

## Cómo se regeneran

Hace falta el `.jar` traducido y los arneses Java que están en el historial de
este repositorio (`Referencia.java` y `CalcAll.java`). Se compilan contra el
`.jar` y se ejecutan sin pantalla:

```
javac -cp BioRAM-es/bioram-4.0.5-es-java-actual.jar -d . Referencia.java
java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Djava.awt.headless=true \
     -cp "BioRAM-es/bioram-4.0.5-es-java-actual.jar:." \
     Referencia BioRAM-es/Biosafety_es.raml escenarios.raml 20 > bioseguridad.tsv
```

Solo hay que rehacerlos si cambia un cuestionario.
