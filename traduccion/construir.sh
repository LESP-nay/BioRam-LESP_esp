#!/bin/sh
# Reconstruye todo lo que se entrega, partiendo de las tablas de traduccion.
#
# Pasos: modelos en espanol -> comprobacion -> clase de arranque -> .jar -> .exe
#
# El .exe necesita Launch4j (https://launch4j.sourceforge.net). Indique donde
# esta con LAUNCH4J; si no esta, el script hace todo lo demas y lo avisa.
#   LAUNCH4J=/ruta/launch4j ./traduccion/construir.sh
#
# Ejecutar desde la raiz del repositorio.
set -e

PLANTILLA_BIOSAFETY="${PLANTILLA_BIOSAFETY:-}"
JAR_ORIGINAL=bioram-4.0.5.jar
ENTREGA=BioRAM-es
CLASES=$(mktemp -d)
trap 'rm -rf "$CLASES"' EXIT

echo "== 1. Modelos en espanol"
python3 traduccion/raml_es.py construir Biosafety.raml   traduccion/biosafety_es.json   "$ENTREGA/Biosafety_es.raml"
python3 traduccion/raml_es.py construir Biosecurity.raml traduccion/biosecurity_es.json "$ENTREGA/Biosecurity_es.raml"

echo "== 2. Comprobacion: solo cambiaron los textos"
python3 traduccion/raml_es.py verificar Biosafety.raml   "$ENTREGA/Biosafety_es.raml"
python3 traduccion/raml_es.py verificar Biosecurity.raml "$ENTREGA/Biosecurity_es.raml"

echo "== 3. Clases propias (arranque y textos que estaban en el codigo)"
javac --release 8 -nowarn -cp "$JAR_ORIGINAL" -d "$CLASES" traduccion/java/*.java

echo "== 4. Programas .jar"
cd traduccion
python3 empacar.py "../$JAR_ORIGINAL" ../bioram-4.0.5-es.jar \
  --clases "$CLASES" --main-class gov.sandia.bioram.MainEs \
  --solo-espanol --reemplazar Resources/reportTemplate.vm=reportTemplate.vm
python3 empacar.py "../$JAR_ORIGINAL" "../$ENTREGA/bioram-4.0.5-es-java-actual.jar" \
  --clases "$CLASES" --jaxb libs_jaxb/ --main-class gov.sandia.bioram.MainEs \
  --solo-espanol --reemplazar Resources/reportTemplate.vm=reportTemplate.vm
cd ..

if [ -z "$LAUNCH4J" ] || [ ! -f "$LAUNCH4J/launch4j.jar" ]; then
  echo "== 5. Ejecutables .exe: omitidos (defina LAUNCH4J=/ruta/launch4j)"
  exit 0
fi

echo "== 5. Ejecutables .exe"
RAIZ=$(pwd)
for cfg in traduccion/launch4j/*.xml; do
  ( cd "$LAUNCH4J" && java -jar launch4j.jar "$RAIZ/$cfg" ) | grep -i 'created\|error' || true
done
