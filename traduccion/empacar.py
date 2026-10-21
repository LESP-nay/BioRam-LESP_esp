#!/usr/bin/env python3
"""Genera el .jar de BioRAM con la interfaz en español.

Reemplaza lang/FormStrings_es.properties dentro del .jar; todo lo demás se copia
byte por byte. El menú "Configuración > Seleccionar idioma..." ya ofrece español,
porque la lista de idiomas viene fija en el programa.

Los acentos se convierten a secuencias \\uXXXX: Java 8 y versiones anteriores
leen los .properties como ISO-8859-1 y Java 9 en adelante como UTF-8, así que
escaparlos es la única forma de que el texto se vea igual en cualquier versión.

Opciones:
  --jaxb DIR         incluye los .jar de JAXB de ese directorio. Hace falta para
                     Java 11 y posteriores, que ya no traen JAXB: sin eso BioRAM
                     falla al abrir cualquier modelo con
                     NoClassDefFoundError: javax/xml/bind/JAXB.
  --clases DIR       incluye los .class compilados de ese directorio.
  --main-class NOMBRE  cambia el Main-Class del manifiesto.

Uso:
  python empacar.py ../bioram-4.0.5.jar ../bioram-4.0.5-es.jar
  python empacar.py ../bioram-4.0.5.jar ../salida.jar --jaxb libs_jaxb/ \\
      --clases /tmp/clases --main-class gov.sandia.bioram.MainEs
"""
import argparse
import pathlib
import re
import sys
import zipfile

RUTA_EN_JAR = 'lang/FormStrings_es.properties'
FUENTE = 'FormStrings_es.utf8.properties'
MANIFIESTO = 'META-INF/MANIFEST.MF'

# De los .jar de terceros no se copia su manifiesto, sus firmas (invalidarían el
# resultado) ni las clases por versión de Java, que exigirían declarar el .jar
# como multi-release.
EXCLUIR = (MANIFIESTO, 'module-info.class')
EXCLUIR_PREFIJOS = ('META-INF/versions/', 'META-INF/maven/')
EXCLUIR_SUFIJOS = ('.SF', '.RSA', '.DSA')


def escapar(texto):
    return ''.join(c if ord(c) < 128 else f'\\u{ord(c):04x}' for c in texto)


def claves(texto):
    return {l.split('=', 1)[0].strip()
            for l in texto.splitlines()
            if '=' in l and not l.lstrip().startswith('#')}


def omitir(nombre):
    return (nombre in EXCLUIR
            or nombre.startswith(EXCLUIR_PREFIJOS)
            or nombre.endswith(EXCLUIR_SUFIJOS))


def cambiar_main_class(manifiesto, clase):
    texto = manifiesto.decode('utf-8')
    nuevo, n = re.subn(r'(?m)^Main-Class: .*$', f'Main-Class: {clase}', texto)
    if n != 1:
        sys.exit(f'se esperaba un Main-Class en el manifiesto, se encontraron {n}')
    return nuevo.encode('utf-8')


def archivos_de(directorio, patron):
    if not directorio:
        return []
    return sorted(pathlib.Path(directorio).rglob(patron))


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument('origen')
    p.add_argument('destino')
    p.add_argument('--jaxb')
    p.add_argument('--clases')
    p.add_argument('--main-class', dest='main_class')
    args = p.parse_args()

    with open(FUENTE, encoding='utf-8') as f:
        fuente = f.read()
    idioma = escapar(fuente).encode('ascii')

    with zipfile.ZipFile(args.origen) as z:
        if RUTA_EN_JAR not in z.namelist():
            sys.exit(f'{args.origen} no contiene {RUTA_EN_JAR}')
        faltantes = claves(z.read('lang/FormStrings.properties').decode('latin-1')) - claves(fuente)
        if faltantes:
            sys.exit(f'faltan claves respecto al inglés: {sorted(faltantes)}')

        with zipfile.ZipFile(args.destino, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                if info.filename == RUTA_EN_JAR:
                    contenido = idioma
                elif info.filename == MANIFIESTO and args.main_class:
                    contenido = cambiar_main_class(z.read(info.filename), args.main_class)
                else:
                    contenido = z.read(info.filename)
                out.writestr(info, contenido)

            puestos = set(z.namelist())

            clases = 0
            raiz = pathlib.Path(args.clases) if args.clases else None
            for ruta in archivos_de(args.clases, '*.class'):
                nombre = ruta.relative_to(raiz).as_posix()
                if nombre in puestos:
                    sys.exit(f'la clase {nombre} ya existe en {args.origen}')
                out.writestr(nombre, ruta.read_bytes())
                puestos.add(nombre)
                clases += 1

            jaxb = 0
            for extra in archivos_de(args.jaxb, '*.jar'):
                with zipfile.ZipFile(extra) as zx:
                    for info in zx.infolist():
                        if info.is_dir() or info.filename in puestos or omitir(info.filename):
                            continue
                        out.writestr(info, zx.read(info.filename))
                        puestos.add(info.filename)
                        jaxb += 1

    partes = [f'{len(claves(fuente))} cadenas de interfaz en español']
    if clases:
        partes.append(f'{clases} clases propias')
    if jaxb:
        partes.append(f'{jaxb} clases de JAXB')
    if args.main_class:
        partes.append(f'arranque en {args.main_class}')
    print(f'{args.destino}: ' + ', '.join(partes))


if __name__ == '__main__':
    main()
