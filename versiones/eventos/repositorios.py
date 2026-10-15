"""Contratos de almacenamiento con implementaciones en memoria y SQLite."""

from abc import ABC, abstractmethod
from datetime import datetime

from .modelos import Alerta, Lectura


class RepositorioLecturas(ABC):
    @abstractmethod
    def guardar(self, lectura): ...

    @abstractmethod
    def todas(self): ...


class RepositorioAlertas(ABC):
    @abstractmethod
    def guardar(self, alerta): ...

    @abstractmethod
    def todas(self): ...


class RepositorioNodos(ABC):
    @abstractmethod
    def registrar_actividad(self, nodo, fecha): ...

    @abstractmethod
    def conectados(self): ...

    @abstractmethod
    def marcar_desconectado(self, nodo): ...


class RepositorioLecturasMemoria(RepositorioLecturas):
    def __init__(self):
        self._datos = []

    def guardar(self, lectura):
        self._datos.append(lectura)

    def todas(self):
        return list(self._datos)


class RepositorioAlertasMemoria(RepositorioAlertas):
    def __init__(self):
        self._datos = []

    def guardar(self, alerta):
        self._datos.append(alerta)

    def todas(self):
        return list(self._datos)


class RepositorioNodosMemoria(RepositorioNodos):
    def __init__(self):
        self._nodos = {}

    def registrar_actividad(self, nodo, fecha):
        self._nodos[nodo] = [fecha, True]

    def conectados(self):
        return [(nodo, datos[0]) for nodo, datos in self._nodos.items() if datos[1]]

    def marcar_desconectado(self, nodo):
        self._nodos[nodo][1] = False


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
