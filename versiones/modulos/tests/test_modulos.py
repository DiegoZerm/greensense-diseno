"""Pruebas de la versión de módulos por funcionalidad.

Cada módulo se prueba a través de su fachada, con repositorios en memoria y
notificadores de prueba.
"""

import ast
import json
from datetime import datetime
from pathlib import Path

from versiones.modulos.alertas.fachada import ModuloAlertas
from versiones.modulos.alertas.modelo import ADVERTENCIA, CRITICA, Alerta
from versiones.modulos.alertas.reglas import Regla, reglas_iniciales
from versiones.modulos.alertas.repositorio import RepositorioAlertasMemoria
from versiones.modulos.lecturas.fachada import ModuloLecturas
from versiones.modulos.lecturas.modelo import Lectura
from versiones.modulos.lecturas.repositorio import RepositorioLecturasMemoria
from versiones.modulos.nodos.fachada import ModuloNodos
from versiones.modulos.nodos.repositorio import RepositorioNodosMemoria
from versiones.modulos.notificaciones.fachada import ModuloNotificaciones
from versiones.modulos.notificaciones.notificador import Notificador
from versiones.modulos.reportes.fachada import ModuloReportes


class NotificadorEnLista(Notificador):
    def __init__(self):
        self.mensajes = []

    def enviar(self, mensaje):
        self.mensajes.append(mensaje)


class NotificadorQueFalla(Notificador):
    def enviar(self, mensaje):
        raise ConnectionError("servicio push no disponible")


def mensaje(hora, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0):
    return json.dumps({"nodo": "nodo1", "fecha": f"2026-10-15T{hora}:00", "temperatura": temperatura,
                       "humedad_aire": humedad_aire, "humedad_sustrato": humedad_sustrato})


def armar(notificador=None, reglas_extra=()):
    notificaciones = ModuloNotificaciones(notificador or NotificadorEnLista())
    alertas = ModuloAlertas(RepositorioAlertasMemoria(), notificaciones, [*reglas_iniciales(), *reglas_extra])
    nodos = ModuloNodos(RepositorioNodosMemoria(), notificaciones)
    lecturas = ModuloLecturas(RepositorioLecturasMemoria(), alertas, nodos)
    return lecturas, alertas, nodos


def test_1_lectura_imposible_se_descarta():
    lecturas, _, _ = armar()
    assert lecturas.registrar(mensaje("10:00", temperatura=-40.0)) is False
    assert lecturas.todas() == []


def test_2_alerta_critica_solo_despues_del_tiempo_minimo():
    _, alertas, _ = armar()
    severidades = []
    for hora in ("10:00", "10:03", "10:05"):
        lectura = Lectura.desde_dict(json.loads(mensaje(hora, temperatura=32.0)))
        severidades.append(alertas.evaluar(lectura)[0].severidad)
    assert severidades == [ADVERTENCIA, ADVERTENCIA, CRITICA]


def test_3_si_falla_el_push_la_alerta_se_guarda():
    lecturas, alertas, _ = armar(notificador=NotificadorQueFalla())
    for hora in ("10:00", "10:03", "10:05"):
        assert lecturas.registrar(mensaje(hora, temperatura=32.0)) is True
    assert CRITICA in [alerta.severidad for alerta in alertas.todas()]


def test_4_nodo_sin_datos_se_marca_desconectado():
    notificador = NotificadorEnLista()
    nodos = ModuloNodos(RepositorioNodosMemoria(), ModuloNotificaciones(notificador))
    nodos.registrar_actividad("nodo1", datetime(2026, 10, 15, 10, 0))
    assert nodos.revisar(datetime(2026, 10, 15, 10, 6)) == ["nodo1"]
    assert nodos.conectados() == []
    assert len(notificador.mensajes) == 1


def test_5_regla_nueva_sin_modificar_el_modulo_de_alertas():
    class ReglaRiesgoHongos(Regla):
        def evaluar(self, lectura):
            if lectura.humedad_aire > 85 and lectura.temperatura > 25:
                return Alerta(lectura.nodo, lectura.fecha, "humedad_aire", lectura.humedad_aire,
                              ADVERTENCIA, "riesgo de hongos")
            return None

    lecturas, alertas, _ = armar(reglas_extra=[ReglaRiesgoHongos()])
    lecturas.registrar(mensaje("10:00", temperatura=26.0, humedad_aire=90.0))
    assert any(alerta.descripcion == "riesgo de hongos" for alerta in alertas.todas())


def test_reportes_usan_solo_la_fachada_de_lecturas(tmp_path):
    lecturas, _, _ = armar()
    lecturas.registrar(mensaje("10:00", temperatura=20.0))
    lecturas.registrar(mensaje("10:01", temperatura=24.0))
    reportes = ModuloReportes(lecturas)
    assert reportes.estadisticas("temperatura")["promedio"] == 22.0
    reportes.exportar_csv(tmp_path / "reporte.csv", rol="administrador")
    assert (tmp_path / "reporte.csv").exists()


def test_ningun_modulo_importa_clases_internas_de_otro():
    """Cohesión: cada módulo solo importa de sí mismo o de la biblioteca estándar."""
    raiz = Path(__file__).resolve().parents[1]
    modulos = {"lecturas", "alertas", "notificaciones", "nodos", "reportes"}
    for modulo in modulos:
        for archivo in (raiz / modulo).glob("*.py"):
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.ImportFrom) and nodo.module:
                    partes = set(nodo.module.split("."))
                    otros = (partes & modulos) - {modulo}
                    assert not otros, f"{archivo.name} importa de {otros}"
