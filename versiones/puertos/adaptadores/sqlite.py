"""Adaptadores de salida con SQLite."""

from datetime import datetime

from ..dominio.modelos import Alerta, Lectura
from ..puertos import RepositorioAlertas, RepositorioLecturas, RepositorioNodos


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
