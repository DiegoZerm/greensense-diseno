# Versiones mejoradas

Cada integrante desarrolla una versión distinta del servidor a partir del diseño original. Todas aplican los principios SOLID, pero organizan las clases de forma diferente.

| Carpeta | Rama | Enfoque | Organización de las clases |
|---|---|---|---|
| `capas/` | `feature/version-capas` | Capas | Por tipo técnico: servicios, repositorios y notificadores |
| `puertos/` | `feature/version-puertos` | Puertos y adaptadores | Un núcleo de reglas aislado; la infraestructura se conecta mediante interfaces |
| `eventos/` | `feature/version-eventos` | Eventos y estrategias | Componentes que reaccionan a eventos; reglas y canales como estrategias intercambiables |
| `modulos/` | `feature/version-modulos` | Módulos por funcionalidad | Por funcionalidad del negocio: lecturas, alertas, nodos, usuarios y reportes |

## Contrato común

Para que las versiones se puedan comparar, todas deben cumplir lo siguiente.

### Alcance

Cada versión implementa los requisitos RF1 a RF10 de [`docs/requisitos.md`](../docs/requisitos.md). Los requisitos de usuarios y bitácora (RF11 y RF12) son opcionales.

### Valores de referencia

Se usan los mismos umbrales, márgenes, límites físicos y tiempos del diseño original, descritos en [`docs/requisitos.md`](../docs/requisitos.md).

### Formato del mensaje

```json
{
  "nodo": "nodo1",
  "fecha": "2026-10-15T10:00:00",
  "temperatura": 22.0,
  "humedad_aire": 70.0,
  "humedad_sustrato": 55.0
}
```

### Pruebas obligatorias

Cada versión incluye en `versiones/<carpeta>/tests/` estas cinco pruebas con `pytest`. Ninguna puede usar una base de datos real, un broker ni un servicio push: se usan dobles de prueba.

| # | Escenario | Resultado esperado |
|---|---|---|
| 1 | Llega una lectura con temperatura de −40 °C | Se descarta y no se guarda |
| 2 | La temperatura está en 32 °C a las 10:00, 10:03 y 10:05 | No hay alerta crítica a las 10:03; sí hay una a las 10:05 |
| 3 | El servicio push falla al generarse una alerta crítica | La alerta queda guardada y el error no detiene el proceso |
| 4 | Un nodo envía su última lectura a las 10:00 y se revisa a las 10:06 | El nodo queda marcado como desconectado |
| 5 | Se agrega la regla "riesgo de hongos": humedad relativa mayor a 85 % con temperatura mayor a 25 °C genera una advertencia | La regla funciona sin modificar el código del evaluador existente |

La prueba 5 se resuelve de forma distinta según el enfoque, y esa diferencia forma parte de la comparación entre versiones.

### Contenido de cada carpeta

```
versiones/<carpeta>/
├── README.md        enfoque, aplicación de SOLID, decisiones y costos
├── diagrama.md      diagrama de clases en Mermaid
├── <código>
└── tests/
```

### Forma de trabajo

El repositorio sigue un flujo GitFlow simplificado. Ver la sección "Flujo de trabajo" del [README principal](../README.md).

1. Crear la rama de la versión a partir de `develop`.
2. Trabajar solo dentro de la carpeta de la versión.
3. Hacer commits pequeños con prefijo: `feat:`, `test:`, `docs:`, `refactor:` o `fix:`.
4. Ejecutar `pytest` antes de cada push.
5. Abrir un pull request hacia `develop` al terminar.
