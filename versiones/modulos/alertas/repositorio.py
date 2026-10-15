"""Almacenamiento del módulo de alertas."""

from abc import ABC, abstractmethod
from datetime import datetime

from .modelo import Alerta


class RepositorioAlertas(ABC):
@abstractmethod
def guardar(self, alerta): ...

@abstractmethod
def todas(self): ...


class RepositorioAlertasMemoria(RepositorioAlertas):
def __init__(self):
    self._datos = []

def guardar(self, alerta):
    self._datos.append(alerta)

def todas(self):
    return list(self._datos)


class RepositorioAlertasSQLite(RepositorioAlertas):
def __init__(self, conexion):
    self.conexion = conexion
    conexion.execute("CREATE TABLE IF NOT EXISTS alertas (nodo TEXT, fecha TEXT, variable TEXT, "
                     "valor REAL, severidad TEXT, descripcion TEXT)")

def guardar(self, alerta):
    self.conexion.execute("INSERT INTO alertas VALUES (?, ?, ?, ?, ?, ?)",
                          (alerta.nodo, alerta.fecha.isoformat(), alerta.variable, alerta.valor,
                           alerta.severidad, alerta.descripcion))
    self.conexion.commit()

def todas(self):
    filas = self.conexion.execute("SELECT * FROM alertas ORDER BY fecha").fetchall()
    return [Alerta(f[0], datetime.fromisoformat(f[1]), f[2], f[3], f[4], f[5]) for f in filas]
