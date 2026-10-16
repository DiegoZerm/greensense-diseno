# Versión de puertos y adaptadores

## Enfoque

Esta versión separa el servidor en un **núcleo** y su **infraestructura**:

- El **dominio** contiene los datos y las reglas del invernadero. No importa ninguna tecnología.
- Los **puertos** son interfaces que describen lo que el núcleo necesita del exterior: guardar, notificar y conocer la hora.
- Los **casos de uso** coordinan el dominio y los puertos.
- Los **adaptadores** conectan tecnologías concretas (MQTT, SQLite, push y reloj del sistema) con los puertos.

Cambiar SQLite por PostgreSQL o el mensaje simulado por Mosquitto significa escribir un adaptador nuevo, sin tocar ninguna regla.

## Estructura

```
versiones/puertos/
├── dominio/
│   ├── modelos.py            Lectura, Alerta, Umbral
│   └── reglas.py             ValidadorLecturas, Regla, ReglaRango, PoliticaUmbrales
├── puertos.py                RepositorioLecturas, RepositorioAlertas, RepositorioNodos, Notificador, Reloj
├── aplicacion/
│   ├── registrar_lectura.py  RegistrarLectura
│   ├── revisar_nodos.py      RevisarNodos
│   └── generar_reporte.py    GenerarReporte
├── adaptadores/
│   ├── entrada_mqtt.py       AdaptadorMqtt
│   ├── sqlite.py             repositorios con SQLite
│   ├── memoria.py            repositorios en memoria y RelojFijo
│   └── push.py               NotificadorPushHttp, NotificadorConsola, RelojSistema
├── sistema.py                crear_sistema(): conecta adaptadores y núcleo
├── diagrama.md
└── tests/test_puertos.py
```

## Clases y responsabilidades

| Capa | Clase | Responsabilidad |
|---|---|---|
| Dominio | `Lectura`, `Alerta`, `Umbral` | Datos del invernadero |
| Dominio | `ValidadorLecturas` | Decidir si una lectura es físicamente posible |
| Dominio | `Regla`, `ReglaRango` | Contrato de regla y regla de rango con tiempo mínimo, una instancia por variable |
| Dominio | `PoliticaUmbrales` | Aplicar la lista de reglas a cada lectura |
| Puerto | `RepositorioLecturas`, `RepositorioAlertas`, `RepositorioNodos` | Contratos de almacenamiento |
| Puerto | `Notificador`, `Reloj` | Contratos de avisos y de tiempo |
| Aplicación | `RegistrarLectura` | Validar, guardar, evaluar, guardar alertas y notificar |
| Aplicación | `RevisarNodos` | Detectar nodos sin datos usando el reloj |
| Aplicación | `GenerarReporte` | Estadísticas y exportación CSV con control por rol |
| Adaptador | `AdaptadorMqtt` | Convertir el mensaje JSON en una `Lectura` |
| Adaptador | `Repositorio...SQLite`, `Repositorio...Memoria` | Implementar los puertos de almacenamiento |
| Adaptador | `NotificadorPushHttp`, `NotificadorConsola`, `RelojSistema`, `RelojFijo` | Implementar los puertos de avisos y tiempo |

## Aplicación de SOLID

| Principio | Cómo se aplica |
|---|---|
| **S** Responsabilidad única | Dominio, casos de uso y adaptadores cambian por razones distintas: reglas del cultivo, flujo de la aplicación y tecnología. |
| **O** Abierto/cerrado | Una regla nueva es otra implementación de `Regla`; una base de datos nueva es otro adaptador. La prueba 5 agrega la regla de riesgo de hongos sin modificar `PoliticaUmbrales`. |
| **L** Sustitución de Liskov | `test_contrato_de_repositorios` se ejecuta con los adaptadores en memoria y con los de SQLite. Ambos pasan, por lo que el núcleo puede usar cualquiera. |
| **I** Segregación de interfaces | Cada caso de uso depende solo de los puertos que usa: `RevisarNodos` no conoce `RepositorioAlertas` y `GenerarReporte` solo conoce `RepositorioLecturas`. |
| **D** Inversión de dependencias | El dominio y los casos de uso no importan `sqlite3`, `urllib` ni `json`. Reciben los puertos por el constructor y `crear_sistema()` decide qué adaptador usar. |

## Pruebas

```bash
pytest versiones/puertos
```

| Prueba | Qué demuestra |
|---|---|
| `test_1_lectura_imposible_se_descarta` | Una lectura de −40 °C no se guarda |
| `test_2_alerta_critica_solo_despues_del_tiempo_minimo` | La política de umbrales se prueba sola: advertencia a las 10:00 y 10:03, crítica a las 10:05 |
| `test_3_si_falla_el_push_la_alerta_se_guarda` | Con un notificador que falla, la alerta crítica queda guardada |
| `test_4_nodo_sin_datos_se_marca_desconectado` | Con un reloj fijo a las 10:06, el nodo queda desconectado |
| `test_5_regla_nueva_sin_modificar_la_politica` | La regla de riesgo de hongos se agrega a la lista de reglas |
| `test_contrato_de_repositorios` | Los adaptadores en memoria y SQLite son sustituibles |
| `test_adaptador_mqtt_descarta_mensajes_incompletos` | La conversión del mensaje vive en el adaptador, no en el núcleo |

## Decisiones y costos

- **Ventaja:** el núcleo se prueba completo sin infraestructura y la tecnología se puede cambiar sin tocar las reglas.
- **Ventaja:** el puerto `Reloj` permite controlar el tiempo en las pruebas, algo imposible en el original.
- **Costo:** tiene más interfaces y archivos que las otras versiones. Para un servidor de este tamaño puede parecer excesivo, pero el costo se paga una vez y facilita la migración a PostgreSQL y Mosquitto del sistema real.
- **Decisión:** la validación de campos faltantes se dejó en el adaptador MQTT, porque depende del formato del mensaje; la validación de límites físicos se dejó en el dominio, porque es una regla del invernadero.

## Diferencias con las otras versiones

- Frente a **capas**: allí los servicios dependen de repositorios, pero no hay una frontera explícita entre núcleo e infraestructura ni un puerto para el tiempo.
- Frente a **eventos**: aquí el flujo es explícito dentro de cada caso de uso; allí se reparte entre manejadores de eventos.
- Frente a **módulos**: aquí se separa por nivel (núcleo e infraestructura); allí por funcionalidad del negocio.
