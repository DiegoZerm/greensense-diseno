"""Adaptador de entrada: convierte el mensaje MQTT en una Lectura del dominio."""

import json
from datetime import datetime

from ..dominio.modelos import Lectura

CAMPOS_REQUERIDOS = ("nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato")


class AdaptadorMqtt:
    def __init__(self, registrar_lectura):
        self.registrar_lectura = registrar_lectura

    def recibir(self, payload):
        datos = json.loads(payload)
        if any(campo not in datos for campo in CAMPOS_REQUERIDOS):
            return False
        lectura = Lectura(
            nodo=datos["nodo"],
            fecha=datetime.fromisoformat(datos["fecha"]),
            temperatura=float(datos["temperatura"]),
            humedad_aire=float(datos["humedad_aire"]),
            humedad_sustrato=float(datos["humedad_sustrato"]),
        )
        return self.registrar_lectura.ejecutar(lectura)
