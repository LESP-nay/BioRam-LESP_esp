# Herramientas de traducción

Con esto se tradujo BioRAM al español, y con esto se traducirá el banco de
preguntas nuevo cuando llegue. No es código del programa: son herramientas de
una sola tarea que se corren a mano y dejan constancia de lo que hacen.

## La regla que gobierna todo

**Traducir cambia los textos y nada más.** Ni un UUID, ni un peso, ni una
fórmula, ni el orden de las preguntas. Si después de traducir un resultado
cambia, hay un error en la traducción, no una mejora.

Eso se comprueba, no se supone: `motor.py` calcula los resultados de un modelo
sin abrir el programa, y así se compara el antes y el después sobre miles de
escenarios. Es lo que permitió afirmar que la traducción no movió ningún
número.

## Qué hace cada herramienta

| Herramienta | Para qué |
|---|---|
| `raml_es.py` | La principal. `extraer` saca los textos de un `.raml` a un `.json`; `construir` arma el `.raml` traducido con ese `.json`; `verificar` comprueba que sólo cambiaron textos |
| `motor.py` | El cálculo en Python, para comparar un modelo antes y después sin abrir nada |
| `reusar.py` | Rellena la tabla de traducción con la traducción oficial de Sandia, cuando los UUID coinciden |
| `reusar_biosafety.py` | Lo mismo para bioseguridad, donde los UUID **no** coinciden porque la traducción oficial es de una versión anterior |
| `emparejar.py` | El puente del caso anterior: empareja una a una las preguntas de dos modelos en inglés distintos |
| `glosario_biosafety.py` | Las etiquetas que la traducción oficial no trae: categorías, perfiles de resultado y títulos de gráficas |
| `termino_instalacion.py` | Cambia «centro» por «instalación», que es lo que se usa en México, arrastrando los determinantes |
| `unir_modulos.py` | Une los módulos de preguntas de un modelo en uno solo |
| `corregir_erratas.py` | Las cuatro erratas de la traducción oficial de Sandia, con su texto en inglés y el porqué de cada una |
| `reponer_referencia.py` | Repone la referencia de puntuación que la traducción oficial había perdido, y se verifica sola |
| `portada_lesp.py` | Pone la portada institucional del laboratorio, conservando los avisos de Sandia |
| `empacar.py` | Arma el `.jar` de la versión Java. **Sólo hace falta si se sigue distribuyendo** |
| `construir.sh` | Corre toda la cadena de la versión Java de principio a fin |

## Cómo traducir un banco de preguntas nuevo

Suponiendo que llega un `.raml` en inglés —si llega como hoja de cálculo, hay
un paso previo que no existe todavía y habría que escribirlo—:

```bash
cd traduccion

# 1. Sacar los textos a traducir
python3 raml_es.py extraer   ../historico/sandia/NUEVO.raml  nuevo_es.json

# 2. Traducir el .json. Es el trabajo de verdad, y es humano.
#    Si Sandia publica una traducción oficial, reusar.py la aprovecha en vez
#    de volver a traducir lo ya traducido.

# 3. Armar el modelo en español
python3 raml_es.py construir ../historico/sandia/NUEVO.raml  nuevo_es.json  NUEVO_es.raml

# 4. Comprobar que SÓLO cambiaron textos
python3 raml_es.py verificar ../historico/sandia/NUEVO.raml  NUEVO_es.raml
```

Y antes de darlo por bueno, la comprobación que de verdad importa: que el
cálculo no se movió. `motor.py` calcula los dos modelos, el inglés y el
traducido, sobre los mismos escenarios, y **ningún resultado puede cambiar**.

## Cómo entra un banco nuevo al programa

El programa no tiene las preguntas metidas en el código: lee los `.raml` que
lleva dentro, en `programa/bioram/cuestionarios/`. Cambiar de banco es poner
ahí el archivo nuevo.

Pero hay dos cosas que **no** son automáticas y conviene saberlas antes:

1. **El reparto en «agente biológico» e «instalaciones»** está en
   `programa/bioram/secciones.py` y depende de las preguntas concretas. Un
   banco nuevo necesita que se revise ese reparto.
2. **La huella de revisión cambiará**, que es justo lo que debe pasar. Las
   evaluaciones capturadas con el banco anterior seguirán abriendo y
   reportándose con su propia huella, y el reporte avisará de la diferencia.
   Lo que no se puede es comparar unas con otras: son instrumentos distintos.

Lo que **no** hay que tocar es `programa/bioram/motor.py`. El cálculo es el de
Sandia y es el mismo para cualquier banco: lo que cambia son las preguntas, los
pesos y los perfiles, y todo eso viaja dentro del `.raml`.
