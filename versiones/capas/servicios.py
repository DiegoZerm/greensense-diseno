"""Servicios que coordinan el flujo del servidor."""

import csv
import json
import logging

from .modelos import CRITICA, VARIABLES, Lectura

registro = logging.getLogger(__name__)


class ServicioAlertas:
    """Guarda las alertas y notifica las críticas.

    La alerta se guarda antes de intentar el aviso, de modo que una falla en
    el canal de notificación no provoca su pérdida.
    """

    def __init__(self, repositorio_alertas, notificador):
        self.repositorio_alertas = repositorio_alertas
        self.notificador = notificador

    def registrar(self, alertas):
        for alerta in alertas:
            self.repositorio_alertas.guardar(alerta)
            if alerta.severidad == CRITICA:
                self._avisar(f"Alerta crítica en {alerta.nodo}: {alerta.variable} = {alerta.valor}")

    def _avisar(self, mensaje):
        try:
            self.notificador.enviar(mensaje)
        except Exception:
            registro.exception("No se pudo enviar la notificación de la alerta")


class ServicioLecturas:
    """Recibe un mensaje, lo valida, lo guarda y entrega las alertas."""

    def __init__(self, validador, repositorio_lecturas, repositorio_nodos, evaluador, servicio_alertas):
        self.validador = validador
        self.repositorio_lecturas = repositorio_lecturas
        self.repositorio_nodos = repositorio_nodos
        self.evaluador = evaluador
        self.servicio_alertas = servicio_alertas

    def procesar_mensaje(self, mensaje):
        datos = json.loads(mensaje)
        if not self.validador.es_valida(datos):
            return False
        lectura = Lectura.desde_dict(datos)
        self.repositorio_lecturas.guardar(lectura)
        self.repositorio_nodos.registrar_actividad(lectura.nodo, lectura.fecha)
        self.servicio_alertas.registrar(self.evaluador.evaluar(lectura))
        return True


class ServicioReportes:
    """Estadísticas y exportación de lecturas."""

    ROLES_CON_EXPORTACION = ("supervisor", "administrador")

    def __init__(self, repositorio_lecturas):
        self.repositorio_lecturas = repositorio_lecturas

    def estadisticas(self, variable):
        if variable not in VARIABLES:
            raise ValueError(f"Variable desconocida: {variable}")
        valores = [lectura.valor(variable) for lectura in self.repositorio_lecturas.todas()]
        if not valores:
            return None
        return {"minimo": min(valores), "maximo": max(valores), "promedio": sum(valores) / len(valores)}

    def exportar_csv(self, ruta, rol):
        if rol not in self.ROLES_CON_EXPORTACION:
            raise PermissionError("El rol no puede exportar reportes")
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nodo", "fecha", *VARIABLES])
            for lectura in self.repositorio_lecturas.todas():
                escritor.writerow([lectura.nodo, lectura.fecha.isoformat(),
                                   *(lectura.valor(v) for v in VARIABLES)])
