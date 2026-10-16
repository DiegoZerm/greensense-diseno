"""Pruebas de la versión de eventos y estrategias.

Se usan repositorios en memoria y canales de prueba; ninguna prueba usa base
de datos real, broker ni servicio push.
"""

import json
from datetime import datetime

from versiones.eventos.bus import BusEventos
from versiones.eventos.canales import CanalNotificacion
from versiones.eventos.eventos import LecturaRecibida, LecturaValidada, NodoDesconectado
from versiones.eventos.modelos import ADVERTENCIA, CRITICA, Alerta, Lectura
from versiones.eventos.nodos import MonitorNodos
from versiones.eventos.reglas import ReglaRango, ReglaUmbral, reglas_iniciales
from versiones.eventos.repositorios import (
    RepositorioAlertasMemoria,
    RepositorioLecturasMemoria,
    RepositorioNodosMemoria,
)
from versiones.eventos.sistema import conectar
from versiones.eventos.modelos import UMBRALES_INICIALES


class CanalEnLista(CanalNotificacion):
    def __init__(self):
        self.mensajes = []

    def enviar(self, mensaje):
        self.mensajes.append(mensaje)


class CanalQueFalla(CanalNotificacion):
    def enviar(self, mensaje):
        raise ConnectionError("servicio push no disponible")


def datos(hora, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0):
    return {"nodo": "nodo1", "fecha": f"2026-10-15T{hora}:00", "temperatura": temperatura,
            "humedad_aire": humedad_aire, "humedad_sustrato": humedad_sustrato}


def armar(canales=None, reglas_extra=()):
    bus = BusEventos()
    lecturas, alertas, nodos = RepositorioLecturasMemoria(), RepositorioAlertasMemoria(), RepositorioNodosMemoria()
    conectar(bus, lecturas, alertas, nodos, [*reglas_iniciales(), *reglas_extra], canales or [CanalEnLista()])
    return bus, lecturas, alertas


def test_1_lectura_imposible_se_descarta():
    bus, lecturas, _ = armar()
    validadas = []
    bus.suscribir(LecturaValidada, validadas.append)
    bus.publicar(LecturaRecibida(datos("10:00", temperatura=-40.0)))
    assert validadas == []
    assert lecturas.todas() == []


def test_2_alerta_critica_solo_despues_del_tiempo_minimo():
    regla = ReglaRango("temperatura", UMBRALES_INICIALES["temperatura"])
    severidades = [regla.evaluar(Lectura.desde_dict(datos(h, temperatura=32.0))).severidad
                   for h in ("10:00", "10:03", "10:05")]
    assert severidades == [ADVERTENCIA, ADVERTENCIA, CRITICA]


def test_3_si_falla_el_push_la_alerta_se_guarda():
    bus, _, alertas = armar(canales=[CanalQueFalla()])
    for hora in ("10:00", "10:03", "10:05"):
        bus.publicar(LecturaRecibida(datos(hora, temperatura=32.0)))
    assert CRITICA in [alerta.severidad for alerta in alertas.todas()]


def test_4_nodo_sin_datos_se_marca_desconectado():
    bus = BusEventos()
    nodos = RepositorioNodosMemoria()
    nodos.registrar_actividad("nodo1", datetime(2026, 10, 15, 10, 0))
    publicados = []
    bus.suscribir(NodoDesconectado, publicados.append)
    assert MonitorNodos(nodos, bus).revisar(datetime(2026, 10, 15, 10, 6)) == ["nodo1"]
    assert publicados[0].nodo == "nodo1"


def test_5_regla_nueva_sin_modificar_el_evaluador():
    class ReglaRiesgoHongos(ReglaUmbral):
        def evaluar(self, lectura):
            if lectura.humedad_aire > 85 and lectura.temperatura > 25:
                return Alerta(lectura.nodo, lectura.fecha, "humedad_aire", lectura.humedad_aire,
                              ADVERTENCIA, "riesgo de hongos")
            return None

    bus, _, alertas = armar(reglas_extra=[ReglaRiesgoHongos()])
    bus.publicar(LecturaRecibida(datos("10:00", temperatura=26.0, humedad_aire=90.0)))
    assert any(alerta.descripcion == "riesgo de hongos" for alerta in alertas.todas())


def test_un_canal_que_falla_no_bloquea_a_los_demas():
    canal = CanalEnLista()
    bus, _, _ = armar(canales=[CanalQueFalla(), canal])
    for hora in ("10:00", "10:05"):
        bus.publicar(LecturaRecibida(datos(hora, temperatura=32.0)))
    assert len(canal.mensajes) == 1
    assert canal.mensajes[0].startswith("Alerta crítica")


def test_el_bus_continua_si_un_manejador_falla():
    bus = BusEventos()
    recibidos = []

    def manejador_que_falla(evento):
        raise RuntimeError("falla")

    bus.suscribir(NodoDesconectado, manejador_que_falla)
    bus.suscribir(NodoDesconectado, recibidos.append)
    bus.publicar(NodoDesconectado("nodo1", datetime(2026, 10, 15, 10, 6)))
    assert len(recibidos) == 1
    assert len(bus.errores) == 1


def test_flujo_completo_desde_el_mensaje():
    from versiones.eventos.sistema import crear_sistema

    canal = CanalEnLista()
    sistema = crear_sistema(":memory:", canales=[canal])
    for hora in ("10:00", "10:05"):
        sistema.recibir(json.dumps(datos(hora, temperatura=32.0)))
    assert sistema.reportes.estadisticas("temperatura")["maximo"] == 32.0
    assert len(canal.mensajes) == 1
