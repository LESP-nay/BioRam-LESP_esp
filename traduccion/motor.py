"""El motor de cálculo de BioRAM, en Python.

No lo usa el programa: sirve para comprobar que un cambio en un modelo no altera
ningún resultado, sin tener que abrir la aplicación. Reproduce las reglas de
classes/model/ResultObject.java y de cada ResultMathOp*.java, y se comprobó
contra el motor Java real: 135 valores idénticos hasta el décimo decimal
(95 de bioseguridad con sus 5 conjuntos de prueba, 40 de bioprotección).

Uso:
  python motor.py <modelo.raml> <respuestas.raml>
"""
import sys
import zipfile
import xml.etree.ElementTree as ET


def leer(raml):
    with zipfile.ZipFile(raml) as z:
        return ET.fromstring(z.read('model.xml'))


class Nodo:
    def __init__(self, elem, padre=None):
        self.tag = elem.tag
        self.padre = padre
        self.peso_bruto = float(elem.findtext('rawWeight', '1.0'))
        self.normaliza = elem.findtext('normalizeChildren', 'false') == 'true'
        self.constante = float(elem.findtext('constant', '0'))
        self.exponente = float(elem.findtext('exponent', '1'))
        self.pregunta = elem.findtext('questionUUID')
        self.ref_perfil = elem.findtext('rpUUID')
        hijos = elem.find('Children')
        self.hijos = [Nodo(h, self) for h in (hijos if hijos is not None else [])]
        # Pesos normalizados: rawWeight / suma de los rawWeight de los hermanos.
        if self.normaliza and self.hijos:
            total = sum(h.peso_bruto for h in self.hijos) or 1.0
            for h in self.hijos:
                h.peso_norm = h.peso_bruto / total

    peso_norm = 0.0

    @property
    def peso(self):
        if self.padre is None:
            return self.peso_bruto
        return self.peso_norm if self.padre.normaliza else self.peso_bruto

    def puntaje(self, resp, perfiles):
        h = [n.puntaje(resp, perfiles) for n in self.hijos]
        t = self.tag

        if t == 'ResultQuestion':
            return resp.get(self.pregunta, 0.0) * self.peso
        if t == 'ResultReference':
            otro = perfiles.get(self.ref_perfil)
            return 0.0 if otro is None else self.peso * otro.puntaje(resp, perfiles)
        if t == 'ResultMathOpConstant':
            return self.constante * self.peso
        if t == 'ResultMathOpSubtract' and len(h) == 2:
            return (h[0] - h[1]) * self.peso
        if t == 'ResultMathOpDivide' and len(h) == 2:
            return (h[0] / h[1]) * self.peso
        if t == 'ResultMathOpMultiply':
            if not h:
                return 0.0
            p = 1.0
            for x in h:
                p *= x
            return p * self.peso
        if t in ('ResultMathOpMin', 'ResultMathOpMax'):
            if not h:
                return 0.0
            return (min(h) if t.endswith('Min') else max(h)) * self.peso
        if t == 'ResultMathOpExponent':
            s = sum(h)
            if -1e-6 < s < 0:   # corrección de error de coma flotante, como en Java
                s = 0.0
            return (s ** self.exponente) * self.peso
        # ResultTitle, ResultCategory, ResultMathOpAdd y cualquier otro: suma
        return sum(h) * self.peso


def cargar_perfiles(raiz):
    perfiles = {}
    for rp in raiz.findall('ResultProfile'):
        perfiles[rp.findtext('uuid')] = Nodo(rp.find('ResultTitle'))
    return perfiles


def conjuntos_de_respuestas(raiz):
    """Las respuestas se guardan por módulo, y un escenario combina un conjunto
    de cada módulo: en bioprotección, el de la instalación y el del agente. Por
    eso se juntan los conjuntos que comparten nombre."""
    escenarios = {}
    for rs in raiz.iter('ResponseSet'):
        nombre = rs.findtext('responseSetName')
        escenarios.setdefault(nombre, {}).update(
            {r.get('uuid'): float(r.text) for r in rs.findall('response')})
    return escenarios.items()


if __name__ == '__main__':
    modelo, respuestas = sys.argv[1], sys.argv[2]
    raiz = leer(modelo)
    perfiles = cargar_perfiles(raiz)
    titulos = {u: rp.findtext('ResultTitle/title')
               for u, rp in ((p.findtext('uuid'), p) for p in raiz.findall('ResultProfile'))}
    for nombre, resp in conjuntos_de_respuestas(leer(respuestas)):
        for uuid, nodo in perfiles.items():
            print(f'{nombre}\t{titulos[uuid]}\t{nodo.puntaje(resp, perfiles):.10f}')
