"""Fachada del módulo de notificaciones."""
import logging
registro = logging.getLogger(__name__)

class ModuloNotificaciones:
    def __init__(self, notificador):
        self._notificador = notificador

    def notificar(self, mensaje):
        try:
            self._notificador.enviar(mensaje)
            return True
        except Exception:
            registro.exception("No se pudo enviar la notificación")
            return False
