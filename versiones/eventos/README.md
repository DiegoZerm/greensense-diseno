# Versión de eventos y estrategias

## Enfoque

Esta versión organiza el servidor alrededor de **eventos**. Cuando llega un mensaje se publica `LecturaRecibida` y cada componente interesado reacciona sin conocer a los demás (patrón **Observer**). Las reglas de umbral y los canales de notificación son **estrategias** intercambiables (patrón **Strategy**).

El flujo queda así: `LecturaRecibida` → `Validador` → `LecturaValidada` → `AlmacenLecturas` y `EvaluadorReglas` → `AlertaGenerada` → `RegistroAlertas` y `DespachadorNotificaciones`.

## Estructura

```
versiones/eventos/
├── modelos.py        Lectura, Alerta, Umbral
├── eventos.py        LecturaRecibida, LecturaValidada, AlertaGenerada, NodoDesconectado
├── bus.py            BusEventos
├── reglas.py         ReglaUmbral, ReglaRango
├── canales.py        CanalNotificacion, CanalPush, CanalConsola
├── manejadores.py    Validador, AlmacenLecturas, EvaluadorReglas, RegistroAlertas, DespachadorNotificaciones
├── nodos.py          MonitorNodos
├── repositorios.py   interfaces, memoria y SQLite
├── reportes.py       ServicioReportes
├── sistema.py        conectar() y crear_sistema(): registran las suscripciones
├── diagrama.md
└── tests/test_eventos.py
```

## Clases y responsabilidades

| Clase | Responsabilidad |
|---|---|
| `BusEventos` | Entregar cada evento a sus suscriptores y aislar las fallas de cada uno |
| `LecturaRecibida`, `LecturaValidada`, `AlertaGenerada`, `NodoDesconectado` | Describir lo que ocurrió |
| `Validador` | Publicar `LecturaValidada` solo si los datos son completos y posibles |
| `AlmacenLecturas` | Guardar la lectura y la actividad del nodo |
| `EvaluadorReglas` | Aplicar cada `ReglaUmbral` y publicar las alertas |
| `RegistroAlertas` | Guardar las alertas |
| `DespachadorNotificaciones` | Enviar avisos por cada canal; si un canal falla, los demás siguen |
| `ReglaUmbral`, `ReglaRango` | Estrategia de regla y regla de rango con tiempo mínimo |
| `CanalNotificacion`, `CanalPush`, `CanalConsola` | Estrategia de canal y sus implementaciones |
| `MonitorNodos` | Publicar `NodoDesconectado` cuando un nodo deja de enviar datos |
| `ServicioReportes` | Estadísticas y exportación CSV con control por rol |
| `conectar()` | Único lugar donde se decide quién escucha cada evento |

## Aplicación de SOLID

| Principio | Cómo se aplica |
|---|---|
| **S** Responsabilidad única | Cada manejador reacciona a un evento y hace una sola tarea: guardar, evaluar, registrar o avisar. |
| **O** Abierto/cerrado | Una regla nueva es otra `ReglaUmbral` y un canal nuevo es otro `CanalNotificacion`; se registran en `conectar()` y ningún manejador cambia. Las pruebas agregan la regla de riesgo de hongos y un segundo canal sin modificar código existente. |
| **L** Sustitución de Liskov | Toda `ReglaUmbral` devuelve una alerta o `None` y todo `CanalNotificacion` solo envía; el evaluador y el despachador tratan igual a cualquier implementación. |
| **I** Segregación de interfaces | `ReglaUmbral` y `CanalNotificacion` tienen un solo método cada una; cada manejador recibe solo el repositorio que usa. |
| **D** Inversión de dependencias | Los manejadores dependen del bus y de interfaces. Las clases concretas se eligen en `crear_sistema()`. |

## Pruebas

```bash
pytest versiones/eventos
```

| Prueba | Qué demuestra |
|---|---|
| `test_1_lectura_imposible_se_descarta` | Con −40 °C no se publica `LecturaValidada` y no se guarda nada |
| `test_2_alerta_critica_solo_despues_del_tiempo_minimo` | La estrategia `ReglaRango` se prueba sola |
| `test_3_si_falla_el_push_la_alerta_se_guarda` | `RegistroAlertas` guarda la alerta aunque el canal falle |
| `test_4_nodo_sin_datos_se_marca_desconectado` | `MonitorNodos` publica `NodoDesconectado` a las 10:06 |
| `test_5_regla_nueva_sin_modificar_el_evaluador` | La regla de riesgo de hongos se registra como estrategia nueva |
| `test_un_canal_que_falla_no_bloquea_a_los_demas` | Un segundo canal recibe el aviso aunque el primero falle |
| `test_el_bus_continua_si_un_manejador_falla` | Una falla en un suscriptor no detiene a los demás |
| `test_flujo_completo_desde_el_mensaje` | El sistema armado procesa mensajes JSON de principio a fin |

## Decisiones y costos

- **Ventaja:** es la versión más fácil de extender. Las variaciones más probables del proyecto (reglas agronómicas y canales de aviso) se agregan sin modificar código probado.
- **Ventaja:** las fallas quedan aisladas en dos niveles: el bus aísla manejadores y el despachador aísla canales.
- **Costo:** el flujo es menos evidente al leer el código, porque ningún método llama a todos los pasos en orden. Por eso el diagrama de secuencia es parte de la documentación.
- **Costo:** el orden de las suscripciones importa. `conectar()` registra el almacenamiento antes que el evaluador para que la lectura quede guardada antes de generar alertas.

## Diferencias con las otras versiones

- Frente a **capas** y **puertos**: allí un servicio o caso de uso llama a los demás en orden; aquí nadie llama a nadie directamente, todo pasa por el bus.
- Frente a **módulos**: allí los módulos se llaman a través de fachadas; aquí se comunican por eventos.
