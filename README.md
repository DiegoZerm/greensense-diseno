# GreenSense IoT: análisis y mejora del diseño

GreenSense IoT es un sistema de monitoreo ambiental y alertas para invernaderos. Un nodo con sensores mide la temperatura, la humedad del aire y la humedad del sustrato cada 60 segundos y envía las lecturas por MQTT a un servidor. El servidor valida y guarda las lecturas, las compara con los umbrales del cultivo y envía notificaciones push cuando una variable sale del rango adecuado.

Este repositorio contiene el análisis del diseño del servidor: una versión original con todas las responsabilidades en una sola clase y cuatro versiones mejoradas que aplican los principios SOLID con enfoques distintos.

## Estructura

```
greensense-diseno/
├── docs/
│   ├── requisitos.md          requisitos funcionales y no funcionales
│   └── analisis_original.md   responsabilidades, problemas, SOLID y diagrama
├── original/
│   ├── sistema_greensense.py  diseño original
│   └── tests/
└── versiones/
    ├── README.md              enfoques y contrato común
    ├── capas/
    ├── puertos/
    ├── eventos/
    └── modulos/
```

## Diseño original

La clase `SistemaGreenSense` recibe mensajes, valida, guarda en la base de datos, evalúa umbrales, genera alertas, envía notificaciones, revisa nodos, calcula estadísticas, exporta reportes y maneja usuarios. Tiene al menos seis motivos de cambio distintos y presenta duplicación, acoplamiento con la infraestructura y un error de confiabilidad: si falla el envío push, la alerta crítica se pierde.

El análisis completo y el diagrama están en [`docs/analisis_original.md`](docs/analisis_original.md).

## Versiones mejoradas

| Versión | Enfoque | Principio que destaca |
|---|---|---|
| [`capas`](versiones/capas) | Servicios, repositorios y notificadores | Responsabilidad única |
| [`puertos`](versiones/puertos) | Núcleo de reglas aislado con puertos y adaptadores | Inversión de dependencias |
| [`eventos`](versiones/eventos) | Eventos con reglas y canales como estrategias | Abierto/cerrado |
| [`modulos`](versiones/modulos) | Módulos por funcionalidad del negocio | Alta cohesión y segregación de interfaces |

Todas cumplen el mismo contrato de alcance y pruebas, descrito en [`versiones/README.md`](versiones/README.md).

## Ejecución

Requiere Python 3.10 o posterior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

El código usa SQLite, mensajes JSON y un envío push simulado para ejecutarse sin servicios adicionales. En el sistema real se usan PostgreSQL, Mosquitto y Web Push.
