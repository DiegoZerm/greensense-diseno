"""Caso de uso: detectar nodos que dejaron de enviar lecturas."""

import logging
from datetime import timedelta

registro = logging.getLogger(__name__)


class RevisarNodos:
    def __init__(self, nodos, notificador, reloj, tiempo_desconexion=timedelta(minutes=5)):
        self.nodos = nodos
        self.notificador = notificador
        self.reloj = reloj
        self.tiempo_desconexion = tiempo_desconexion

    def ejecutar(self):
        ahora = self.reloj.ahora()
        desconectados = []
        for nodo, ultima in self.nodos.conectados():
            if ahora - ultima >= self.tiempo_desconexion:
                self.nodos.marcar_desconectado(nodo)
                desconectados.append(nodo)
                try:
                    self.notificador.enviar(f"El nodo {nodo} dejó de enviar datos")
                except Exception:
                    registro.exception("No se pudo enviar el aviso de desconexión")
        return desconectados
