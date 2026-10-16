"""Reglas del dominio: deciden sin guardar ni notificar nada."""

from abc import ABC, abstractmethod
from datetime import timedelta

from .modelos import ADVERTENCIA, CRITICA, UMBRALES_INICIALES, Alerta

LIMITES_FISICOS = {
    "temperatura": (-10.0, 60.0),
    "humedad_aire": (0.0, 100.0),
    "humedad_sustrato": (0.0, 100.0),
}


class ValidadorLecturas:
    """Decide si una lectura es físicamente posible."""

    def __init__(self, limites=None):
        self.limites = limites or LIMITES_FISICOS

    def es_valida(self, lectura):
        return all(minimo <= lectura.valor(variable) <= maximo
                   for variable, (minimo, maximo) in self.limites.items())


class Regla(ABC):
    """Contrato de una regla del invernadero."""

    @abstractmethod
    def evaluar(self, lectura):
        """Devuelve una Alerta o None."""


class ReglaRango(Regla):
    """Regla de rango para una variable, con margen de advertencia y tiempo mínimo."""

    def __init__(self, variable, umbral, tiempo_minimo=timedelta(minutes=5)):
        self.variable = variable
        self.umbral = umbral
        self.tiempo_minimo = tiempo_minimo
        self._fuera_desde = {}

    def evaluar(self, lectura):
        valor = lectura.valor(self.variable)
        if self.umbral.fuera_de_rango(valor):
            inicio = self._fuera_desde.setdefault(lectura.nodo, lectura.fecha)
            severidad = CRITICA if lectura.fecha - inicio >= self.tiempo_minimo else ADVERTENCIA
            return Alerta(lectura.nodo, lectura.fecha, self.variable, valor, severidad, "fuera de rango")
        self._fuera_desde.pop(lectura.nodo, None)
        if self.umbral.cerca_del_limite(valor):
            return Alerta(lectura.nodo, lectura.fecha, self.variable, valor, ADVERTENCIA, "cerca del límite")
        return None


class PoliticaUmbrales:
    """Aplica una lista de reglas a cada lectura."""

    def __init__(self, reglas):
        self.reglas = list(reglas)

    def evaluar(self, lectura):
        alertas = []
        for regla in self.reglas:
            alerta = regla.evaluar(lectura)
            if alerta:
                alertas.append(alerta)
        return alertas


def reglas_iniciales(umbrales=None, tiempo_minimo=timedelta(minutes=5)):
    umbrales = umbrales or UMBRALES_INICIALES
    return [ReglaRango(variable, umbral, tiempo_minimo) for variable, umbral in umbrales.items()]
