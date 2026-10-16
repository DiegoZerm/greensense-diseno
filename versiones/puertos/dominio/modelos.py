"""Modelos del dominio. No dependen de ninguna tecnología externa."""

from dataclasses import dataclass
from datetime import datetime

VARIABLES = ("temperatura", "humedad_aire", "humedad_sustrato")

ADVERTENCIA = "advertencia"
CRITICA = "critica"


@dataclass(frozen=True)
class Lectura:
    nodo: str
    fecha: datetime
    temperatura: float
    humedad_aire: float
    humedad_sustrato: float

    def valor(self, variable):
        return getattr(self, variable)


@dataclass(frozen=True)
class Umbral:
    minimo: float
    maximo: float
    margen: float

    def fuera_de_rango(self, valor):
        return valor < self.minimo or valor > self.maximo

    def cerca_del_limite(self, valor):
        return valor < self.minimo + self.margen or valor > self.maximo - self.margen


@dataclass(frozen=True)
class Alerta:
    nodo: str
    fecha: datetime
    variable: str
    valor: float
    severidad: str
    descripcion: str = ""


UMBRALES_INICIALES = {
    "temperatura": Umbral(18.0, 28.0, 2.0),
    "humedad_aire": Umbral(60.0, 80.0, 5.0),
    "humedad_sustrato": Umbral(45.0, 70.0, 5.0),
}
