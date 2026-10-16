"""Caso de uso: registrar una lectura que llega de un nodo."""

import logging

from ..dominio.modelos import CRITICA

registro = logging.getLogger(__name__)


class RegistrarLectura:
    def __init__(self, validador, politica, lecturas, alertas, nodos, notificador):
        self.validador = validador
        self.politica = politica
        self.lecturas = lecturas
        self.alertas = alertas
        self.nodos = nodos
        self.notificador = notificador

    def ejecutar(self, lectura):
        if not self.validador.es_valida(lectura):
            return False
        self.lecturas.guardar(lectura)
        self.nodos.registrar_actividad(lectura.nodo, lectura.fecha)
        for alerta in self.politica.evaluar(lectura):
            self.alertas.guardar(alerta)
            if alerta.severidad == CRITICA:
                self._avisar(f"Alerta crítica en {alerta.nodo}: {alerta.variable} = {alerta.valor}")
        return True

    def _avisar(self, mensaje):
        try:
            self.notificador.enviar(mensaje)
        except Exception:
            registro.exception("No se pudo enviar la notificación")
