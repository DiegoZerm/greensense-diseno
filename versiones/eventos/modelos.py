"""Datos del invernadero."""

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

    @classmethod
    def desde_dict(cls, datos):
        return cls(datos["nodo"], datetime.fromisoformat(datos["fecha"]), float(datos["temperatura"]),
                   float(datos["humedad_aire"]), float(datos["humedad_sustrato"]))

    def valor(self, variable):
        return getattr(self, variable)


@dataclass(frozen=True)
class Umbral:
    minimo: float
    maximo: float
    margen: float


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
