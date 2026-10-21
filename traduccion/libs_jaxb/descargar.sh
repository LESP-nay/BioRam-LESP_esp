#!/bin/sh
# Descarga de Maven Central los .jar de JAXB que empacar.py incluye en el
# bioram-...-java-actual.jar. Ver README.md para las versiones y licencias.
set -e
cd "$(dirname "$0")"

for ruta in \
  javax/xml/bind/jaxb-api/2.3.1/jaxb-api-2.3.1 \
  org/glassfish/jaxb/jaxb-runtime/2.3.1/jaxb-runtime-2.3.1 \
  org/glassfish/jaxb/txw2/2.3.1/txw2-2.3.1 \
  com/sun/istack/istack-commons-runtime/3.0.7/istack-commons-runtime-3.0.7 \
  org/jvnet/staxex/stax-ex/1.8/stax-ex-1.8 \
  com/sun/xml/fastinfoset/FastInfoset/1.2.15/FastInfoset-1.2.15 \
  javax/activation/javax.activation-api/1.2.0/javax.activation-api-1.2.0
do
  archivo=$(basename "$ruta").jar
  echo "$archivo"
  # Maven Central limita las descargas seguidas; de ahí los reintentos.
  curl -sS --fail --retry 5 --retry-delay 10 \
    -o "$archivo" "https://repo1.maven.org/maven2/$ruta.jar"
done
