"""Manejadores: cada uno reacciona a un evento y hace una sola tarea."""

import logging

from .eventos import AlertaGenerada, LecturaValidada
from .modelos import CRITICA, Lectura

registro = logging.getLogger(__name__)

CAMPOS_REQUERIDOS = ("nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato")
LIMITES_FISICOS = {"temperatura": (-10.0, 60.0), "humedad_aire": (0.0, 100.0), "humedad_sustrato": (0.0, 100.0)}


class Validador:
    """LecturaRecibida -> LecturaValidada, solo si los datos son completos y posibles."""

    def __init__(self, bus):
        self.bus = bus

    def manejar(self, evento):
        datos = evento.datos
        if any(campo not in datos for campo in CAMPOS_REQUERIDOS):
            return
        if not all(minimo <= datos[v] <= maximo for v, (minimo, maximo) in LIMITES_FISICOS.items()):
            return
        self.bus.publicar(LecturaValidada(Lectura.desde_dict(datos)))


class AlmacenLecturas:
    """LecturaValidada -> guarda la lectura y la actividad del nodo."""

    def __init__(self, repositorio_lecturas, repositorio_nodos):
        self.repositorio_lecturas = repositorio_lecturas
        self.repositorio_nodos = repositorio_nodos

    def manejar(self, evento):
        self.repositorio_lecturas.guardar(evento.lectura)
        self.repositorio_nodos.registrar_actividad(evento.lectura.nodo, evento.lectura.fecha)


class EvaluadorReglas:
    """LecturaValidada -> AlertaGenerada por cada regla que se cumple."""

    def __init__(self, bus, reglas):
        self.bus = bus
        self.reglas = list(reglas)

    def manejar(self, evento):
        for regla in self.reglas:
            alerta = regla.evaluar(evento.lectura)
            if alerta:
                self.bus.publicar(AlertaGenerada(alerta))


class RegistroAlertas:
    """AlertaGenerada -> guarda la alerta."""

    def __init__(self, repositorio_alertas):
        self.repositorio_alertas = repositorio_alertas

    def manejar(self, evento):
        self.repositorio_alertas.guardar(evento.alerta)


class DespachadorNotificaciones:
    """AlertaGenerada crítica o NodoDesconectado -> envía el aviso por cada canal.

    Si un canal falla, los demás canales envían el aviso de todos modos.
    """

    def __init__(self, canales):
        self.canales = list(canales)

    def al_generar_alerta(self, evento):
        alerta = evento.alerta
        if alerta.severidad == CRITICA:
            self._enviar(f"Alerta crítica en {alerta.nodo}: {alerta.variable} = {alerta.valor}")

    def al_desconectar_nodo(self, evento):
        self._enviar(f"El nodo {evento.nodo} dejó de enviar datos")

    def _enviar(self, mensaje):
        for canal in self.canales:
            try:
                canal.enviar(mensaje)
            except Exception:
                registro.exception("Falló el canal %s", type(canal).__name__)
