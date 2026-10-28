# Histórico

Aquí no hay nada que haga falta para usar el programa ni para mejorarlo. Está
separado por eso: para que quien llegue nuevo no tenga que adivinar qué es
actual y qué no.

Pero **no es relleno, y conviene no borrarlo.** Cada carpeta se conserva por una
razón concreta.

## `sandia/` — el original, tal como Sandia lo publicó

Todo lo que está aquí lo subió `sacaske` al repositorio público
`github.com/sandialabs/BioRAM`. **No se ha modificado ni un byte**, y no debe
modificarse.

Se conserva por tres razones:

1. **Es la referencia del cálculo.** `VERIFICACION.md` afirma que el programa
   nuevo reproduce el motor original sin diferencias. Quien quiera comprobarlo
   —una auditoría, por ejemplo— necesita el original contra el cual comparar.
   `bioram-4.0.5.jar` es ese original.
2. **Es la prueba de qué versión se usó.** Sandia advirtió que existe una
   versión propietaria aparte de la de código abierto. Estos archivos
   demuestran, con su historial de commits, que el laboratorio trabajó sobre la
   abierta. Eso importa mientras la licencia se formaliza.
3. **Es la fuente de la traducción.** Los `.raml` en inglés y `Java source.zip`
   son de donde salen los textos originales que las herramientas de
   `traduccion/` comparan y reutilizan.

Contiene también instrumentos que **este laboratorio no usa**: la hoja de
cálculo `BioRAM-2022 (BioRisk)`, que es un instrumento posterior y distinto, y
los archivos `ChemSAM`, que son de evaluación de riesgo **químico**, no
biológico. Están porque venían en el repositorio del autor.

## `java-es/` — la versión en Java traducida al español

Es la primera entrega del laboratorio: el programa Java original de Sandia con
su interfaz y sus cuestionarios traducidos. Funciona y se puede usar.

Está en el histórico porque **el programa nuevo la reemplaza**: hace lo mismo,
reproduce el cálculo sin diferencias, reúne las dos evaluaciones en una sola
herramienta y no necesita Java instalado. Sus instrucciones están en
`java-es/LEEME.md`.

Dos cosas pendientes que le afectan, y que están en `../PLAN-BETA-2.md`:

- El `.jar` lleva dentro **JFreeChart**, que es LGPL, y no se incluye el texto
  de esa licencia. Si se deja de distribuir, la obligación desaparece.
- El `.jar` dice `Built-By: danbowe`, que es quien construyó el de Sandia, no
  quien construyó éste.

**Mientras se siga ofreciendo para descarga, las dos cosas hay que
resolverlas.** Si se decide dejar de distribuirlo, basta con decirlo en el
`LEEME.md` y dejarlo aquí como lo que es: el antecedente.

## Los archivos `.raml` traducidos

`java-es/Biosafety_es.raml` y `java-es/Biosecurity_es.raml` **sí son trabajo
vivo**, aunque estén aquí: son la traducción misma, y las herramientas de
`../traduccion/` siguen operando sobre ellos junto con los que lleva el
programa nuevo. Si alguna vez se corrige una errata o se repone algo, se
corrige en los cuatro archivos a la vez.
