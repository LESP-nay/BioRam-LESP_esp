# Trabajar en el programa desde su computadora

Para no depender de GitHub para cada prueba. Una vez instalado, ver un cambio
tarda segundos en vez de cuatro minutos.

## Lo que hay que instalar, una sola vez

1. **Python 3.13** de <https://www.python.org/downloads/>. Al instalarlo,
   **marque la casilla «Add python.exe to PATH»**. Si no la marca, nada de lo
   demás funciona.
2. **Git para Windows** de <https://git-scm.com/download/win>. Siguiente,
   siguiente, siguiente.

Para comprobar que quedaron, abra el **Símbolo del sistema** (tecla Windows,
escriba `cmd`) y teclee:

```
python --version
git --version
```

Si contestan con un número de versión, listo.

## Bajar el programa

```
cd %USERPROFILE%\Documents
git clone -b claude/spanish-translation-analysis-c7myvw https://github.com/LESP-nay/BioRam-LESP_esp.git
cd BioRam-LESP_esp\programa
pip install PySide6 pytest pyinstaller
```

La primera vez tarda, porque PySide6 son unos 130 MB.

## Correrlo

```
cd %USERPROFILE%\Documents\BioRam-LESP_esp\programa
python -m bioram.interfaz.app lab.db
```

Se abre la ventana, igual que el `.exe`, y guarda en `lab.db` ahí mismo. Para
trabajar con sus datos de verdad, ponga la ruta de su archivo en lugar de
`lab.db`.

## Comprobar que no se rompió nada

```
python -m pytest -q
```

Debe decir **130 passed** en unos segundos. **Córralo siempre antes y después
de cambiar algo**: es lo que avisa si un cambio movió un puntaje, dejó un color
ilegible o rompió la compatibilidad con los archivos de datos viejos.

## Armar el ejecutable usted mismo

En el Explorador, abra `programa\empaquetar\` y **doble clic a
`construir.bat`**. Corre las pruebas y, si pasan, arma el programa. Tarda unos
minutos y deja el resultado en:

```
programa\dist\BioRAM LESP.exe
```

Es el mismo ejecutable que baja de GitHub. Esto es lo que más tiempo ahorra:
ya no hay que esperar el armado en la nube para ver un cambio.

## Guardar los cambios

```
git add -A
git commit -m "lo que cambió y por qué"
git push
```

La primera vez que haga `push`, Git le pedirá entrar a GitHub en el navegador.

Si prefiere no subir nada todavía, trabaje sin `push`: los cambios quedan en su
computadora y se suben cuando quiera.

## Para que Claude trabaje directo en su computadora

Si quiere que los cambios se hagan sobre esta copia local en vez de en la nube:
en la **aplicación de escritorio de Claude**, vaya a **Configuración ▸ Claude
Code ▸ Remote Control** y agregue la carpeta
`Documents\BioRam-LESP_esp`. Tiene que ser la carpeta raíz, la que contiene
`.git`.

Hecho eso, pídamelo y me conecto a ella.

## Si algo falla

| Dice | Es |
|---|---|
| `'python' no se reconoce…` | No se marcó «Add python.exe to PATH». Reinstale Python marcándola |
| `'git' no se reconoce…` | Falta Git, o hay que cerrar y volver a abrir el Símbolo del sistema |
| `ModuleNotFoundError: PySide6` | Faltó el `pip install`, o se corrió en otra carpeta |
| Las pruebas fallan recién clonado | Avise antes de seguir: eso no debería pasar |
