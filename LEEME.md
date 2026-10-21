# BioRAM en español

Traducción completa al español (México) de la versión Java de BioRAM, para las
evaluaciones de bioseguridad (*biosafety*) y bioprotección (*biosecurity*).

## Qué usar en Windows 11

Necesita Java instalado (Java 8 o cualquier versión posterior). Si no lo tiene,
instálelo desde <https://adoptium.net>.

| Archivo | Para qué |
|---|---|
| `BioRAM-4.0.5-es.exe` | **Recomendado.** Ejecutable: doble clic y listo. Lleva el programa adentro. |
| `BioRAM-es.bat` | Respaldo, por si el antivirus bloquea el `.exe`. Hace lo mismo. |
| `bioram-4.0.5-es-java-actual.jar` | El programa. Funciona con el Java que se instala hoy (probado en Java 21). |
| `bioram-4.0.5-es.jar` | Solo si ya tiene Java 8. Es el programa original con la interfaz traducida, sin ningún otro cambio. |
| `Biosafety_es.raml` | Modelo de evaluación de riesgos de bioseguridad. |
| `Biosecurity_es.raml` | Modelo de evaluación de riesgos de bioprotección. |

El `.exe` se basta solo: lleva el programa adentro. El `.bat`, en cambio,
necesita que `bioram-4.0.5-es-java-actual.jar` esté en la misma carpeta. Lo más
simple es poner todo junto en una carpeta, junto con los dos `.raml`.

Ya dentro del programa, use *Archivo > Abrir perfil* y seleccione
`Biosafety_es.raml` o `Biosecurity_es.raml`.

El programa toma el idioma del sistema. Si aparece en inglés, cámbielo en
*Configuración > Seleccionar idioma... > Español*.

### Si Windows o el antivirus bloquean el .exe

Es normal con ejecutables sin firma digital: Windows muestra "Windows protegió
tu PC" (SmartScreen). Elija *Más información > Ejecutar de todas formas*, o use
`BioRAM-es.bat`, que no tiene ese problema. Para firmarlo haría falta un
certificado de firma de código.

### Por qué hay dos .jar

El BioRAM original usa JAXB, una biblioteca que venía incluida en Java hasta la
versión 8 y que Java eliminó a partir de la 11. Con un Java actual, el programa
original abre su ventana pero falla al cargar cualquier modelo con el error
`NoClassDefFoundError: javax/xml/bind/JAXB`. La variante
`-es-java-actual.jar` trae JAXB adentro y por eso funciona sin instalar nada
más. El `.exe` original no sirve para esto: es solo un envoltorio que busca el
Java del sistema, no incluye Java.

## Qué se tradujo

- Las 105 preguntas de cada modelo, con sus textos de detalle (los criterios de
  puntuación de cada opción).
- Los nombres de categorías, módulos, perfiles de resultados, gráficas, ejes y
  leyendas.
- La portada de cada modelo.
- Las 185 cadenas de la interfaz: menús, botones, pestañas, avisos y el reporte.

Lo que **no** se tradujo, a propósito: los 80 nombres de agentes biológicos del
modelo de bioprotección (*Bacillus anthracis*, *Yersinia pestis*, etc.), porque
son nombres científicos en latín y se usan igual en español.

## De dónde viene la traducción

De las traducciones al español que Sandia ya había publicado en este mismo
repositorio (`BiosafetyRAM_es.raml` y `BiosecurityRAM_es.raml`), no de una
traducción nueva. Son las preguntas oficiales y se reutilizan tal cual; solo se
corrigió el formato, que traía espacios dobles y espacios duros de la conversión
desde MS Word, y se quitó la numeración "(17)" que el modelo en inglés no tiene.

Esos dos archivos se conservan porque son la fuente de la traducción. El de
bioprotección ya traducía el modelo vigente. El de bioseguridad traducía una
versión anterior, con otros identificadores y otro orden, así que **no** se puede
usar con el modelo actual: ahí está la diferencia con `Biosafety_es.raml`.

## Cómo se regenera

Todo está en `traduccion/`. Las traducciones viven en dos archivos JSON, una
entrada por texto, y los `.raml` se generan a partir de ellos:

```
cd traduccion

# 1. Extraer los textos del modelo en inglés (solo si cambia el modelo original)
python raml_es.py extraer ../Biosafety.raml   biosafety_es.json
python raml_es.py extraer ../Biosecurity.raml biosecurity_es.json

# 2. Rellenar con la traducción publicada
python reusar.py biosecurity_es.json ../BiosecurityRAM_es.raml
python reusar_biosafety.py <plantilla_en.raml>

# 3. Cambiar "centro" por "instalación", con su concordancia
python termino_instalacion.py biosafety_es.json biosecurity_es.json

# 4. Generar los modelos en español
cd ..
python traduccion/raml_es.py construir Biosafety.raml   traduccion/biosafety_es.json   Biosafety_es.raml
python traduccion/raml_es.py construir Biosecurity.raml traduccion/biosecurity_es.json Biosecurity_es.raml

# 5. Comprobar que solo cambiaron los textos
python traduccion/raml_es.py verificar Biosafety.raml   Biosafety_es.raml
python traduccion/raml_es.py verificar Biosecurity.raml Biosecurity_es.raml

# 6. Generar los .jar
cd traduccion
python empacar.py ../bioram-4.0.5.jar ../bioram-4.0.5-es.jar
python empacar.py ../bioram-4.0.5.jar ../bioram-4.0.5-es-java-actual.jar libs_jaxb/

# 7. Generar el .exe (necesita Launch4j: https://launch4j.sourceforge.net)
launch4j launch4j.xml
```

La plantilla inglesa del paso 2 es
`util/translatedQuestionMover/modelTemplates/Biosafety.raml`, que viene dentro de
`Java source.zip`. Es la versión del modelo que corresponde a la traducción
antigua y sirve de puente para emparejar las preguntas (ver `emparejar.py`).

Para corregir un texto, edite el JSON correspondiente y repita los pasos 4 y 5.
Para corregir la interfaz, edite `FormStrings_es.utf8.properties` y repita el 6.

## Cómo se verificó

`raml_es.py verificar` compara el modelo traducido contra el original elemento
por elemento y falla si cambió cualquier cosa que no sea un texto visible:
identificadores, pesos, fórmulas, imágenes. Los dos modelos pasan, así que
**calculan exactamente igual que la versión en inglés**.

Además se comprobó que:

- No queda ningún texto sin traducir (377 de 377 en bioseguridad, 268 de 268 en
  bioprotección).
- Cada pregunta conserva su patrón de puntajes (`4 =`, `2 =`, `0 =`...), idéntico
  al del inglés en las 105 preguntas de cada modelo.
- Dos preguntas distintas nunca recibieron la misma traducción, que era el riesgo
  real al emparejar el modelo de bioseguridad.
- BioRAM abre los dos modelos y muestra los nombres en español. Se probó
  cargándolos con el propio motor del programa, con Java 21.
- El `.jar` que se incrusta en el `.exe` es válido y su clase principal arranca.

Lo que **no** se pudo probar aquí, porque este entorno es Linux y sin pantalla:

- La ventana del programa. La revisión visual de la interfaz queda pendiente en
  Windows.
- Que el `.exe` encuentre el Java instalado. Eso solo se comprueba en Windows; si
  falla, `BioRAM-es.bat` es la alternativa.
- `bioram-4.0.5-es.jar` con Java 8, porque aquí solo hay Java 21. De ese archivo
  sí se verificó que es idéntico al original salvo el archivo de idioma.
