"""Conecta los módulos entre sí mediante sus fachadas."""

import sqlite3
from dataclasses import dataclass

from .alertas.fachada import ModuloAlertas
from .alertas.reglas import reglas_iniciales
from .alertas.repositorio import RepositorioAlertasSQLite
from .lecturas.fachada import ModuloLecturas
from .lecturas.repositorio import RepositorioLecturasSQLite
from .nodos.fachada import ModuloNodos
from .nodos.repositorio import RepositorioNodosSQLite
from .notificaciones.fachada import ModuloNotificaciones
from .notificaciones.notificador import NotificadorConsola
from .reportes.fachada import ModuloReportes


@dataclass
class Sistema:
lecturas: ModuloLecturas
alertas: ModuloAlertas
nodos: ModuloNodos
reportes: ModuloReportes


def crear_sistema(ruta_bd="greensense.db", notificador=None, reglas_extra=()):
conexion = sqlite3.connect(ruta_bd)
notificaciones = ModuloNotificaciones(notificador or NotificadorConsola())
alertas = ModuloAlertas(RepositorioAlertasSQLite(conexion), notificaciones, [*reglas_iniciales(), *reglas_extra])
nodos = ModuloNodos(RepositorioNodosSQLite(conexion), notificaciones)
lecturas = ModuloLecturas(RepositorioLecturasSQLite(conexion), alertas, nodos)
return Sistema(lecturas=lecturas, alertas=alertas, nodos=nodos, reportes=ModuloReportes(lecturas))
