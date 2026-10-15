"""Pruebas de la versión de capas.

Ninguna prueba usa base de datos real, broker ni servicio push: los
repositorios en memoria y los notificadores de prueba sustituyen a la
infraestructura.
"""

import json
import sqlite3
from datetime import datetime

import pytest

from versiones.capas.evaluacion import EvaluadorUmbrales, ReglaAdicional
from versiones.capas.modelos import ADVERTENCIA, CRITICA, UMBRALES_INICIALES, Alerta, Lectura
from versiones.capas.nodos import MonitorNodos
from versiones.capas.notificaciones import Notificador
from versiones.capas.repositorios import (
    RepositorioAlertasMemoria,
    RepositorioLecturasMemoria,
    RepositorioLecturasSQLite,
    RepositorioNodosMemoria,
)
from versiones.capas.servicios import ServicioAlertas, ServicioLecturas, ServicioReportes
from versiones.capas.validacion import ValidadorLecturas


# ----------------------------------------------------------------------
# Dobles de prueba y utilidades
# ----------------------------------------------------------------------
class NotificadorEnLista(Notificador):
    def __init__(self):
        self.mensajes = []

    def enviar(self, mensaje):
        self.mensajes.append(mensaje)


class NotificadorQueFalla(Notificador):
    def enviar(self, mensaje):
        raise ConnectionError("servicio push no disponible")


def mensaje(hora, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0, nodo="nodo1"):
    return json.dumps({
        "nodo": nodo,
        "fecha": f"2026-10-15T{hora}:00",
        "temperatura": temperatura,
        "humedad_aire": humedad_aire,
        "humedad_sustrato": humedad_sustrato,
    })


def lectura(hora, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0):
    return Lectura.desde_dict(json.loads(mensaje(hora, temperatura, humedad_aire, humedad_sustrato)))


def crear_servicio(notificador=None, reglas_adicionales=()):
    repositorio_lecturas = RepositorioLecturasMemoria()
    repositorio_alertas = RepositorioAlertasMemoria()
    alertas = ServicioAlertas(repositorio_alertas, notificador or NotificadorEnLista())
    servicio = ServicioLecturas(
        ValidadorLecturas(),
        repositorio_lecturas,
        RepositorioNodosMemoria(),
        EvaluadorUmbrales(UMBRALES_INICIALES, reglas_adicionales=reglas_adicionales),
        alertas,
    )
    return servicio, repositorio_lecturas, repositorio_alertas


# ----------------------------------------------------------------------
# Pruebas obligatorias del contrato común
# ----------------------------------------------------------------------
def test_1_lectura_imposible_se_descarta():
    servicio, repositorio_lecturas, _ = crear_servicio()
    assert servicio.procesar_mensaje(mensaje("10:00", temperatura=-40.0)) is False
    assert repositorio_lecturas.todas() == []


def test_2_alerta_critica_solo_despues_del_tiempo_minimo():
    evaluador = EvaluadorUmbrales(UMBRALES_INICIALES)
    assert evaluador.evaluar(lectura("10:00", temperatura=32.0))[0].severidad == ADVERTENCIA
    assert evaluador.evaluar(lectura("10:03", temperatura=32.0))[0].severidad == ADVERTENCIA
    assert evaluador.evaluar(lectura("10:05", temperatura=32.0))[0].severidad == CRITICA


def test_3_si_falla_el_push_la_alerta_se_guarda():
    servicio, _, repositorio_alertas = crear_servicio(notificador=NotificadorQueFalla())
    for hora in ("10:00", "10:03", "10:05"):
        assert servicio.procesar_mensaje(mensaje(hora, temperatura=32.0)) is True
    severidades = [alerta.severidad for alerta in repositorio_alertas.todas()]
    assert CRITICA in severidades


def test_4_nodo_sin_datos_se_marca_desconectado():
    repositorio_nodos = RepositorioNodosMemoria()
    repositorio_nodos.registrar_actividad("nodo1", datetime(2026, 10, 15, 10, 0))
    notificador = NotificadorEnLista()
    monitor = MonitorNodos(repositorio_nodos, notificador)

    assert monitor.revisar(datetime(2026, 10, 15, 10, 6)) == ["nodo1"]
    assert repositorio_nodos.conectados() == []
    assert len(notificador.mensajes) == 1


def test_5_regla_nueva_sin_modificar_el_evaluador():
    class ReglaRiesgoHongos(ReglaAdicional):
        def evaluar(self, lectura):
            if lectura.humedad_aire > 85 and lectura.temperatura > 25:
                return Alerta(lectura.nodo, lectura.fecha, "humedad_aire", lectura.humedad_aire,
                              ADVERTENCIA, "riesgo de hongos")
            return None

    evaluador = EvaluadorUmbrales(UMBRALES_INICIALES, reglas_adicionales=[ReglaRiesgoHongos()])
    alertas = evaluador.evaluar(lectura("10:00", temperatura=26.0, humedad_aire=90.0))
    assert any(alerta.descripcion == "riesgo de hongos" for alerta in alertas)


# ----------------------------------------------------------------------
# Pruebas adicionales
# ----------------------------------------------------------------------
@pytest.fixture(params=["memoria", "sqlite"])
def repositorio_lecturas(request):
    if request.param == "memoria":
        return RepositorioLecturasMemoria()
    return RepositorioLecturasSQLite(sqlite3.connect(":memory:"))


def test_contrato_repositorio_de_lecturas(repositorio_lecturas):
    """Liskov: ambas implementaciones cumplen el mismo contrato."""
    primera = lectura("10:00", temperatura=21.5)
    segunda = lectura("10:01", temperatura=22.5)
    repositorio_lecturas.guardar(primera)
    repositorio_lecturas.guardar(segunda)
    assert repositorio_lecturas.todas() == [primera, segunda]


def test_reportes_por_variable_y_permiso_de_exportacion(tmp_path):
    repositorio = RepositorioLecturasMemoria()
    for hora, temperatura in (("10:00", 20.0), ("10:01", 24.0)):
        repositorio.guardar(lectura(hora, temperatura=temperatura))
    reportes = ServicioReportes(repositorio)

    assert reportes.estadisticas("temperatura") == {"minimo": 20.0, "maximo": 24.0, "promedio": 22.0}
    with pytest.raises(PermissionError):
        reportes.exportar_csv(tmp_path / "reporte.csv", rol="operador")
    reportes.exportar_csv(tmp_path / "reporte.csv", rol="supervisor")
    assert (tmp_path / "reporte.csv").read_text(encoding="utf-8").count("\n") == 3
