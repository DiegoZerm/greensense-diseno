# Diagramas de la versión de módulos por funcionalidad

## Diagrama de clases

```mermaid
classDiagram
    direction LR

    namespace lecturas {
        class ModuloLecturas {
            <<fachada>>
            +registrar(mensaje) bool
            +todas() list
        }
        class ValidadorLecturas
        class Lectura
        class RepositorioLecturas {
            <<interface>>
        }
    }

    namespace alertas {
        class ModuloAlertas {
            <<fachada>>
            +evaluar(lectura) list
            +todas() list
        }
        class Regla {
            <<interface>>
            +evaluar(lectura) Alerta
        }
        class ReglaRango
        class Alerta
        class RepositorioAlertas {
            <<interface>>
        }
    }

    namespace notificaciones {
        class ModuloNotificaciones {
            <<fachada>>
            +notificar(mensaje) bool
        }
        class Notificador {
            <<interface>>
            +enviar(mensaje)
        }
        class NotificadorPush
        class NotificadorConsola
    }

    namespace nodos {
        class ModuloNodos {
            <<fachada>>
            +registrar_actividad(nodo, fecha)
            +revisar(ahora) list
            +conectados() list
        }
        class RepositorioNodos {
            <<interface>>
        }
    }

    namespace reportes {
        class ModuloReportes {
            <<fachada>>
            +estadisticas(variable) dict
            +exportar_csv(ruta, rol)
        }
    }

    ModuloLecturas *-- ValidadorLecturas
    ModuloLecturas --> RepositorioLecturas
    ModuloLecturas ..> Lectura : crea
    ModuloAlertas o-- Regla
    Regla <|.. ReglaRango
    ModuloAlertas --> RepositorioAlertas
    ModuloAlertas ..> Alerta : guarda
    ModuloNotificaciones --> Notificador
    Notificador <|.. NotificadorPush
    Notificador <|.. NotificadorConsola
    ModuloNodos --> RepositorioNodos

    ModuloLecturas --> ModuloAlertas : usa la fachada
    ModuloLecturas --> ModuloNodos : usa la fachada
    ModuloAlertas --> ModuloNotificaciones : usa la fachada
    ModuloNodos --> ModuloNotificaciones : usa la fachada
    ModuloReportes --> ModuloLecturas : usa la fachada
```

Las flechas entre módulos siempre llegan a una fachada. Ningún módulo usa las clases internas de otro.

## Diagrama de secuencia: llega una lectura fuera de rango

```mermaid
sequenceDiagram
    participant L as ModuloLecturas
    participant N as ModuloNodos
    participant A as ModuloAlertas
    participant T as ModuloNotificaciones
    participant P as NotificadorPush

    L->>L: valida y guarda la lectura
    L->>N: registrar_actividad(nodo, fecha)
    L->>A: evaluar(lectura)
    A->>A: aplica reglas y guarda la alerta crítica
    A->>T: notificar(mensaje)
    T->>P: enviar(mensaje)
    P--xT: error del servicio push
    T-->>A: falso
    Note over A: La alerta ya está guardada.
```
