#!/usr/bin/env python3
"""Genera el .jar de BioRAM con la interfaz en español.

Solo reemplaza lang/FormStrings_es.properties dentro del .jar; todo lo demás se
copia byte por byte. El menú "Configuración > Seleccionar idioma..." ya ofrece
español, porque la lista de idiomas viene fija en el programa.

Los acentos se convierten a secuencias \\uXXXX: Java 8 y versiones anteriores
leen los .properties como ISO-8859-1 y Java 9 en adelante como UTF-8, así que
escaparlos es la única forma de que el texto se vea igual en cualquier versión.

Con un tercer argumento —un directorio con los .jar de JAXB— también los incluye
dentro del resultado. Hace falta para Java 11 y versiones posteriores, que ya no
traen JAXB: sin eso, BioRAM falla al abrir cualquier modelo con
NoClassDefFoundError: javax/xml/bind/JAXB.

Uso:
  python empacar.py ../bioram-4.0.5.jar ../bioram-4.0.5-es.jar
  python empacar.py ../bioram-4.0.5.jar ../bioram-4.0.5-es-java-actual.jar libs_jaxb/
"""
import pathlib
import sys
import zipfile

RUTA_EN_JAR = 'lang/FormStrings_es.properties'
FUENTE = 'FormStrings_es.utf8.properties'

# Del resto de los .jar no se copia su manifiesto, sus firmas (invalidarían el
# resultado) ni las clases por versión de Java, que exigirían declarar el .jar
# como multi-release.
EXCLUIR = ('META-INF/MANIFEST.MF', 'module-info.class')
EXCLUIR_PREFIJOS = ('META-INF/versions/', 'META-INF/maven/')
EXCLUIR_SUFIJOS = ('.SF', '.RSA', '.DSA')


def escapar(texto):
    salida = []
    for ch in texto:
        salida.append(ch if ord(ch) < 128 else f'\\u{ord(ch):04x}')
    return ''.join(salida)


def claves(texto):
    return {l.split('=', 1)[0].strip()
            for l in texto.splitlines()
            if '=' in l and not l.lstrip().startswith('#')}


def omitir(nombre):
    return (nombre in EXCLUIR
            or nombre.startswith(EXCLUIR_PREFIJOS)
            or nombre.endswith(EXCLUIR_SUFIJOS))


def main(jar_en, jar_es, dir_jaxb=None):
    with open(FUENTE, encoding='utf-8') as f:
        fuente = f.read()
    datos = escapar(fuente).encode('ascii')

    with zipfile.ZipFile(jar_en) as z:
        if RUTA_EN_JAR not in z.namelist():
            sys.exit(f'{jar_en} no contiene {RUTA_EN_JAR}')
        faltantes = claves(z.read('lang/FormStrings.properties').decode('latin-1')) - claves(fuente)
        if faltantes:
            sys.exit(f'faltan claves respecto al inglés: {sorted(faltantes)}')
        with zipfile.ZipFile(jar_es, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                contenido = datos if info.filename == RUTA_EN_JAR else z.read(info.filename)
                out.writestr(info, contenido)
            puestos = set(z.namelist())
            agregados = 0
            for extra in sorted(pathlib.Path(dir_jaxb).glob('*.jar')) if dir_jaxb else []:
                with zipfile.ZipFile(extra) as zx:
                    for info in zx.infolist():
                        if info.is_dir() or info.filename in puestos or omitir(info.filename):
                            continue
                        out.writestr(info, zx.read(info.filename))
                        puestos.add(info.filename)
                        agregados += 1
    print(f'{jar_es}: {len(claves(fuente))} cadenas de interfaz en español'
          + (f', {agregados} clases de JAXB incluidas' if dir_jaxb else ''))


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    main(*sys.argv[1:])
