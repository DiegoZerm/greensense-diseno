"""Almacenamiento del módulo de lecturas."""
from abc import ABC, abstractmethod
from datetime import datetime
from .modelo import Lectura

class RepositorioLecturas(ABC):
    @abstractmethod
    def guardar(self, lectura): ...
    @abstractmethod
    def todas(self): ...

class RepositorioLecturasMemoria(RepositorioLecturas):
    def __init__(self):
        self._datos = []
    def guardar(self, lectura):
        self._datos.append(lectura)
    def todas(self):
        return list(self._datos)

class RepositorioLecturasSQLite(RepositorioLecturas):
    def __init__(self, conexion):
        self.conexion = conexion
        conexion.execute("CREATE TABLE IF NOT EXISTS lecturas (nodo TEXT, fecha TEXT, "
                         "temperatura REAL, humedad_aire REAL, humedad_sustrato REAL)")

    def guardar(self, lectura):
        self.conexion.execute("INSERT INTO lecturas VALUES (?, ?, ?, ?, ?)",
                              (lectura.nodo, lectura.fecha.isoformat(), lectura.temperatura,
                               lectura.humedad_aire, lectura.humedad_sustrato))
        self.conexion.commit()

    def todas(self):
        filas = self.conexion.execute("SELECT * FROM lecturas ORDER BY fecha").fetchall()
        return [Lectura(f[0], datetime.fromisoformat(f[1]), f[2], f[3], f[4]) for f in filas]
