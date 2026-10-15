"""Canales de notificación como estrategias intercambiables."""

import json
import urllib.request
from abc import ABC, abstractmethod


class CanalNotificacion(ABC):
    @abstractmethod
    def enviar(self, mensaje): ...


class CanalPush(CanalNotificacion):
    def __init__(self, url, tiempo_espera=5):
        self.url = url
        self.tiempo_espera = tiempo_espera

    def enviar(self, mensaje):
        cuerpo = json.dumps({"mensaje": mensaje}).encode("utf-8")
        peticion = urllib.request.Request(self.url, data=cuerpo, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(peticion, timeout=self.tiempo_espera)


class CanalConsola(CanalNotificacion):
    def enviar(self, mensaje):
        print("[AVISO]", mensaje)
