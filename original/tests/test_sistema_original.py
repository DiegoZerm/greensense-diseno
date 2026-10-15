"""Pruebas del diseño original.

Estas pruebas documentan el comportamiento actual de SistemaGreenSense,
incluidos sus problemas. Todas necesitan crear una base de datos real,
porque la clase la abre en su constructor.
"""

import json
import sqlite3

import pytest

from original.sistema_greensense import SistemaGreenSense


def mensaje(fecha, temperatura=22.0, humedad_aire=70.0, humedad_sustrato=55.0, nodo="nodo1"):
    return json.dumps({
        "nodo": nodo,
        "fecha": fecha,
        "temperatura": temperatura,
        "humedad_aire": humedad_aire,
        "humedad_sustrato": humedad_sustrato,
    })


@pytest.fixture
def sistema(tmp_path):
    return SistemaGreenSense(ruta_bd=str(tmp_path / "prueba.db"))


def contar_alertas(ruta_bd, severidad):
    conexion = sqlite3.connect(ruta_bd)
    total = conexion.execute("SELECT COUNT(*) FROM alertas WHERE severidad = ?", (severidad,)).fetchone()[0]
    conexion.close()
    return total


def test_lectura_imposible_se_descarta(sistema):
    assert sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:00:00", temperatura=-40.0)) is False


def test_alerta_critica_solo_despues_del_tiempo_minimo(sistema, tmp_path):
    sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:00:00", temperatura=32.0))
    sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:03:00", temperatura=32.0))
    assert contar_alertas(tmp_path / "prueba.db", "critica") == 0
    sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:05:00", temperatura=32.0))
    assert contar_alertas(tmp_path / "prueba.db", "critica") == 1


def test_nodo_sin_datos_se_marca_desconectado(sistema):
    from datetime import datetime

    sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:00:00"))
    assert sistema.revisar_nodos(datetime.fromisoformat("2026-10-15T10:06:00")) == ["nodo1"]


def test_si_falla_el_push_se_pierde_la_alerta(sistema, tmp_path):
    """Documenta un problema del diseño original.

    Para simular la falla hay que reemplazar un método interno de la clase,
    porque el envío push está escrito dentro de ella. La alerta se inserta,
    el push falla antes del commit y la alerta nunca se guarda.
    """
    def push_que_falla(mensaje):
        raise ConnectionError("servicio push no disponible")

    sistema.enviar_push = push_que_falla
    sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:00:00", temperatura=32.0))
    with pytest.raises(ConnectionError):
        sistema.procesar_mensaje_mqtt(mensaje("2026-10-15T10:05:00", temperatura=32.0))
    assert contar_alertas(tmp_path / "prueba.db", "critica") == 0
