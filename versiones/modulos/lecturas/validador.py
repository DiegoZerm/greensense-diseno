"""Validación interna del módulo de lecturas."""

CAMPOS_REQUERIDOS = ("nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato")
LIMITES_FISICOS = {"temperatura": (-10.0, 60.0), "humedad_aire": (0.0, 100.0), "humedad_sustrato": (0.0, 100.0)}


class ValidadorLecturas:
def es_valida(self, datos):
    if any(campo not in datos for campo in CAMPOS_REQUERIDOS):
        return False
    return all(minimo <= datos[v] <= maximo for v, (minimo, maximo) in LIMITES_FISICOS.items())
