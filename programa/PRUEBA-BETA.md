# Primera prueba beta — qué probar y qué reportar

El programa ya pasa 70 pruebas automáticas y reproduce el cálculo del BioRAM
original sin una sola diferencia. Lo que **ninguna prueba automática puede
decir** es si sirve para trabajar: si se entiende, si el camino es el que el
laboratorio sigue de verdad, y si aguanta lo que la gente hace sin querer.

Eso es lo que buscamos aquí. No hace falta ser ordenado: al contrario, **lo más
útil es usarlo como se usaría de verdad**, con prisa y sin leer instrucciones.

> **Es una prueba.** Haga las evaluaciones con datos reales si quiere, pero no
> dé por bueno nada todavía para un expediente oficial hasta que cerremos esta
> ronda.

---

## Antes de empezar

1. Copie `BioRAM LESP.exe` a una carpeta suya, por ejemplo
   `Documentos\BioRAM beta`. **No** lo deje en Descargas.
2. Doble clic. La primera vez Windows puede decir «Windows protegió tu PC»:
   **Más información ▸ Ejecutar de todas formas**. Es normal en programas sin
   firma digital y está explicado en el `LEEME.md`.
3. Compruebe en **Archivo ▸ ¿Dónde se guarda mi trabajo?** dónde quedó el
   archivo de datos. Anótelo: es todo su trabajo en un solo archivo.

---

## Lo que más nos sirve que pruebe

Está en orden de utilidad. Si sólo alcanza a hacer los tres primeros, ya valió
la pena.

### 1. Una evaluación completa, de principio a fin

Cree un área, una cepa, y conteste **las 105 preguntas** de bioseguridad.
Después vea la pestaña de resultados y guarde el reporte en PDF.

Lo que queremos saber: ¿se entiende cada pregunta? ¿el criterio de puntuación
ayuda o estorba? ¿encontró alguna pregunta que no supiera contestar, no por
falta de información, sino porque está mal redactada?

### 2. Las instalaciones que se heredan

Con la primera cepa contestada, vaya a **Datos y respaldo** y oprima
**«Guardar estas respuestas para el área»**. Después cree una segunda cepa en
la misma área y ábrala.

Lo que queremos saber: ¿llegaron ya contestadas las preguntas de instalaciones?
¿el renglón que dice en qué situación está se entiende? Pruebe también
**«Limpiar y empezar de cero»** y **«Traer las del área»**.

### 3. El reporte, como si fuera para un expediente

Guarde el reporte en los tres formatos: PDF, página web y hoja de cálculo.
Ábralos. Imprima el PDF si puede.

Lo que queremos saber: ¿se ve bien? ¿los acentos salen correctos? ¿la hoja de
cálculo abre bien en Excel? **¿Puede seleccionar y copiar el texto del PDF?**
Esta última es importante: sabemos que en Windows puede fallar y necesitamos
confirmarlo.

### 4. Portarse mal a propósito

Esto es lo que más defectos saca. Pruebe:

- Poner nombres con acentos, con diagonales (`Influenza A/H1N1`), con dos
  puntos (`BSL-3: sala 2`), muy largos, o repetidos.
- Cerrar el programa a media captura y volver a abrirlo. ¿Está todo?
- Abrir **dos ventanas del programa a la vez** sobre el mismo archivo.
- Dejar preguntas sin contestar y ver los resultados.
- Usar **«Otro valor…»** para poner un valor intermedio, como 2.5.
- Marcar respuestas como **estimación** y ver si la marca sigue ahí después de
  cerrar y abrir.
- Poner el archivo de datos en una **carpeta de red** y trabajar desde ahí.
- Copiar la carpeta completa a una **memoria USB** y abrirla en otra
  computadora.

### 5. Las dos evaluaciones de la misma cepa

Conteste bioseguridad y bioprotección de la misma cepa y compare. ¿Se entiende
que son dos cosas distintas? ¿La separación entre **agente biológico** e
**instalaciones del laboratorio** le resulta natural?

---

## Qué reportar, y cómo

Para cada cosa que encuentre, con esto basta:

| | |
|---|---|
| **Qué hacía** | «Estaba contestando la pregunta 40 de bioprotección» |
| **Qué esperaba** | «Que guardara y pasara a la siguiente» |
| **Qué pasó** | «Se quedó en la misma y la barra no avanzó» |
| **Se repite** | Sí / no / a veces |

Si sale un cuadro de error, **oprima «Mostrar detalles» y copie todo el texto**:
ahí está lo que hace falta para arreglarlo.

Una captura de pantalla vale más que una descripción. Si el problema es con el
archivo de datos, guarde una copia de `bioram.db` antes de seguir trabajando.

### Lo que NO hace falta reportar

- Que Windows avise que el programa no es seguro al abrirlo. Ya lo sabemos: es
  por la falta de firma digital.
- Que tarde unos segundos en abrir la primera vez. Es normal: el programa se
  desempaqueta solo.

---

## Lo que ya sabemos que falta o falla

Para que no gaste tiempo reportándolo:

| Pendiente | Estado |
|---|---|
| El texto del PDF podría no poderse copiar en Windows | **Confírmelo, por favor.** Es lo único de esta lista que sí queremos que nos diga |
| Windows avisa que el programa no está firmado | Conocido. Requiere un certificado de firma de código, que se compra |
| La licencia de BioRAM | Pendiente de la respuesta de Sandia |
| La encuesta nueva de 2023 | Pendiente de traducir, decidido para después |

---

## Cómo vuelve el programa corregido

Cada vez que se corrija algo saldrá un ejecutable nuevo. **Su archivo de datos
no se pierde:** basta reemplazar el `.exe` y dejar el `bioram.db` donde está.

Si una corrección llegara a cambiar algún puntaje, el programa lo dice solo: el
pie de cada reporte trae la revisión del cuestionario con la que se calculó, y
avisa si una evaluación se capturó con una revisión y se está reportando con
otra.
