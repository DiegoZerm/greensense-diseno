"""Bus de eventos (patrón Observer)."""

import logging
from collections import defaultdict

registro = logging.getLogger(__name__)


class BusEventos:
    """Entrega cada evento a sus suscriptores.

    Si un suscriptor falla, el error se registra y los demás suscriptores
    reciben el evento de todos modos.
    """

    def __init__(self):
        self._suscriptores = defaultdict(list)
        self.errores = []

    def suscribir(self, tipo_evento, manejador):
        self._suscriptores[tipo_evento].append(manejador)

    def publicar(self, evento):
        for manejador in self._suscriptores[type(evento)]:
            try:
                manejador(evento)
            except Exception as error:
                self.errores.append(error)
                registro.exception("Falló un manejador de %s", type(evento).__name__)
