"""Almacenamiento del módulo de nodos."""
from abc import ABC, abstractmethod
from datetime import datetime

class RepositorioNodos(ABC):
    @abstractmethod
    def registrar_actividad(self, nodo, fecha): ...
    @abstractmethod
    def conectados(self): ...
    @abstractmethod
    def marcar_desconectado(self, nodo): ...

class RepositorioNodosMemoria(RepositorioNodos):
    def __init__(self):
        self._nodos = {}
    def registrar_actividad(self, nodo, fecha):
        self._nodos[nodo] = [fecha, True]
    def conectados(self):
        return [(nodo, datos[0]) for nodo, datos in self._nodos.items() if datos[1]]
    def marcar_desconectado(self, nodo):
        self._nodos[nodo][1] = False

class RepositorioNodosSQLite(RepositorioNodos):
    def __init__(self, conexion):
        self.conexion = conexion
        conexion.execute("CREATE TABLE IF NOT EXISTS nodos (nodo TEXT PRIMARY KEY, ultima TEXT, conectado INTEGER)")

    def registrar_actividad(self, nodo, fecha):
        self.conexion.execute("INSERT OR REPLACE INTO nodos VALUES (?, ?, 1)", (nodo, fecha.isoformat()))
        self.conexion.commit()

    def conectados(self):
        filas = self.conexion.execute("SELECT nodo, ultima FROM nodos WHERE conectado = 1").fetchall()
        return [(f[0], datetime.fromisoformat(f[1])) for f in filas]

    def marcar_desconectado(self, nodo):
        self.conexion.execute("UPDATE nodos SET conectado = 0 WHERE nodo = ?", (nodo,))
        self.conexion.commit()
