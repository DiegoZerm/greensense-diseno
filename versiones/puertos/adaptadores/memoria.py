"""Adaptadores en memoria. Sirven como dobles de prueba."""

from ..puertos import Reloj, RepositorioAlertas, RepositorioLecturas, RepositorioNodos


class RepositorioLecturasMemoria(RepositorioLecturas):
    def __init__(self):
        self._datos = []

    def guardar(self, lectura):
        self._datos.append(lectura)

    def todas(self):
        return list(self._datos)


class RepositorioAlertasMemoria(RepositorioAlertas):
    def __init__(self):
        self._datos = []

    def guardar(self, alerta):
        self._datos.append(alerta)

    def todas(self):
        return list(self._datos)


class RepositorioNodosMemoria(RepositorioNodos):
    def __init__(self):
        self._nodos = {}

    def registrar_actividad(self, nodo, fecha):
        self._nodos[nodo] = [fecha, True]

    def conectados(self):
        return [(nodo, datos[0]) for nodo, datos in self._nodos.items() if datos[1]]

    def marcar_desconectado(self, nodo):
        self._nodos[nodo][1] = False


class RelojFijo(Reloj):
    """Reloj controlado para pruebas."""

    def __init__(self, momento):
        self.momento = momento

    def ahora(self):
        return self.momento
