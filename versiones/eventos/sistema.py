"""Registra las suscripciones: aquí se decide quién reacciona a cada evento."""

import json
import sqlite3
from dataclasses import dataclass

from .bus import BusEventos
from .canales import CanalConsola
from .eventos import AlertaGenerada, LecturaRecibida, LecturaValidada, NodoDesconectado
from .manejadores import AlmacenLecturas, DespachadorNotificaciones, EvaluadorReglas, RegistroAlertas, Validador
from .nodos import MonitorNodos
from .reglas import reglas_iniciales
from .reportes import ServicioReportes
from .repositorios import RepositorioAlertasSQLite, RepositorioLecturasSQLite, RepositorioNodosSQLite


@dataclass
class Sistema:
    bus: BusEventos
    monitor: MonitorNodos
    reportes: ServicioReportes

    def recibir(self, payload):
        self.bus.publicar(LecturaRecibida(json.loads(payload)))


def conectar(bus, repositorio_lecturas, repositorio_alertas, repositorio_nodos, reglas, canales):
    despachador = DespachadorNotificaciones(canales)
    bus.suscribir(LecturaRecibida, Validador(bus).manejar)
    bus.suscribir(LecturaValidada, AlmacenLecturas(repositorio_lecturas, repositorio_nodos).manejar)
    bus.suscribir(LecturaValidada, EvaluadorReglas(bus, reglas).manejar)
    bus.suscribir(AlertaGenerada, RegistroAlertas(repositorio_alertas).manejar)
    bus.suscribir(AlertaGenerada, despachador.al_generar_alerta)
    bus.suscribir(NodoDesconectado, despachador.al_desconectar_nodo)


def crear_sistema(ruta_bd="greensense.db", canales=None, reglas_extra=()):
    conexion = sqlite3.connect(ruta_bd)
    bus = BusEventos()
    lecturas = RepositorioLecturasSQLite(conexion)
    alertas = RepositorioAlertasSQLite(conexion)
    nodos = RepositorioNodosSQLite(conexion)
    conectar(bus, lecturas, alertas, nodos, [*reglas_iniciales(), *reglas_extra], canales or [CanalConsola()])
    return Sistema(bus=bus, monitor=MonitorNodos(nodos, bus), reportes=ServicioReportes(lecturas))
