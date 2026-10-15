"""Fachada del módulo de nodos."""
from datetime import timedelta

class ModuloNodos:
    def __init__(self, repositorio, notificaciones, tiempo_desconexion=timedelta(minutes=5)):
        self._repositorio = repositorio
        self._notificaciones = notificaciones
        self._tiempo_desconexion = tiempo_desconexion

    def registrar_actividad(self, nodo, fecha):
        self._repositorio.registrar_actividad(nodo, fecha)

    def revisar(self, ahora):
        desconectados = []
        for nodo, ultima in self._repositorio.conectados():
            if ahora - ultima >= self._tiempo_desconexion:
                self._repositorio.marcar_desconectado(nodo)
                desconectados.append(nodo)
                self._notificaciones.notificar(f"El nodo {nodo} dejó de enviar datos")
        return desconectados

    def conectados(self):
        return [nodo for nodo, _ in self._repositorio.conectados()]
