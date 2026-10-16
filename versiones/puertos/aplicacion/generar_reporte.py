"""Caso de uso: estadísticas y exportación de lecturas."""

import csv

from ..dominio.modelos import VARIABLES

ROLES_CON_EXPORTACION = ("supervisor", "administrador")


class GenerarReporte:
    def __init__(self, lecturas):
        self.lecturas = lecturas

    def estadisticas(self, variable):
        if variable not in VARIABLES:
            raise ValueError(f"Variable desconocida: {variable}")
        valores = [lectura.valor(variable) for lectura in self.lecturas.todas()]
        if not valores:
            return None
        return {"minimo": min(valores), "maximo": max(valores), "promedio": sum(valores) / len(valores)}

    def exportar_csv(self, ruta, rol):
        if rol not in ROLES_CON_EXPORTACION:
            raise PermissionError("El rol no puede exportar reportes")
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nodo", "fecha", *VARIABLES])
            for lectura in self.lecturas.todas():
                escritor.writerow([lectura.nodo, lectura.fecha.isoformat(), *(lectura.valor(v) for v in VARIABLES)])
