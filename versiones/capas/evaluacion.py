"""Evaluación de las lecturas contra los umbrales del cultivo."""

from abc import ABC, abstractmethod
from datetime import timedelta

from .modelos import ADVERTENCIA, CRITICA, VARIABLES, Alerta


class ReglaAdicional(ABC):
    """Regla extra que el evaluador aplica después de los umbrales.

    Permite agregar comportamientos nuevos sin modificar EvaluadorUmbrales.
    """

    @abstractmethod
    def evaluar(self, lectura):
        """Devuelve una Alerta o None."""


class EvaluadorUmbrales:
    """Decide si cada variable está normal, en advertencia o en estado crítico.

    Una variable fuera de rango genera advertencia hasta que cumple el tiempo
    mínimo; a partir de ahí genera alerta crítica.
    """

    def __init__(self, umbrales, tiempo_minimo=timedelta(minutes=5), reglas_adicionales=()):
        self.umbrales = umbrales
        self.tiempo_minimo = tiempo_minimo
        self.reglas_adicionales = list(reglas_adicionales)
        self._fuera_de_rango_desde = {}

    def evaluar(self, lectura):
        alertas = []
        for variable in VARIABLES:
            alerta = self._evaluar_variable(lectura, variable)
            if alerta:
                alertas.append(alerta)
        for regla in self.reglas_adicionales:
            alerta = regla.evaluar(lectura)
            if alerta:
                alertas.append(alerta)
        return alertas

    def _evaluar_variable(self, lectura, variable):
        umbral = self.umbrales[variable]
        valor = lectura.valor(variable)
        clave = (lectura.nodo, variable)

        if umbral.fuera_de_rango(valor):
            inicio = self._fuera_de_rango_desde.setdefault(clave, lectura.fecha)
            severidad = CRITICA if lectura.fecha - inicio >= self.tiempo_minimo else ADVERTENCIA
            return Alerta(lectura.nodo, lectura.fecha, variable, valor, severidad, "fuera de rango")

        self._fuera_de_rango_desde.pop(clave, None)
        if umbral.cerca_del_limite(valor):
            return Alerta(lectura.nodo, lectura.fecha, variable, valor, ADVERTENCIA, "cerca del límite")
        return None
