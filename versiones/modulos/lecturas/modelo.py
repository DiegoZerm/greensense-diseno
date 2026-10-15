"""Modelo del módulo de lecturas."""
from dataclasses import dataclass
from datetime import datetime

VARIABLES = ("temperatura", "humedad_aire", "humedad_sustrato")

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
