"""Fachada del módulo de lecturas: lo único que otros módulos usan."""

import json

from .modelo import Lectura
from .validador import ValidadorLecturas


class ModuloLecturas:

cd ~/Desktop/greensense-diseno
mkdir -p versiones/modulos/alertas
cat > versiones/modulos/alertas/modelo.py << 'FIN_ARCHIVO'
"""Modelo del módulo de alertas."""

from dataclasses import dataclass
from datetime import datetime

ADVERTENCIA = "advertencia"
CRITICA = "critica"


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
