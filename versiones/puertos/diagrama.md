# Diagramas de la versión de puertos y adaptadores

## Diagrama de clases

```mermaid
classDiagram
    direction LR

    namespace dominio {
        class Lectura
        class Alerta
        class Umbral
        class ValidadorLecturas {
            +es_valida(lectura) bool
        }
        class Regla {
            <<interface>>
            +evaluar(lectura) Alerta
        }
        class ReglaRango {
            -variable: str
            -umbral: Umbral
            -tiempo_minimo: timedelta
            +evaluar(lectura) Alerta
        }
        class PoliticaUmbrales {
            -reglas: list
            +evaluar(lectura) list
        }
    }

    namespace puertos {
        class RepositorioLecturas {
            <<interface>>
            +guardar(lectura)
            +todas() list
        }
        class RepositorioAlertas {
            <<interface>>
            +guardar(alerta)
            +todas() list
        }
        class RepositorioNodos {
            <<interface>>
            +registrar_actividad(nodo, fecha)
            +conectados() list
            +marcar_desconectado(nodo)
        }
        class Notificador {
            <<interface>>
            +enviar(mensaje)
        }
        class Reloj {
            <<interface>>
            +ahora() datetime
        }
    }

    namespace aplicacion {
        class RegistrarLectura {
            +ejecutar(lectura) bool
        }
        class RevisarNodos {
            +ejecutar() list
        }
        class GenerarReporte {
            +estadisticas(variable) dict
            +exportar_csv(ruta, rol)
        }
    }

    namespace adaptadores {
        class AdaptadorMqtt {
            +recibir(payload) bool
        }
        class RepositorioLecturasSQLite
        class RepositorioLecturasMemoria
        class RepositorioAlertasSQLite
        class RepositorioAlertasMemoria
        class RepositorioNodosSQLite
        class RepositorioNodosMemoria
        class NotificadorPushHttp
        class NotificadorConsola
        class RelojSistema
        class RelojFijo
    }

    Regla <|.. ReglaRango
    ReglaRango --> Umbral
    PoliticaUmbrales o-- Regla

    RegistrarLectura --> ValidadorLecturas
    RegistrarLectura --> PoliticaUmbrales
    RegistrarLectura --> RepositorioLecturas
    RegistrarLectura --> RepositorioAlertas
    RegistrarLectura --> RepositorioNodos
    RegistrarLectura --> Notificador
    RevisarNodos --> RepositorioNodos
    RevisarNodos --> Notificador
    RevisarNodos --> Reloj
    GenerarReporte --> RepositorioLecturas

    AdaptadorMqtt --> RegistrarLectura
    AdaptadorMqtt ..> Lectura : crea
    RepositorioLecturas <|.. RepositorioLecturasSQLite
    RepositorioLecturas <|.. RepositorioLecturasMemoria
    RepositorioAlertas <|.. RepositorioAlertasSQLite
    RepositorioAlertas <|.. RepositorioAlertasMemoria
    RepositorioNodos <|.. RepositorioNodosSQLite
    RepositorioNodos <|.. RepositorioNodosMemoria
    Notificador <|.. NotificadorPushHttp
    Notificador <|.. NotificadorConsola
    Reloj <|.. RelojSistema
    Reloj <|.. RelojFijo
```

Todas las flechas de dependencia apuntan hacia el núcleo (dominio y puertos). Los adaptadores conocen al núcleo, pero el núcleo no conoce a ningún adaptador.

## Diagrama de secuencia: llega una lectura fuera de rango

```mermaid
sequenceDiagram
    participant M as AdaptadorMqtt
    participant R as RegistrarLectura
    participant V as ValidadorLecturas
    participant P as PoliticaUmbrales
    participant RL as RepositorioLecturas
    participant RA as RepositorioAlertas
    participant N as Notificador

    M->>M: convierte el JSON en Lectura
    M->>R: ejecutar(lectura)
    R->>V: es_valida(lectura)
    V-->>R: verdadero
    R->>RL: guardar(lectura)
    R->>P: evaluar(lectura)
    P-->>R: [alerta crítica]
    R->>RA: guardar(alerta)
    R->>N: enviar(mensaje)
    N--xR: error del servicio push
    Note over R: El error se registra.<br/>La alerta ya está guardada.
```
