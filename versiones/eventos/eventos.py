"""Eventos del sistema: describen algo que ya ocurrió."""

from dataclasses import dataclass
from datetime import datetime

from .modelos import Alerta, Lectura


@dataclass(frozen=True)
class LecturaRecibida:
    datos: dict


@dataclass(frozen=True)
class LecturaValidada:
    lectura: Lectura


@dataclass(frozen=True)
class AlertaGenerada:
    alerta: Alerta


@dataclass(frozen=True)
class NodoDesconectado:
    nodo: str
    fecha: datetime
