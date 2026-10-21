# BioRAM en español

Traducción completa al español (México) de la versión Java de BioRAM, para las
evaluaciones de bioseguridad (*biosafety*) y bioprotección (*biosecurity*).

## Qué usar

Descargue la carpeta **`BioRAM-es/`** completa y dé doble clic al programa que
necesite:

| Archivo | Para qué |
|---|---|
| `BioRAM Bioseguridad.exe` | Abre el cuestionario de bioseguridad, ya en español. |
| `BioRAM Bioproteccion.exe` | Abre el cuestionario de bioprotección, ya en español. |
| `BioRAM.bat` | Respaldo, por si el antivirus bloquea los `.exe`. |

No hay que elegir ningún archivo: cada ejecutable abre su propio cuestionario.
Hace falta Java instalado (versión 8 o cualquiera posterior); si no lo tiene,
<https://adoptium.net>.

En la raíz hay además dos alternativas:

| Archivo | Para qué |
|---|---|
| `BioRAM-4.0.5-es-portable.exe` | Un solo archivo que lleva el programa adentro. Necesita un `.raml` en español a su lado. Útil para una memoria USB. |
| `bioram-4.0.5-es.jar` | Para quien tenga Java 8 y no quiera el programa con JAXB incluido. |

### Si Windows o el antivirus bloquean el .exe

Es normal con ejecutables sin firma digital: aparece "Windows protegió tu PC"
(SmartScreen). Elija *Más información > Ejecutar de todas formas*, o use
`BioRAM.bat`. Firmarlos requeriría un certificado de firma de código.

## Por qué antes salían las preguntas en inglés

El arranque original de BioRAM (`gov.sandia.bioram.Main`) ignora los argumentos
y deja que la ventana busque un modelo por su cuenta. En
`ResponseForm.java:56-62` recorre la carpeta y carga **el primer archivo `.raml`
que encuentra**, sin avisar:

```java
if (model == null) {
  for (File f : new File(".").listFiles()) {
    if (f.getName().endsWith(".raml")) { model = this.loadModelFromFile(f); break; }
  }
}
```

En una carpeta con `Biosafety.raml` y `Biosafety_es.raml` gana el inglés, porque
al ordenar `.` va antes que `_`. El resultado es exactamente el síntoma que se
ve: interfaz en español y cuestionario en inglés, sin haber elegido nada.

Se corrigió de tres formas, para que no vuelva a pasar:

1. **Arranque propio** (`traduccion/java/MainEs.java`): abre el modelo que se le
   indica como argumento o, si no viene ninguno, busca `Biosafety_es.raml` o
   `Biosecurity_es.raml` **por nombre exacto** junto al programa. Si no lo
   encuentra, abre vacío y lo dice, en vez de cargar otro idioma en silencio.
2. **Un ejecutable por evaluación**, cada uno con su modelo fijado.
3. **La carpeta `BioRAM-es/` no contiene ningún modelo en inglés.**

También fija el idioma en **es-MX**. La interfaz se tomaba del idioma de
Windows, así que en un Windows en inglés salía en inglés; y se usa `es_MX`, no
`es` a secas, porque el español de España escribe los decimales con coma y los
puntajes se leerían mal ("2,488" en vez de "2.488").

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

De las traducciones al español que Sandia ya había publicado en este
repositorio, no de una traducción nueva. Son las preguntas oficiales y se
reutilizan tal cual; solo se corrigió el formato, que traía espacios dobles y
espacios duros de la conversión desde MS Word, y se quitó la numeración "(17)"
que el modelo en inglés no tiene.

Esos archivos se conservan en `traduccion/fuente/`, porque son la fuente de la
traducción. Se movieron ahí para que no estorben: también acaban en `_es.raml` y
competían por la carga automática. El de bioprotección ya traducía el modelo
vigente; el de bioseguridad traducía una versión anterior, con otros
identificadores y otro orden, así que **no** sirve con el modelo actual.

## Cómo se regenera

Todo con un comando, desde la raíz del repositorio:

```
LAUNCH4J=/ruta/a/launch4j ./traduccion/construir.sh
```

Hace los modelos, los comprueba, compila la clase de arranque, arma los `.jar` y
genera los `.exe`. Sin `LAUNCH4J` hace todo menos los `.exe`
(Launch4j: <https://launch4j.sourceforge.net>).

Para **corregir un texto del cuestionario**, edite el JSON correspondiente en
`traduccion/` y vuelva a correr `construir.sh`. Para **corregir la interfaz**,
edite `traduccion/FormStrings_es.utf8.properties` y vuelva a correrlo.

Para rehacer la traducción desde cero (solo si cambia el modelo original en
inglés):

```
python3 traduccion/raml_es.py extraer Biosafety.raml   traduccion/biosafety_es.json
python3 traduccion/raml_es.py extraer Biosecurity.raml traduccion/biosecurity_es.json
cd traduccion
python3 reusar.py biosecurity_es.json fuente/BiosecurityRAM_es.raml
python3 reusar_biosafety.py <plantilla_en.raml>
python3 termino_instalacion.py biosafety_es.json biosecurity_es.json
cd .. && ./traduccion/construir.sh
```

La plantilla inglesa es `util/translatedQuestionMover/modelTemplates/Biosafety.raml`,
que viene dentro de `Java source.zip`. Es la versión del modelo que corresponde a
la traducción antigua y sirve de puente para emparejar las preguntas (ver
`traduccion/emparejar.py`).

## Cómo se verificó

`raml_es.py verificar` compara el modelo traducido contra el original elemento
por elemento y falla si cambió cualquier cosa que no sea un texto visible:
identificadores, pesos, fórmulas, imágenes. Los dos modelos pasan, así que
**calculan exactamente igual que la versión en inglés**.

Además se comprobó, con el motor real del programa y no leyendo el XML:

- Las 105 preguntas de cada modelo están en español, y las 51 y 37 categorías
  también. Ningún título quedó idéntico al inglés (cruce exacto de conjuntos).
- Cada pregunta conserva su patrón de puntajes (`4 =`, `2 =`, `0 =`...), igual al
  del inglés.
- Dos preguntas distintas nunca recibieron la misma traducción, que era el riesgo
  real al emparejar el modelo de bioseguridad.
- El programa abre el modelo correcto aunque en la misma carpeta estén el modelo
  en inglés y la traducción antigua.
- La interfaz sale en español aunque el sistema esté en inglés o en alemán, con
  punto decimal.

Lo que **no** se pudo probar aquí, porque este entorno es Linux y sin pantalla:

- La ventana del programa. La revisión visual queda pendiente en Windows.
- Que los `.exe` encuentren el Java instalado. Eso solo se comprueba en Windows;
  si falla, `BioRAM.bat` es la alternativa.
- `bioram-4.0.5-es.jar` con Java 8, porque aquí solo hay Java 21.
