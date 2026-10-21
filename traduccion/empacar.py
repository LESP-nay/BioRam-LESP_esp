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
  --clases DIR       incluye los .class compilados de ese directorio. Si una
                     clase ya existe en el .jar, la sustituye y lo informa.
  --main-class NOMBRE  cambia el Main-Class del manifiesto.
  --solo-espanol     quita los paquetes de idioma de otros idiomas (francés,
                     alemán, árabe...). Se queda el español y el inglés, que es
                     el que el programa usa como último recurso: sin ninguno,
                     ResourceBundle lanzaría MissingResourceException.
  --reemplazar R=A   sustituye el recurso R del .jar por el archivo A. Repetible.

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

# Paquetes de idioma que no son ni el español ni el inglés de respaldo.
OTROS_IDIOMAS = re.compile(r'^lang/FormStrings_(?!es[._])\w+\.properties$')


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
    p.add_argument('--solo-espanol', action='store_true', dest='solo_espanol')
    p.add_argument('--reemplazar', action='append', default=[], metavar='RUTA=ARCHIVO')
    args = p.parse_args()

    with open(FUENTE, encoding='utf-8') as f:
        fuente = f.read()
    idioma = escapar(fuente).encode('ascii')

    reemplazos = {}
    for par in args.reemplazar:
        ruta, _, archivo = par.partition('=')
        if not archivo:
            sys.exit(f'--reemplazar espera RUTA=ARCHIVO, se recibió: {par}')
        reemplazos[ruta] = pathlib.Path(archivo).read_bytes()

    with zipfile.ZipFile(args.origen) as z:
        if RUTA_EN_JAR not in z.namelist():
            sys.exit(f'{args.origen} no contiene {RUTA_EN_JAR}')
        faltantes = claves(z.read('lang/FormStrings.properties').decode('latin-1')) - claves(fuente)
        if faltantes:
            sys.exit(f'faltan claves respecto al inglés: {sorted(faltantes)}')

        raiz = pathlib.Path(args.clases) if args.clases else None
        nuevas = {ruta.relative_to(raiz).as_posix(): ruta.read_bytes()
                  for ruta in archivos_de(args.clases, '*.class')}
        sustituidas = sorted(set(nuevas) & set(z.namelist()))

        faltan = [r for r in reemplazos if r not in z.namelist()]
        if faltan:
            sys.exit(f'{args.origen} no contiene: {faltan}')

        quitados = 0
        with zipfile.ZipFile(args.destino, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                if args.solo_espanol and OTROS_IDIOMAS.match(info.filename):
                    quitados += 1
                    continue
                if info.filename in nuevas:
                    contenido = nuevas.pop(info.filename)
                elif info.filename in reemplazos:
                    contenido = reemplazos[info.filename]
                elif info.filename == RUTA_EN_JAR:
                    contenido = idioma
                elif info.filename == MANIFIESTO and args.main_class:
                    contenido = cambiar_main_class(z.read(info.filename), args.main_class)
                else:
                    contenido = z.read(info.filename)
                out.writestr(info, contenido)

            puestos = set(z.namelist())

            # Lo que quede en `nuevas` son clases que el .jar no traía.
            for nombre, contenido in sorted(nuevas.items()):
                out.writestr(nombre, contenido)
                puestos.add(nombre)
            clases = len(nuevas)

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
    if sustituidas:
        partes.append(f'{len(sustituidas)} clases sustituidas ('
                      + ', '.join(n.rsplit('/', 1)[-1] for n in sustituidas) + ')')
    if jaxb:
        partes.append(f'{jaxb} clases de JAXB')
    if quitados:
        partes.append(f'{quitados} idiomas ajenos quitados')
    if reemplazos:
        partes.append(f'{len(reemplazos)} recursos reemplazados')
    if args.main_class:
        partes.append(f'arranque en {args.main_class}')
    print(f'{args.destino}: ' + ', '.join(partes))


if __name__ == '__main__':
    main()
