"""Modelos del dominio: datos del invernadero sin lógica de infraestructura."""

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
        return cls(
            nodo=datos["nodo"],
            fecha=datetime.fromisoformat(datos["fecha"]),
            temperatura=float(datos["temperatura"]),
            humedad_aire=float(datos["humedad_aire"]),
            humedad_sustrato=float(datos["humedad_sustrato"]),
        )

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
    "temperatura": Umbral(minimo=18.0, maximo=28.0, margen=2.0),
    "humedad_aire": Umbral(minimo=60.0, maximo=80.0, margen=5.0),
    "humedad_sustrato": Umbral(minimo=45.0, maximo=70.0, margen=5.0),
}
