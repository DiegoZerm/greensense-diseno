"""Puertos de salida: lo que el núcleo necesita del exterior.

El núcleo solo conoce estas interfaces. Las tecnologías concretas viven en
la carpeta adaptadores.
"""

from abc import ABC, abstractmethod


class RepositorioLecturas(ABC):
    @abstractmethod
    def guardar(self, lectura): ...

    @abstractmethod
    def todas(self): ...


class RepositorioAlertas(ABC):
    @abstractmethod
    def guardar(self, alerta): ...

    @abstractmethod
    def todas(self): ...


class RepositorioNodos(ABC):
    @abstractmethod
    def registrar_actividad(self, nodo, fecha): ...

    @abstractmethod
    def conectados(self):
        """Devuelve pares (nodo, fecha de la última lectura)."""

    @abstractmethod
    def marcar_desconectado(self, nodo): ...


class Notificador(ABC):
    @abstractmethod
    def enviar(self, mensaje): ...


class Reloj(ABC):
    @abstractmethod
    def ahora(self): ...
