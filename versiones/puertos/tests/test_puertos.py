"""Pruebas de la versión de puertos y adaptadores.

Las pruebas usan adaptadores en memoria y un reloj fijo: el núcleo se prueba
sin base de datos real, broker ni servicio push.
"""

import json
import sqlite3
from datetime import datetime

import pytest

from versiones.puertos.adaptadores.entrada_mqtt import AdaptadorMqtt
from versiones.puertos.adaptadores.memoria import (
    RelojFijo,
    RepositorioAlertasMemoria,
    RepositorioLecturasMemoria,
    RepositorioNodosMemoria,
)
from versiones.puertos.adaptadores.sqlite import RepositorioAlertasSQLite, RepositorioLecturasSQLite
from versiones.puertos.aplicacion.registrar_lectura import RegistrarLectura
from versiones.puertos.aplicacion.revisar_nodos import RevisarNodos
from versiones.puertos.dominio.modelos import ADVERTENCIA, CRITICA, Alerta, Lectura
from versiones.puertos.dominio.reglas import PoliticaUmbrales, Regla, ValidadorLecturas, reglas_iniciales
from versiones.puertos.puertos import Notificador


class NotificadorEnLista(Notificador):
    def __init__(self):
        self.mensajes = []

    def enviar(self, mensaje):
        self.mensajes.append(mensaje)


class NotificadorQueFalla(Notificador):
    def enviar(self, mensaje):
        raise ConnectionError("servicio push no disponible")


def lectura(hora, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0):
    return Lectura("nodo1", datetime.fromisoformat(f"2026-10-15T{hora}:00"),
                   temperatura, humedad_aire, humedad_sustrato)


def crear_caso_de_uso(notificador=None, reglas_extra=()):
    lecturas = RepositorioLecturasMemoria()
    alertas = RepositorioAlertasMemoria()
    caso = RegistrarLectura(ValidadorLecturas(), PoliticaUmbrales([*reglas_iniciales(), *reglas_extra]),
                            lecturas, alertas, RepositorioNodosMemoria(), notificador or NotificadorEnLista())
    return caso, lecturas, alertas


def test_1_lectura_imposible_se_descarta():
    caso, lecturas, _ = crear_caso_de_uso()
    assert caso.ejecutar(lectura("10:00", temperatura=-40.0)) is False
    assert lecturas.todas() == []


def test_2_alerta_critica_solo_despues_del_tiempo_minimo():
    politica = PoliticaUmbrales(reglas_iniciales())
    assert politica.evaluar(lectura("10:00", temperatura=32.0))[0].severidad == ADVERTENCIA
    assert politica.evaluar(lectura("10:03", temperatura=32.0))[0].severidad == ADVERTENCIA
    assert politica.evaluar(lectura("10:05", temperatura=32.0))[0].severidad == CRITICA


def test_3_si_falla_el_push_la_alerta_se_guarda():
    caso, _, alertas = crear_caso_de_uso(notificador=NotificadorQueFalla())
    for hora in ("10:00", "10:03", "10:05"):
        assert caso.ejecutar(lectura(hora, temperatura=32.0)) is True
    assert CRITICA in [alerta.severidad for alerta in alertas.todas()]


def test_4_nodo_sin_datos_se_marca_desconectado():
    nodos = RepositorioNodosMemoria()
    nodos.registrar_actividad("nodo1", datetime(2026, 10, 15, 10, 0))
    caso = RevisarNodos(nodos, NotificadorEnLista(), RelojFijo(datetime(2026, 10, 15, 10, 6)))
    assert caso.ejecutar() == ["nodo1"]
    assert nodos.conectados() == []


def test_5_regla_nueva_sin_modificar_la_politica():
    class ReglaRiesgoHongos(Regla):
        def evaluar(self, lectura):
            if lectura.humedad_aire > 85 and lectura.temperatura > 25:
                return Alerta(lectura.nodo, lectura.fecha, "humedad_aire", lectura.humedad_aire,
                              ADVERTENCIA, "riesgo de hongos")
            return None

    politica = PoliticaUmbrales([*reglas_iniciales(), ReglaRiesgoHongos()])
    alertas = politica.evaluar(lectura("10:00", temperatura=26.0, humedad_aire=90.0))
    assert any(alerta.descripcion == "riesgo de hongos" for alerta in alertas)


@pytest.fixture(params=["memoria", "sqlite"])
def repositorios(request):
    if request.param == "memoria":
        return RepositorioLecturasMemoria(), RepositorioAlertasMemoria()
    conexion = sqlite3.connect(":memory:")
    return RepositorioLecturasSQLite(conexion), RepositorioAlertasSQLite(conexion)


def test_contrato_de_repositorios(repositorios):
    """Liskov: los adaptadores en memoria y SQLite cumplen el mismo contrato."""
    lecturas, alertas = repositorios
    primera = lectura("10:00")
    lecturas.guardar(primera)
    alerta = Alerta("nodo1", primera.fecha, "temperatura", 32.0, CRITICA, "fuera de rango")
    alertas.guardar(alerta)
    assert lecturas.todas() == [primera]
    assert alertas.todas() == [alerta]


def test_adaptador_mqtt_descarta_mensajes_incompletos():
    caso, lecturas, _ = crear_caso_de_uso()
    adaptador = AdaptadorMqtt(caso)
    assert adaptador.recibir(json.dumps({"nodo": "nodo1"})) is False
    completo = {"nodo": "nodo1", "fecha": "2026-10-15T10:00:00", "temperatura": 22.0,
                "humedad_aire": 70.0, "humedad_sustrato": 55.0}
    assert adaptador.recibir(json.dumps(completo)) is True
    assert len(lecturas.todas()) == 1
