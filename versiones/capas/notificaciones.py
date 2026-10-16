"""Envío de avisos al usuario."""

import json
import urllib.request
from abc import ABC, abstractmethod


class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensaje):
        """Envía un aviso. Puede lanzar una excepción si el canal falla."""


class NotificadorPush(Notificador):
    """Envía el aviso a un servicio push mediante HTTP."""

    def __init__(self, url, tiempo_espera=5):
        self.url = url
        self.tiempo_espera = tiempo_espera

    def enviar(self, mensaje):
        cuerpo = json.dumps({"mensaje": mensaje}).encode("utf-8")
        peticion = urllib.request.Request(
            self.url, data=cuerpo, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(peticion, timeout=self.tiempo_espera)


class NotificadorConsola(Notificador):
    """Muestra el aviso en la terminal; se usa al ejecutar el sistema en local."""

    def enviar(self, mensaje):
        print("[AVISO]", mensaje)
