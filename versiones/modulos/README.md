# Versión de módulos por funcionalidad

## Enfoque

Esta versión organiza el servidor por funcionalidad del negocio: lecturas, alertas, notificaciones, nodos y reportes. Cada módulo contiene su propio modelo, reglas y repositorio, y expone hacia fuera una sola clase, su fachada. Los módulos se comunican únicamente a través de esas fachadas.

## Estructura

versiones/modulos/
├── lecturas/
│   ├── modelo.py        Lectura
│   ├── validador.py     ValidadorLecturas
│   ├── repositorio.py   interfaz, memoria y SQLite
│   └── fachada.py       ModuloLecturas
├── alertas/
│   ├── modelo.py        Alerta, Umbral
│   ├── reglas.py        Regla, ReglaRango
│   ├── repositorio.py   interfaz, memoria y SQLite
│   └── fachada.py       ModuloAlertas
├── notificaciones/
│   ├── notificador.py   Notificador, NotificadorPush, NotificadorConsola
│   └── fachada.py       ModuloNotificaciones
├── nodos/
│   ├── repositorio.py   interfaz, memoria y SQLite
│   └── fachada.py       ModuloNodos
├── reportes/
│   └── fachada.py       ModuloReportes
├── sistema.py           crear_sistema(): conecta las fachadas
├── diagrama.md
└── tests/test_modulos.py

## Clases y responsabilidades

| Módulo | Fachada | Responsabilidad |
|---|---|---|
| Lecturas | ModuloLecturas | Validar el mensaje, guardar la lectura y entregarla a alertas y nodos |
| Alertas | ModuloAlertas | Aplicar las reglas, guardar las alertas y pedir el aviso de las críticas |
| Notificaciones | ModuloNotificaciones | Enviar avisos; si el canal falla, registra el error sin propagarlo |
| Nodos | ModuloNodos | Registrar actividad y detectar nodos desconectados |
| Reportes | ModuloReportes | Estadísticas y exportación CSV con control por rol, leyendo solo la fachada de lecturas |

Las clases internas (modelos, validador, reglas y repositorios) solo se usan dentro de su módulo.

## Aplicación de SOLID

| Principio | Cómo se aplica |
|---|---|
| S Responsabilidad única | Cada módulo cambia por una sola área del negocio. Si cambian las reglas agronómicas, solo cambia alertas; si cambia el canal de aviso, solo notificaciones. |
| O Abierto/cerrado | Una regla nueva es otra implementación de Regla y se entrega al crear ModuloAlertas. La prueba 5 agrega la regla de riesgo de hongos sin modificar la fachada. |
| L Sustitución de Liskov | Las implementaciones en memoria y SQLite de cada repositorio son intercambiables dentro de su módulo; las pruebas usan las de memoria y el sistema las de SQLite. |
| I Segregación de interfaces | Cada fachada expone solo lo que otros módulos necesitan. ModuloReportes conoce todas() de lecturas, pero no cómo se validan ni cómo se evalúan alertas. |
| D Inversión de dependencias | Las fachadas reciben por el constructor los repositorios y las fachadas de otros módulos; crear_sistema() decide las implementaciones concretas. |

## Pruebas

Comando para ejecutar las pruebas: pytest versiones/modulos

| Prueba | Qué demuestra |
|---|---|
| test_1_lectura_imposible_se_descarta | Con −40 °C la lectura no se guarda |
| test_2_alerta_critica_solo_despues_del_tiempo_minimo | El módulo de alertas se prueba solo |
| test_3_si_falla_el_push_la_alerta_se_guarda | El módulo de notificaciones absorbe la falla y la alerta queda guardada |
| test_4_nodo_sin_datos_se_marca_desconectado | El módulo de nodos detecta la desconexión y avisa |
| test_5_regla_nueva_sin_modificar_el_modulo_de_alertas | La regla de riesgo de hongos se agrega al crear el módulo |
| test_reportes_usan_solo_la_fachada_de_lecturas | Reportes funciona sin conocer el interior de lecturas |
| test_ningun_modulo_importa_clases_internas_de_otro | Revisa el código y comprueba que ningún módulo importa clases internas de otro |

## Decisiones y costos

- Ventaja: todo lo de una funcionalidad está en un solo lugar. Para cambiar las alertas se abre una sola carpeta.
- Ventaja: la frontera entre módulos se verifica con una prueba automática, no solo por convención.
- Costo: algunos elementos pequeños se repiten entre módulos, como la lista de variables en lecturas y en reportes. Se aceptó para que ningún módulo dependa del interior de otro.
- Costo: el orden de creación importa: notificaciones antes que alertas y nodos, y estos antes que lecturas.

## Diferencias con las otras versiones

- Frente a capas: las responsabilidades son similares, pero aquí se agrupan por funcionalidad y no por tipo técnico. Para agregar la variable luminosidad se modifican los módulos lecturas, alertas y reportes, y cada cambio queda dentro de su área; en capas, los cambios caen en archivos técnicos (modelos, validación y repositorios).
- Frente a puertos: allí se separa por nivel (núcleo e infraestructura); aquí por área del negocio.
- Frente a eventos: aquí los módulos se llaman entre sí a través de fachadas; allí se comunican por eventos.
