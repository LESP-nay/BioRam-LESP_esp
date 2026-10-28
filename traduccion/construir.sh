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
JAR_ORIGINAL=historico/sandia/bioram-4.0.5.jar
ENTREGA=historico/java-es
CLASES=$(mktemp -d)
trap 'rm -rf "$CLASES"' EXIT

# Los dos modelos se arman distinto, a proposito:
#
# Bioproteccion: se traduce el modelo ingles vigente, porque la traduccion
# oficial de Sandia corresponde a ese mismo modelo (comparten los 151 UUID), y
# despues se unen sus dos modulos en uno solo de 105 preguntas.
#
# Bioseguridad: se parte del modelo en espanol ya traducido. El modelo ingles
# de BioRAM 4.0.5 reparte las preguntas en dos modulos (Facility y Agent),
# mientras que la traduccion oficial al espanol corresponde a la version
# anterior, de un solo modulo. El laboratorio prefiere ese cuestionario unido,
# asi que la fuente es traduccion/fuente/Biosafety_es_corregido.raml y aqui
# solo se limpian espacios y se cambia la imagen de la grafica.
SEC_DIVIDIDO="$CLASES/Biosecurity_dividido.raml"

echo "== 1. Modelos en espanol"
python3 traduccion/raml_es.py adaptar   traduccion/fuente/Biosafety_es_corregido.raml "$ENTREGA/Biosafety_es.raml"
python3 traduccion/raml_es.py construir historico/sandia/Biosecurity.raml traduccion/biosecurity_es.json "$SEC_DIVIDIDO"

echo "== 2. Comprobacion: solo cambiaron los textos"
python3 traduccion/raml_es.py verificar traduccion/fuente/BiosafetyRAM_es.raml "$ENTREGA/Biosafety_es.raml"
python3 traduccion/raml_es.py verificar historico/sandia/Biosecurity.raml "$SEC_DIVIDIDO"

echo "== 3. Un solo modulo en bioproteccion"
python3 traduccion/unir_modulos.py "$SEC_DIVIDIDO" "$ENTREGA/Biosecurity_es.raml" "Bioprotección"

echo "== 4. Clases propias (arranque y textos que estaban en el codigo)"
javac --release 8 -nowarn -cp "$JAR_ORIGINAL" -d "$CLASES" traduccion/java/*.java

echo "== 5. Programas .jar"
cd traduccion
python3 empacar.py "../$JAR_ORIGINAL" ../historico/java-es/bioram-4.0.5-es.jar \
  --clases "$CLASES" --main-class gov.sandia.bioram.MainEs \
  --solo-espanol --reemplazar Resources/reportTemplate.vm=reportTemplate.vm
python3 empacar.py "../$JAR_ORIGINAL" "../$ENTREGA/bioram-4.0.5-es-java-actual.jar" \
  --clases "$CLASES" --jaxb libs_jaxb/ --main-class gov.sandia.bioram.MainEs \
  --solo-espanol --reemplazar Resources/reportTemplate.vm=reportTemplate.vm
cd ..

if [ -z "$LAUNCH4J" ] || [ ! -f "$LAUNCH4J/launch4j.jar" ]; then
  echo "== 6. Ejecutables .exe: omitidos (defina LAUNCH4J=/ruta/launch4j)"
  exit 0
fi

echo "== 6. Ejecutables .exe"
RAIZ=$(pwd)
for cfg in traduccion/launch4j/*.xml; do
  ( cd "$LAUNCH4J" && java -jar launch4j.jar "$RAIZ/$cfg" ) | grep -i 'created\|error' || true
done
