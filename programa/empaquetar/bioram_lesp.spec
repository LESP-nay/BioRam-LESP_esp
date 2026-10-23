# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
#
# Receta de PyInstaller para armar el ejecutable.
#
#     cd programa && pyinstaller empaquetar/bioram_lesp.spec --noconfirm
#
# Sale un solo archivo, sin instalador y sin ventana de consola. En Windows se
# llama «BioRAM LESP.exe» y se puede copiar a una memoria USB: el archivo de
# datos se guarda junto a él, y si esa carpeta no se puede escribir, en los
# Documentos del usuario (ver bioram/ubicacion.py).
#
# Lo que hay que cuidar aquí es que viajen los datos que el programa necesita y
# que NO viaje lo que no usa, que en PySide6 es casi todo: sin excluir nada, el
# ejecutable pasa de unos 60 MB a más de 200.
import sys
from pathlib import Path

RAIZ = Path(SPECPATH).resolve().parent          # la carpeta programa/
PROYECTO = RAIZ.parent
WINDOWS = sys.platform == 'win32'

# Los cuestionarios y el logotipo viajan dentro: no hay archivos sueltos que el
# usuario pueda mover o borrar sin darse cuenta.
datos = [
    (str(RAIZ / 'bioram' / 'cuestionarios' / 'bioseguridad.raml'), 'bioram/cuestionarios'),
    (str(RAIZ / 'bioram' / 'cuestionarios' / 'bioproteccion.raml'), 'bioram/cuestionarios'),
]
for documento in ('LICENSE', 'AVISO.md', 'VERIFICACION.md'):
    origen = PROYECTO / documento
    if origen.exists():
        datos.append((str(origen), 'documentos'))
origen_leeme = RAIZ / 'LEEME.md'
if origen_leeme.exists():
    datos.append((str(origen_leeme), 'documentos'))

# De PySide6 sólo se usan Core, Gui, Widgets y Svg (el logotipo) más el PDF que
# escribe los reportes. Todo lo demás estorba.
SOBRAN = [
    'PySide6.QtNetwork', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuick3D',
    'PySide6.QtQuickWidgets', 'PySide6.Qt3DCore', 'PySide6.Qt3DRender',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtCharts',
    'PySide6.QtDataVisualization', 'PySide6.QtBluetooth', 'PySide6.QtNfc',
    'PySide6.QtPositioning', 'PySide6.QtLocation', 'PySide6.QtSerialPort',
    'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtDesigner', 'PySide6.QtHelp',
    'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtSensors',
    'PySide6.QtTextToSpeech', 'PySide6.QtRemoteObjects', 'PySide6.QtScxml',
    'PySide6.QtStateMachine', 'PySide6.QtSpatialAudio', 'PySide6.QtHttpServer',
    'PySide6.QtWebSockets',
    # el programa no abre ventanas de desarrollo ni usa estas bibliotecas
    'tkinter', 'unittest', 'pydoc', 'doctest', 'pytest', 'setuptools', 'pip',
    'numpy', 'matplotlib', 'PIL', 'scipy', 'pandas',
]

analisis = Analysis(
    [str(RAIZ / 'empaquetar' / 'arranque.py')],
    pathex=[str(RAIZ)],
    binaries=[],
    datas=datos,
    hiddenimports=['bioram', 'bioram.cli'],
    hookspath=[],
    runtime_hooks=[],
    excludes=SOBRAN,
    noarchive=False,
)

pyz = PYZ(analisis.pure)

icono = PROYECTO / 'traduccion' / 'media' / 'bioram_lesp.ico'

exe = EXE(
    pyz,
    analisis.scripts,
    analisis.binaries,
    analisis.datas,
    [],
    name='BioRAM LESP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                  # UPX dispara falsos positivos en los antivirus
    runtime_tmpdir=None,
    # Sin consola: es un programa de ventana. Los errores que antes salían por
    # la consola ahora se muestran en un cuadro (ver interfaz/app.py).
    console=False,
    disable_windowed_traceback=False,
    icon=str(icono) if icono.exists() else None,
    # Datos de versión para las Propiedades del archivo en Windows. Sin esto
    # el ejecutable sale sin empresa, sin producto y sin versión, que es parte
    # de lo que hace saltar el aviso de SmartScreen.
    version=str(RAIZ / 'empaquetar' / 'version_windows.txt') if WINDOWS else None,
)
