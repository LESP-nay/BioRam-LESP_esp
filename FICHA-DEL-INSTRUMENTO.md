# Ficha técnica del instrumento que usa el programa

**Para:** la instancia normativa que autoriza los instrumentos de evaluación.
**De:** Laboratorio Estatal de Salud Pública de Nayarit.
**Al:** 28 de octubre de 2026.

Este documento responde a una sola pregunta: **qué instrumento de evaluación
aplica el programa del laboratorio**, con los datos necesarios para
identificarlo sin ambigüedad y para verificar lo que aquí se afirma.

---

## 1. Identificación del instrumento

| | |
|---|---|
| **Nombre** | BioRAM — *Biosafety and Biosecurity Laboratory Risk Assessment Model* |
| **Versión** | 4.0 (distribución 4.0.5) |
| **Autor** | Sandia National Laboratories, Estados Unidos |
| **Registro del autor** | SCR1186.1 — *Biosecurity Risk Assessment Methodology (BioRAM) v. 4.0* |
| **Identificador de publicación** | SAND No. 2010-6487 |
| **Año del modelo** | 2010. El cuestionario de bioseguridad corresponde a la revisión de 2014 |
| **Origen del archivo** | Repositorio público del autor, `github.com/sandialabs/BioRAM` |
| **Idioma** | Español. **Traducción oficial de Sandia**, una de las once que el propio autor publicó |

## 2. Composición del instrumento

Son **dos cuestionarios independientes**, que se aplican por separado a cada
agente biológico:

| Cuestionario | Preguntas | Qué evalúa |
|---|---:|---|
| Bioseguridad | **105** | Riesgo de exposición accidental |
| Bioprotección (biocustodia) | **105** | Riesgo de uso indebido deliberado |

Cada cuestionario se divide, dentro del programa, en dos bloques visibles:

- **Agente biológico** — propiedades del agente. No cambian con lo que haga el
  laboratorio.
- **Instalaciones del laboratorio** — prácticas, equipo y procedimientos. Son
  las mismas para todas las cepas de un área, y por eso se capturan una vez.

Esa división es de presentación: **no altera el cálculo**, que es el del autor.

## 3. Qué instrumento **no** se está usando

El repositorio del autor incluye además **BioRAM-2022 (BioRisk)**, actualizado
en diciembre de 2023, que es un instrumento posterior y distinto, con otras
secciones y otro conjunto de preguntas.

**Ese instrumento no está implementado en el programa del laboratorio.** Existe
en el repositorio únicamente como el archivo de hoja de cálculo tal como el
autor lo publicó, sin uso. El programa no lee hojas de cálculo: aplica
exclusivamente los dos cuestionarios descritos en el apartado 2.

Se aclara porque los dos instrumentos se citan con el mismo nombre comercial,
BioRAM, y conviene distinguirlos por **versión y fecha**, no por el número de
preguntas.

## 4. Fidelidad del cálculo respecto del original

El programa del laboratorio es una reimplementación: no se rehízo el método, se
reprodujo. Lo verificado, con los respaldos en `VERIFICACION.md`:

| Comprobación | Resultado |
|---|---|
| 1 180 valores de referencia tomados del motor original, recalculados | **0 diferencias** a 10 decimales |
| 57 valores de un escenario de mitigaciones variables | **0 diferencias** |
| Archivos exportados por el programa nuevo, abiertos en el programa original | **mismos puntajes** |
| Ponderaciones medidas contra el **apéndice B** de la guía oficial del autor | **coinciden** al segundo decimal |
| Ejemplo resuelto de *Bacillus anthracis* publicado por el autor | **reproducido** |

## 5. La única modificación al contenido, y su justificación

Se documenta por transparencia, porque **sí afecta a un resultado**.

La traducción oficial al español de Sandia había **perdido una referencia de
puntuación** presente en el original en inglés: la pregunta sobre inventarios
dejó de contribuir al perfil de exposición por contacto. El efecto era que ese
perfil salía **más bajo de lo que corresponde**.

La referencia se repuso el **23 de octubre de 2026**, y la reposición se
verificó contra el original en inglés de 2014: tras reponerla, los **7 600
valores comparados dan diferencia cero**. Es decir, la corrección **no introduce
un criterio local**: restituye la fidelidad al instrumento del autor.

El hallazgo se comunicó a Sandia. El detalle completo está en
`VERIFICACION.md`, apartado 2 bis.

## 6. Trazabilidad

Cada evaluación guarda **con qué revisión del cuestionario se capturó**, y el
reporte lo imprime al pie. Si una evaluación se capturó con una revisión y se
reporta con otra, el propio reporte lo advierte.

Esto permite dos cosas que importan para un expediente: saber siempre con qué
versión del instrumento se obtuvo un número, y poder corregir el instrumento en
el futuro sin que un reporte anterior quede sin explicación.

| Cuestionario | Revisión vigente |
|---|---|
| Bioseguridad | `fc20862a` |
| Bioprotección | `e94994e1` |

## 7. Situación de derechos

El autor confirmó por escrito, el **28 de octubre de 2026**, por conducto de
**Robert Sleeper JD, Licensing Executive de Sandia National Laboratories**, que:

- el producto es el de **código abierto**, no la versión propietaria;
- se publicó **sin licencia atribuida**, y Sandia se comprometió a atribuirle
  una licencia **BSD de 3 cláusulas**, que permite usar, modificar y
  distribuir;
- el laboratorio **puede seguir adelante** mientras la licencia se formaliza.

A la fecha la licencia **aún no está publicada**. El correo del autor obra en el
expediente del laboratorio. El detalle está en `AVISO.md`.

## 8. Cómo verificar lo aquí afirmado

Todo lo anterior es comprobable por un tercero sin depender de este documento:

| Qué | Dónde |
|---|---|
| El instrumento original del autor | `github.com/sandialabs/BioRAM`, y copia en `historico/sandia/` |
| La guía oficial del autor, con el apéndice B y el ejemplo resuelto | `historico/sandia/BioRAM UserGuide SAND.pdf` |
| Las comprobaciones, una por una | `VERIFICACION.md` |
| Procedencia, derechos y licencias | `AVISO.md` |
| Las pruebas automáticas que vigilan el cálculo | `programa/pruebas/`, se corren con `python3 -m pytest` |

---

**Lo que el laboratorio solicita.** Que se indique, por nombre, versión y fecha,
cuál instrumento está autorizado para su uso, y si el aquí descrito —BioRAM
v. 4.0, modelo 2010, en la traducción oficial al español de Sandia— lo está, no
lo está, o se encuentra pendiente de revisión.
