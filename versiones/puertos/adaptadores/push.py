"""Adaptadores de notificación y de tiempo real."""

import json
import urllib.request
from datetime import datetime

from ..puertos import Notificador, Reloj


class NotificadorPushHttp(Notificador):
    def __init__(self, url, tiempo_espera=5):
        self.url = url
        self.tiempo_espera = tiempo_espera

    def enviar(self, mensaje):
        cuerpo = json.dumps({"mensaje": mensaje}).encode("utf-8")
        peticion = urllib.request.Request(self.url, data=cuerpo, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(peticion, timeout=self.tiempo_espera)


class NotificadorConsola(Notificador):
    def enviar(self, mensaje):
        print("[AVISO]", mensaje)


class RelojSistema(Reloj):
    def ahora(self):
        return datetime.now()
