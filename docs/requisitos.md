# Requisitos del servidor de GreenSense IoT

Los requisitos provienen de la propuesta del proyecto GreenSense IoT, un sistema de monitoreo ambiental y alertas para invernaderos. Este documento se limita al servidor, que es la parte que se analiza en la actividad.

## Requisitos funcionales

| Clave | Requisito |
|---|---|
| RF1 | Recibir lecturas de los nodos IoT en formato JSON mediante MQTT. |
| RF2 | Descartar lecturas incompletas o con valores físicamente imposibles. |
| RF3 | Guardar cada lectura válida con su nodo, fecha y hora. |
| RF4 | Comparar cada lectura con los umbrales configurados para el cultivo. |
| RF5 | Generar una alerta de advertencia cuando una variable se acerca al límite o sale del rango por poco tiempo. |
| RF6 | Generar una alerta crítica cuando una variable permanece fuera del rango durante el tiempo mínimo definido. |
| RF7 | Enviar una notificación push cuando se genera una alerta crítica o un nodo se desconecta. |
| RF8 | Marcar como desconectado un nodo que deja de enviar datos durante el tiempo definido. |
| RF9 | Calcular mínimo, máximo y promedio de cada variable. |
| RF10 | Exportar las lecturas a CSV, solo para supervisor y administrador. |
| RF11 | Registrar usuarios e iniciar sesión con contraseña cifrada y rol. |
| RF12 | Registrar en una bitácora las acciones relevantes de los usuarios. |

## Requisitos no funcionales

| Clave | Atributo | Requisito verificable |
|---|---|---|
| RNF1 | Rendimiento | Una lectura aparece en el panel en menos de 10 segundos después de tomarse. |
| RNF2 | Rendimiento | Una alerta crítica llega al teléfono en menos de 1 minuto. |
| RNF3 | Disponibilidad | Menos del 5 % de lecturas perdidas durante 7 días de prueba. |
| RNF4 | Seguridad | Las contraseñas se guardan cifradas y cada función se restringe por rol. |
| RNF5 | Mantenibilidad | Agregar una variable, una regla o un canal de notificación modifica pocos archivos y no cambia código ya probado. |
| RNF6 | Mantenibilidad | Las reglas del sistema se pueden probar sin base de datos, sin broker y sin servicio push. |
| RNF7 | Confiabilidad | Una falla en el envío de notificaciones no impide que la alerta se guarde. |

## Valores de referencia usados en el código

| Parámetro | Valor |
|---|---|
| Temperatura del aire | Rango 18 a 28 °C, margen de advertencia 2 °C |
| Humedad relativa | Rango 60 a 80 %, margen de advertencia 5 % |
| Humedad del sustrato | Rango 45 a 70 %, margen de advertencia 5 % |
| Valores físicamente posibles | Temperatura de −10 a 60 °C; humedades de 0 a 100 % |
| Tiempo mínimo para alerta crítica | 5 minutos fuera de rango |
| Tiempo para considerar un nodo desconectado | 5 minutos sin lecturas |

En el sistema real se usan PostgreSQL, Mosquitto y Web Push. En este repositorio se usan SQLite, mensajes JSON y un envío push simulado para que el código se ejecute sin instalar servicios adicionales.
