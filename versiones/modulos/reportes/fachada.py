"""Fachada del módulo de reportes. Lee las lecturas solo a través de su fachada."""

import csv

VARIABLES = ("temperatura", "humedad_aire", "humedad_sustrato")
ROLES_CON_EXPORTACION = ("supervisor", "administrador")


class ModuloReportes:
def __init__(self, lecturas):
    self._lecturas = lecturas

def estadisticas(self, variable):
    if variable not in VARIABLES:
        raise ValueError(f"Variable desconocida: {variable}")
    valores = [lectura.valor(variable) for lectura in self._lecturas.todas()]
    if not valores:
        return None
    return {"minimo": min(valores), "maximo": max(valores), "promedio": sum(valores) / len(valores)}

def exportar_csv(self, ruta, rol):
    if rol not in ROLES_CON_EXPORTACION:
        raise PermissionError("El rol no puede exportar reportes")
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["nodo", "fecha", *VARIABLES])
        for lectura in self._lecturas.todas():
            escritor.writerow([lectura.nodo, lectura.fecha.isoformat(), *(lectura.valor(v) for v in VARIABLES)])
