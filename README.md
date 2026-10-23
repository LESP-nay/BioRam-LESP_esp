# BioRAM — versión en español del LESP de Nayarit

Este repositorio es una copia del repositorio de **BioRAM** de Sandia National
Laboratories, más el trabajo que el **Laboratorio Estatal de Salud Pública de
Nayarit** hizo sobre él: la traducción completa al español (México) y un programa
nuevo que reúne las dos evaluaciones en una sola herramienta.

> **Lea [`AVISO.md`](AVISO.md) antes de redistribuir.** BioRAM es de Sandia
> Corporation. Su guía de usuario oficial lo declara código abierto, pero no
> viaja ningún archivo de licencia que precise las condiciones, y la portada del
> cuestionario lleva una advertencia de control de exportaciones.

## Por dónde empezar

| Si usted quiere… | Lea |
|---|---|
| Usar BioRAM en español, en Windows | **[`LEEME.md`](LEEME.md)** |
| Usar el programa nuevo (áreas, cepas y las dos evaluaciones juntas) | **[`programa/LEEME.md`](programa/LEEME.md)** |
| Saber de quién es cada cosa y qué se puede redistribuir | **[`AVISO.md`](AVISO.md)** |
| Ver las comprobaciones contra el programa original, y cómo se leen los resultados | **[`VERIFICACION.md`](VERIFICACION.md)** |
| El original en inglés de Sandia | la sección de abajo |

## Qué hay aquí

```
BioRAM-es/      El programa Java traducido, listo para usar en Windows.
                Dos ejecutables, uno por evaluación, y los dos cuestionarios
                en español. Es lo que se descarga para trabajar.

programa/       El programa nuevo, en Python. Reúne bioseguridad y
                bioprotección en una sola herramienta, organiza el trabajo
                por áreas y cepas, y guarda todo en un solo archivo.

traduccion/     Las herramientas con las que se hizo y se verifica la
                traducción, y el código Java que se cambió.

AVISO.md        Procedencia, derechos y licencias.
LEEME.md        Instrucciones del programa Java en español.
```

Lo demás en la raíz (los `.xlsx`, los `.pdf`, los `.raml` en inglés, los `.zip`
del código fuente) viene del repositorio original de Sandia y se conserva sin
cambios.

## Lo que se verificó

El cálculo de la versión en español es el mismo que el del programa original.
No es una afirmación de confianza, está comprobado:

- **1,180 valores de referencia** tomados del motor Java original se reproducen
  en el programa nuevo con **cero diferencias** a diez decimales.
- Los archivos que exporta el programa nuevo se abren con el programa Java
  original y dan los mismos puntajes.
- La unión de los módulos de cada cuestionario se verificó contra los valores
  previos: no cambió ningún número.
- Diez de las ponderaciones publicadas por Sandia en el apéndice B de su guía
  de usuario se reproducen **exactas** al centésimo en el modelo que usa el
  laboratorio.
- Ni el programa Java ni el programa en Python acceden a Internet, envían
  informes ni mandan información a ningún lado. Está auditado y documentado en
  [`AVISO.md`](AVISO.md), sección 6.

Todo el detalle, con los números y las órdenes que los produjeron, está en
[`VERIFICACION.md`](VERIFICACION.md). Ahí también está explicado por qué el
modelo es multiplicativo y qué significa eso al leer un resultado.

Dos cosas que conviene saber sobre **bioseguridad**:

1. El cuestionario oficial de Sandia en español corresponde a una **revisión
   distinta** del `Biosafety.raml` inglés que está en la raíz de este
   repositorio, aunque los dos declaren «Versión 1.0, septiembre de 2010». Es la
   revisión de 2014 que viene dentro de `Java source.zip`, con la que comparte
   los 105 identificadores de pregunta. Los resultados no son comparables con
   los de quien use el inglés de hoy.
2. Esa traducción de Sandia **perdió una referencia de puntuación**, y por eso
   subestima la probabilidad de infección por ingestión (hasta 1.07 de 4, en el
   77.5 % de los escenarios). Hay que decidir si se repone. Está documentado con
   los números en [`VERIFICACION.md`](VERIFICACION.md), sección 2 bis.

Bioprotección no tiene ninguno de los dos problemas: es el mismo modelo que el
inglés y da los mismos números.

---
---

# README original de Sandia

*A partir de aquí, el README tal como venía en el repositorio de Sandia, sin
cambios.*

# BioRAM
BioSafety and BioSecurity Laboratory Risk Assessment Tool

See the BioRAM UserGuide SAND for details on the methods used in the tool and examples.  

You can use either the excel version or the Java versions.  

For the excel, the BioRAM-2022 (BioRisk) file is the newest (still in beta) and joins the safety and security assessment into a single assessment tool. 

(The monkey pox files include an example biorisk assessment of a laboratory conducting diagnostics on monkey pox.)

-----


For the Java version, you will need the BioRAM-4.0.5.exe or BioRAM-4.0.5.jar and correct .raml file.  BioSafety.raml is the model for biosafety risk assessments, and Biosecurity.raml for security assessments.  The files with 2-digit iso extensions are translated versions of the questions.

The BioRAM 4.0 Directions will review the details on opening and using the Java BioRAM tool.  

For Chemical Security assessments, the ChemSAM files can be used. 

Source code is availble in the .zip file
