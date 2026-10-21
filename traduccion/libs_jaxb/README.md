# JAXB para Java 11 y versiones posteriores

BioRAM lee sus modelos `.raml` con JAXB, que venía dentro de Java hasta la
versión 8 y que Java eliminó a partir de la 11. Estos son los `.jar` que
`empacar.py` incluye dentro de `bioram-4.0.5-es-java-actual.jar` para que el
programa funcione con un Java actual.

Son archivos de terceros, sin modificar, tomados de Maven Central:

| Artefacto | Versión | Licencia |
|---|---|---|
| `javax.xml.bind:jaxb-api` | 2.3.1 | CDDL 1.1 / GPL 2 con excepción classpath |
| `org.glassfish.jaxb:jaxb-runtime` | 2.3.1 | Eclipse Distribution License 1.0 |
| `org.glassfish.jaxb:txw2` | 2.3.1 | Eclipse Distribution License 1.0 |
| `com.sun.istack:istack-commons-runtime` | 3.0.7 | Eclipse Distribution License 1.0 |
| `org.jvnet.staxex:stax-ex` | 1.8 | Eclipse Distribution License 1.0 |
| `com.sun.xml.fastinfoset:FastInfoset` | 1.2.15 | Apache 2.0 / Eclipse Distribution License 1.0 |
| `javax.activation:javax.activation-api` | 1.2.0 | CDDL 1.1 / GPL 2 con excepción classpath |

Para volver a descargarlos:

```
./descargar.sh
```
