"""Punto único donde se eligen las implementaciones concretas."""

import sqlite3
from dataclasses import dataclass
from datetime import timedelta

from .evaluacion import EvaluadorUmbrales
from .modelos import UMBRALES_INICIALES
from .nodos import MonitorNodos
from .notificaciones import NotificadorConsola
from .repositorios import RepositorioAlertasSQLite, RepositorioLecturasSQLite, RepositorioNodosSQLite
from .servicios import ServicioAlertas, ServicioLecturas, ServicioReportes
from .validacion import ValidadorLecturas


@dataclass
class Sistema:
    lecturas: ServicioLecturas
    alertas: ServicioAlertas
    reportes: ServicioReportes
    monitor: MonitorNodos


def crear_sistema(ruta_bd="greensense.db", notificador=None, reglas_adicionales=()):
    conexion = sqlite3.connect(ruta_bd)
    notificador = notificador or NotificadorConsola()

    repositorio_lecturas = RepositorioLecturasSQLite(conexion)
    repositorio_alertas = RepositorioAlertasSQLite(conexion)
    repositorio_nodos = RepositorioNodosSQLite(conexion)

    evaluador = EvaluadorUmbrales(UMBRALES_INICIALES, timedelta(minutes=5), reglas_adicionales)
    alertas = ServicioAlertas(repositorio_alertas, notificador)
    lecturas = ServicioLecturas(ValidadorLecturas(), repositorio_lecturas, repositorio_nodos, evaluador, alertas)

    return Sistema(
        lecturas=lecturas,
        alertas=alertas,
        reportes=ServicioReportes(repositorio_lecturas),
        monitor=MonitorNodos(repositorio_nodos, notificador, timedelta(minutes=5)),
    )
