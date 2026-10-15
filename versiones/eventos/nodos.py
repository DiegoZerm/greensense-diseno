"""Supervisión de nodos: publica NodoDesconectado."""

from datetime import timedelta

from .eventos import NodoDesconectado


class MonitorNodos:
    def __init__(self, repositorio_nodos, bus, tiempo_desconexion=timedelta(minutes=5)):
        self.repositorio_nodos = repositorio_nodos
        self.bus = bus
        self.tiempo_desconexion = tiempo_desconexion

    def revisar(self, ahora):
        desconectados = []
        for nodo, ultima in self.repositorio_nodos.conectados():
            if ahora - ultima >= self.tiempo_desconexion:
                self.repositorio_nodos.marcar_desconectado(nodo)
                desconectados.append(nodo)
                self.bus.publicar(NodoDesconectado(nodo, ahora))
        return desconectados
