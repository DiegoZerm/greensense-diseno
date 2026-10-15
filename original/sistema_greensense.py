"""Primera versión del servidor de GreenSense IoT.

Prototipo inicial: toda la lógica del servidor está en una sola clase.
Este archivo es el punto de partida del análisis de diseño; sus problemas
se describen en docs/analisis_original.md.
"""

import csv
import hashlib
import json
import sqlite3
import urllib.request
from datetime import datetime, timedelta


class SistemaGreenSense:
    # En el prototipo, MODO_PRUEBA evita enviar notificaciones reales.
    MODO_PRUEBA = True
    URL_PUSH = "https://push.greensense.local/enviar"

    def __init__(self, ruta_bd="greensense.db"):
        self.conexion = sqlite3.connect(ruta_bd)
        self.conexion.row_factory = sqlite3.Row
        self.umbrales = {
            "temperatura": {"min": 18.0, "max": 28.0, "margen": 2.0},
            "humedad_aire": {"min": 60.0, "max": 80.0, "margen": 5.0},
            "humedad_sustrato": {"min": 45.0, "max": 70.0, "margen": 5.0},
        }
        self.tiempo_minimo_critico = timedelta(minutes=5)
        self.tiempo_desconexion = timedelta(minutes=5)
        self.fuera_de_rango_desde = {}
        self.usuario_actual = None
        self._crear_tablas()

    def _crear_tablas(self):
        cursor = self.conexion.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS lecturas (id INTEGER PRIMARY KEY, nodo TEXT, "
            "fecha TEXT, temperatura REAL, humedad_aire REAL, humedad_sustrato REAL)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY, nodo TEXT, "
            "fecha TEXT, variable TEXT, valor REAL, severidad TEXT, atendida INTEGER DEFAULT 0)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS nodos (nodo TEXT PRIMARY KEY, ultima_lectura TEXT, "
            "conectado INTEGER DEFAULT 1)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, contrasena TEXT, rol TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS bitacora (id INTEGER PRIMARY KEY, correo TEXT, "
            "accion TEXT, fecha TEXT)"
        )
        self.conexion.commit()

    # ------------------------------------------------------------------
    # Recepción de mensajes MQTT
    # ------------------------------------------------------------------
    def procesar_mensaje_mqtt(self, payload):
        datos = json.loads(payload)
        if not self.validar_lectura(datos):
            print("Lectura descartada:", datos)
            return False
        self.guardar_lectura(datos)
        self.evaluar_umbrales(datos)
        return True

    def validar_lectura(self, datos):
        campos = ["nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato"]
        for campo in campos:
            if campo not in datos:
                return False
        if datos["temperatura"] < -10 or datos["temperatura"] > 60:
            return False
        if datos["humedad_aire"] < 0 or datos["humedad_aire"] > 100:
            return False
        if datos["humedad_sustrato"] < 0 or datos["humedad_sustrato"] > 100:
            return False
        return True

    # ------------------------------------------------------------------
    # Base de datos
    # ------------------------------------------------------------------
    def guardar_lectura(self, datos):
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO lecturas (nodo, fecha, temperatura, humedad_aire, humedad_sustrato) "
            "VALUES (?, ?, ?, ?, ?)",
            (datos["nodo"], datos["fecha"], datos["temperatura"],
             datos["humedad_aire"], datos["humedad_sustrato"]),
        )
        cursor.execute(
            "INSERT OR REPLACE INTO nodos (nodo, ultima_lectura, conectado) VALUES (?, ?, 1)",
            (datos["nodo"], datos["fecha"]),
        )
        self.conexion.commit()

    # ------------------------------------------------------------------
    # Reglas de umbral
    # ------------------------------------------------------------------
    def evaluar_umbrales(self, datos):
        fecha = datetime.fromisoformat(datos["fecha"])
        nodo = datos["nodo"]

        temperatura = datos["temperatura"]
        u = self.umbrales["temperatura"]
        clave = nodo + ":temperatura"
        if temperatura < u["min"] or temperatura > u["max"]:
            if clave not in self.fuera_de_rango_desde:
                self.fuera_de_rango_desde[clave] = fecha
            if fecha - self.fuera_de_rango_desde[clave] >= self.tiempo_minimo_critico:
                self.crear_alerta(nodo, datos["fecha"], "temperatura", temperatura, "critica")
            else:
                self.crear_alerta(nodo, datos["fecha"], "temperatura", temperatura, "advertencia")
        elif temperatura < u["min"] + u["margen"] or temperatura > u["max"] - u["margen"]:
            self.fuera_de_rango_desde.pop(clave, None)
            self.crear_alerta(nodo, datos["fecha"], "temperatura", temperatura, "advertencia")
        else:
            self.fuera_de_rango_desde.pop(clave, None)

        humedad_aire = datos["humedad_aire"]
        u = self.umbrales["humedad_aire"]
        clave = nodo + ":humedad_aire"
        if humedad_aire < u["min"] or humedad_aire > u["max"]:
            if clave not in self.fuera_de_rango_desde:
                self.fuera_de_rango_desde[clave] = fecha
            if fecha - self.fuera_de_rango_desde[clave] >= self.tiempo_minimo_critico:
                self.crear_alerta(nodo, datos["fecha"], "humedad_aire", humedad_aire, "critica")
            else:
                self.crear_alerta(nodo, datos["fecha"], "humedad_aire", humedad_aire, "advertencia")
        elif humedad_aire < u["min"] + u["margen"] or humedad_aire > u["max"] - u["margen"]:
            self.fuera_de_rango_desde.pop(clave, None)
            self.crear_alerta(nodo, datos["fecha"], "humedad_aire", humedad_aire, "advertencia")
        else:
            self.fuera_de_rango_desde.pop(clave, None)

        humedad_sustrato = datos["humedad_sustrato"]
        u = self.umbrales["humedad_sustrato"]
        clave = nodo + ":humedad_sustrato"
        if humedad_sustrato < u["min"] or humedad_sustrato > u["max"]:
            if clave not in self.fuera_de_rango_desde:
                self.fuera_de_rango_desde[clave] = fecha
            if fecha - self.fuera_de_rango_desde[clave] >= self.tiempo_minimo_critico:
                self.crear_alerta(nodo, datos["fecha"], "humedad_sustrato", humedad_sustrato, "critica")
            else:
                self.crear_alerta(nodo, datos["fecha"], "humedad_sustrato", humedad_sustrato, "advertencia")
        elif humedad_sustrato < u["min"] + u["margen"] or humedad_sustrato > u["max"] - u["margen"]:
            self.fuera_de_rango_desde.pop(clave, None)
            self.crear_alerta(nodo, datos["fecha"], "humedad_sustrato", humedad_sustrato, "advertencia")
        else:
            self.fuera_de_rango_desde.pop(clave, None)

    # ------------------------------------------------------------------
    # Alertas y notificaciones
    # ------------------------------------------------------------------
    def crear_alerta(self, nodo, fecha, variable, valor, severidad):
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO alertas (nodo, fecha, variable, valor, severidad) VALUES (?, ?, ?, ?, ?)",
            (nodo, fecha, variable, valor, severidad),
        )
        if severidad == "critica":
            self.enviar_push(f"Alerta crítica en {nodo}: {variable} = {valor}")
        self.conexion.commit()

    def enviar_push(self, mensaje):
        if self.MODO_PRUEBA:
            print("[PUSH]", mensaje)
            return
        cuerpo = json.dumps({"mensaje": mensaje}).encode("utf-8")
        peticion = urllib.request.Request(
            self.URL_PUSH, data=cuerpo, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(peticion, timeout=5)

    # ------------------------------------------------------------------
    # Estado de los nodos
    # ------------------------------------------------------------------
    def revisar_nodos(self, ahora):
        cursor = self.conexion.cursor()
        desconectados = []
        for fila in cursor.execute("SELECT nodo, ultima_lectura, conectado FROM nodos").fetchall():
            ultima = datetime.fromisoformat(fila["ultima_lectura"])
            if ahora - ultima >= self.tiempo_desconexion and fila["conectado"]:
                cursor.execute("UPDATE nodos SET conectado = 0 WHERE nodo = ?", (fila["nodo"],))
                desconectados.append(fila["nodo"])
                self.enviar_push(f"El nodo {fila['nodo']} dejó de enviar datos")
        self.conexion.commit()
        return desconectados

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def calcular_estadisticas(self, variable):
        cursor = self.conexion.cursor()
        if variable == "temperatura":
            fila = cursor.execute(
                "SELECT MIN(temperatura) AS minimo, MAX(temperatura) AS maximo, "
                "AVG(temperatura) AS promedio FROM lecturas"
            ).fetchone()
        elif variable == "humedad_aire":
            fila = cursor.execute(
                "SELECT MIN(humedad_aire) AS minimo, MAX(humedad_aire) AS maximo, "
                "AVG(humedad_aire) AS promedio FROM lecturas"
            ).fetchone()
        elif variable == "humedad_sustrato":
            fila = cursor.execute(
                "SELECT MIN(humedad_sustrato) AS minimo, MAX(humedad_sustrato) AS maximo, "
                "AVG(humedad_sustrato) AS promedio FROM lecturas"
            ).fetchone()
        else:
            return None
        return dict(fila)

    def exportar_csv(self, ruta):
        if self.usuario_actual is None or self.usuario_actual["rol"] not in ("supervisor", "administrador"):
            raise PermissionError("El usuario no puede exportar reportes")
        cursor = self.conexion.cursor()
        filas = cursor.execute(
            "SELECT nodo, fecha, temperatura, humedad_aire, humedad_sustrato FROM lecturas"
        ).fetchall()
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nodo", "fecha", "temperatura", "humedad_aire", "humedad_sustrato"])
            for fila in filas:
                escritor.writerow(list(fila))
        self.registrar_bitacora(self.usuario_actual["correo"], "exportar_csv")

    # ------------------------------------------------------------------
    # Usuarios y bitácora
    # ------------------------------------------------------------------
    def registrar_usuario(self, correo, contrasena, rol):
        cifrada = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        cursor = self.conexion.cursor()
        cursor.execute("INSERT INTO usuarios (correo, contrasena, rol) VALUES (?, ?, ?)", (correo, cifrada, rol))
        self.conexion.commit()

    def autenticar_usuario(self, correo, contrasena):
        cifrada = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        cursor = self.conexion.cursor()
        fila = cursor.execute(
            "SELECT correo, rol FROM usuarios WHERE correo = ? AND contrasena = ?", (correo, cifrada)
        ).fetchone()
        if fila is None:
            return False
        self.usuario_actual = dict(fila)
        self.registrar_bitacora(correo, "inicio_sesion")
        return True

    def registrar_bitacora(self, correo, accion):
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO bitacora (correo, accion, fecha) VALUES (?, ?, ?)",
            (correo, accion, datetime.now().isoformat()),
        )
        self.conexion.commit()
