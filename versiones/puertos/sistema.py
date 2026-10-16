"""Conecta los adaptadores con el núcleo. Es el único lugar que conoce las tecnologías."""

import sqlite3
from dataclasses import dataclass

from .adaptadores.entrada_mqtt import AdaptadorMqtt
from .adaptadores.push import NotificadorConsola, RelojSistema
from .adaptadores.sqlite import RepositorioAlertasSQLite, RepositorioLecturasSQLite, RepositorioNodosSQLite
from .aplicacion.generar_reporte import GenerarReporte
from .aplicacion.registrar_lectura import RegistrarLectura
from .aplicacion.revisar_nodos import RevisarNodos
from .dominio.reglas import PoliticaUmbrales, ValidadorLecturas, reglas_iniciales


@dataclass
class Sistema:
    entrada: AdaptadorMqtt
    revisar_nodos: RevisarNodos
    reportes: GenerarReporte


def crear_sistema(ruta_bd="greensense.db", notificador=None, reglas_extra=()):
    conexion = sqlite3.connect(ruta_bd)
    notificador = notificador or NotificadorConsola()
    lecturas = RepositorioLecturasSQLite(conexion)
    alertas = RepositorioAlertasSQLite(conexion)
    nodos = RepositorioNodosSQLite(conexion)
    politica = PoliticaUmbrales([*reglas_iniciales(), *reglas_extra])
    registrar = RegistrarLectura(ValidadorLecturas(), politica, lecturas, alertas, nodos, notificador)
    return Sistema(
        entrada=AdaptadorMqtt(registrar),
        revisar_nodos=RevisarNodos(nodos, notificador, RelojSistema()),
        reportes=GenerarReporte(lecturas),
    )
