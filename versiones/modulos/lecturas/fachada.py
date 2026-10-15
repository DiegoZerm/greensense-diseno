"""Fachada del módulo de lecturas."""
import json
from .modelo import Lectura
from .validador import ValidadorLecturas

class ModuloLecturas:
    def __init__(self, repositorio, alertas, nodos, validador=None):
        self._repositorio = repositorio
        self._alertas = alertas
        self._nodos = nodos
        self._validador = validador or ValidadorLecturas()

    def registrar(self, mensaje):
        datos = json.loads(mensaje)
        if not self._validador.es_valida(datos):
            return False
        lectura = Lectura.desde_dict(datos)
        self._repositorio.guardar(lectura)
        self._nodos.registrar_actividad(lectura.nodo, lectura.fecha)
        self._alertas.evaluar(lectura)
        return True

    def todas(self):
        return self._repositorio.todas()
