# Versión de capas

## Enfoque

Esta versión reorganiza el servidor de GreenSense por **tipo técnico**, siguiendo el esquema de servicios y repositorios:

- **Servicios** que coordinan el flujo: `ServicioLecturas`, `ServicioAlertas` y `ServicioReportes`.
- **Clases de reglas** que toman decisiones: `ValidadorLecturas` y `EvaluadorUmbrales`.
- **Repositorios** que guardan datos, definidos como interfaces con una versión en SQLite y otra en memoria.
- **Notificadores** que envían avisos, también detrás de una interfaz.

Es la mejora más directa respecto al diseño original: cada motivo de cambio que estaba mezclado en `SistemaGreenSense` pasa a su propia clase, sin agregar mecanismos adicionales.

## Estructura

```
versiones/capas/
├── modelos.py          Lectura, Alerta, Umbral y valores iniciales
├── validacion.py       ValidadorLecturas
├── evaluacion.py       EvaluadorUmbrales y la interfaz ReglaAdicional
├── servicios.py        ServicioLecturas, ServicioAlertas, ServicioReportes
├── repositorios.py     interfaces e implementaciones SQLite y en memoria
├── notificaciones.py   Notificador, NotificadorPush, NotificadorConsola
├── nodos.py            MonitorNodos
├── sistema.py          crear_sistema(): único lugar con clases concretas
├── diagrama.md         diagrama de clases y de secuencia
└── tests/test_capas.py
```

## Clases y responsabilidades

| Clase | Responsabilidad | Motivo de cambio |
|---|---|---|
| `Lectura`, `Alerta`, `Umbral` | Representar los datos del invernadero | Cambio en los datos que se miden |
| `ValidadorLecturas` | Decidir si un mensaje está completo y es físicamente posible | Cambio en los límites físicos |
| `EvaluadorUmbrales` | Decidir advertencia o crítica, con tiempo mínimo, para cualquier variable | Cambio en las reglas del cultivo |
| `ReglaAdicional` | Contrato para reglas extra | Nuevas reglas agronómicas |
| `ServicioLecturas` | Coordinar validar, guardar, evaluar y entregar alertas | Cambio en el flujo de recepción |
| `ServicioAlertas` | Guardar alertas y notificar las críticas | Cambio en el manejo de alertas |
| `ServicioReportes` | Estadísticas y exportación a CSV con control por rol | Cambio en los reportes |
| `MonitorNodos` | Detectar nodos sin datos y avisar | Cambio en la política de conexión |
| `RepositorioLecturas`, `RepositorioAlertas`, `RepositorioNodos` | Contratos de almacenamiento | Cambio en lo que se necesita guardar |
| `Repositorio...SQLite`, `Repositorio...Memoria` | Implementaciones de almacenamiento | Cambio de motor de base de datos |
| `Notificador`, `NotificadorPush`, `NotificadorConsola` | Contrato e implementaciones de avisos | Cambio de canal o proveedor |
| `crear_sistema()` | Elegir y conectar las implementaciones concretas | Cambio de configuración |

## Aplicación de SOLID

| Principio | Cómo se aplica |
|---|---|
| **S** Responsabilidad única | Cada clase tiene un motivo de cambio. `EvaluadorUmbrales` cambia solo si cambian las reglas; `RepositorioLecturasSQLite`, solo si cambia la base de datos. |
| **O** Abierto/cerrado | Una regla nueva se agrega como implementación de `ReglaAdicional` y se pasa al evaluador al crearlo. La prueba 5 agrega la regla de riesgo de hongos sin modificar `EvaluadorUmbrales`. |
| **L** Sustitución de Liskov | `RepositorioLecturasSQLite` y `RepositorioLecturasMemoria` cumplen el mismo contrato. La prueba `test_contrato_repositorio_de_lecturas` se ejecuta con las dos implementaciones y ambas pasan. |
| **I** Segregación de interfaces | En lugar de un repositorio general hay tres interfaces pequeñas. `MonitorNodos` solo conoce `RepositorioNodos` y `ServicioReportes` solo `RepositorioLecturas`. |
| **D** Inversión de dependencias | Los servicios reciben repositorios y notificador por el constructor y dependen de las interfaces. Solo `crear_sistema()` importa las clases concretas. |

## Pruebas

```bash
pytest versiones/capas
```

| Prueba | Qué demuestra |
|---|---|
| `test_1_lectura_imposible_se_descarta` | Una lectura de −40 °C no se guarda |
| `test_2_alerta_critica_solo_despues_del_tiempo_minimo` | Advertencia a las 10:00 y 10:03; crítica a las 10:05. El evaluador se prueba solo, sin base de datos |
| `test_3_si_falla_el_push_la_alerta_se_guarda` | Con un notificador que falla, la alerta crítica queda guardada y el proceso continúa |
| `test_4_nodo_sin_datos_se_marca_desconectado` | Un nodo sin datos durante 6 minutos queda desconectado y se envía un aviso |
| `test_5_regla_nueva_sin_modificar_el_evaluador` | La regla de riesgo de hongos se agrega sin tocar el evaluador |
| `test_contrato_repositorio_de_lecturas` | Las implementaciones SQLite y en memoria son sustituibles |
| `test_reportes_por_variable_y_permiso_de_exportacion` | Estadísticas genéricas y exportación restringida por rol |

Ninguna prueba usa base de datos en archivo, broker ni servicio push.

## Mejoras concretas respecto al original

| Problema del original | Solución en esta versión |
|---|---|
| El bloque de umbrales se repetía tres veces | Un solo método genérico, `_evaluar_variable`, recorre las variables |
| La consulta de estadísticas se repetía tres veces | `ServicioReportes.estadisticas` funciona para cualquier variable |
| Si fallaba el push se perdía la alerta crítica | `ServicioAlertas` guarda primero y el error del aviso se registra sin detener el proceso |
| La clase abría la base de datos en su constructor | La conexión se crea en `crear_sistema()` y se entrega a los repositorios |
| La bandera `MODO_PRUEBA` mezclaba pruebas con producción | Las pruebas usan dobles de prueba; el código de producción no sabe que existen |
| Las reglas no se podían probar sin base de datos | El evaluador y el validador se prueban de forma aislada |

## Decisiones y costos

- **Ventaja:** es la versión más fácil de leer y de explicar. Cada archivo corresponde a un tipo de responsabilidad y el flujo se sigue de forma lineal desde `ServicioLecturas`.
- **Costo:** los archivos se agrupan por tipo técnico. Para agregar una variable como la luminosidad hay que tocar `modelos.py`, `validacion.py` y el esquema de `repositorios.py`, que están en archivos distintos.
- **Costo:** las reglas extra se resuelven con una lista sencilla dentro del evaluador. Si el número de reglas o de canales creciera mucho, un enfoque basado en eventos lo organizaría mejor.
- **Decisión:** no se crearon interfaces para el validador ni para el evaluador, porque no hay una variación probable que lo justifique. Se evitó crear abstracciones sin necesidad.

## Diagramas

Ver [`diagrama.md`](diagrama.md).
