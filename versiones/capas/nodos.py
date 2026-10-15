"""Supervisión del estado de conexión de los nodos."""

import logging
from datetime import timedelta

registro = logging.getLogger(__name__)


class MonitorNodos:
    """Marca como desconectados los nodos que dejaron de enviar lecturas."""

    def __init__(self, repositorio_nodos, notificador, tiempo_desconexion=timedelta(minutes=5)):
        self.repositorio_nodos = repositorio_nodos
        self.notificador = notificador
        self.tiempo_desconexion = tiempo_desconexion

    def revisar(self, ahora):
        desconectados = []
        for nodo, ultima in self.repositorio_nodos.conectados():
            if ahora - ultima >= self.tiempo_desconexion:
                self.repositorio_nodos.marcar_desconectado(nodo)
                desconectados.append(nodo)
                self._avisar(f"El nodo {nodo} dejó de enviar datos")
        return desconectados

    def _avisar(self, mensaje):
        try:
            self.notificador.enviar(mensaje)
        except Exception:
            registro.exception("No se pudo enviar el aviso de desconexión")
