"""Validación de los datos que llegan de los nodos."""

CAMPOS_REQUERIDOS = ("nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato")

LIMITES_FISICOS = {
    "temperatura": (-10.0, 60.0),
    "humedad_aire": (0.0, 100.0),
    "humedad_sustrato": (0.0, 100.0),
}


class ValidadorLecturas:
    """Decide si un mensaje contiene una lectura completa y físicamente posible."""

    def __init__(self, limites=None):
        self.limites = limites or LIMITES_FISICOS

    def es_valida(self, datos):
        if any(campo not in datos for campo in CAMPOS_REQUERIDOS):
            return False
        for variable, (minimo, maximo) in self.limites.items():
            if not minimo <= datos[variable] <= maximo:
                return False
        return True
