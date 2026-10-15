"""Reglas internas del módulo de alertas."""

from abc import ABC, abstractmethod
from datetime import timedelta

from .modelo import ADVERTENCIA, CRITICA, UMBRALES_INICIALES, Alerta


class Regla(ABC):
@abstractmethod
def evaluar(self, lectura):
    """Devuelve una Alerta o None."""


class ReglaRango(Regla):
def __init__(self, variable, umbral, tiempo_minimo=timedelta(minutes=5)):
    self.variable = variable
    self.umbral = umbral
    self.tiempo_minimo = tiempo_minimo
    self._fuera_desde = {}

def evaluar(self, lectura):
    valor = lectura.valor(self.variable)
    u = self.umbral
    if valor < u.minimo or valor > u.maximo:
        inicio = self._fuera_desde.setdefault(lectura.nodo, lectura.fecha)
        severidad = CRITICA if lectura.fecha - inicio >= self.tiempo_minimo else ADVERTENCIA
        return Alerta(lectura.nodo, lectura.fecha, self.variable, valor, severidad, "fuera de rango")
    self._fuera_desde.pop(lectura.nodo, None)
    if valor < u.minimo + u.margen or valor > u.maximo - u.margen:
        return Alerta(lectura.nodo, lectura.fecha, self.variable, valor, ADVERTENCIA, "cerca del límite")
    return None


def reglas_iniciales(umbrales=None, tiempo_minimo=timedelta(minutes=5)):
umbrales = umbrales or UMBRALES_INICIALES
return [ReglaRango(variable, umbral, tiempo_minimo) for variable, umbral in umbrales.items()]
