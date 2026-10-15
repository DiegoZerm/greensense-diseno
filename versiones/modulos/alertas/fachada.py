"""Fachada del módulo de alertas."""

from .modelo import CRITICA
from .reglas import reglas_iniciales


class ModuloAlertas:
def __init__(self, repositorio, notificaciones, reglas=None):
    self._repositorio = repositorio
    self._notificaciones = notificaciones
    self._reglas = list(reglas) if reglas is not None else reglas_iniciales()

def evaluar(self, lectura):
    """Aplica las reglas, guarda las alertas y pide avisar las críticas."""
    alertas = []
    for regla in self._reglas:
        alerta = regla.evaluar(lectura)
        if alerta:
            self._repositorio.guardar(alerta)
            alertas.append(alerta)
            if alerta.severidad == CRITICA:
                self._notificaciones.notificar(
                    f"Alerta crítica en {alerta.nodo}: {alerta.variable} = {alerta.valor}")
    return alertas

def todas(self):
    return self._repositorio.todas()
