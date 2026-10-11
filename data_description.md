# Descripción de los datos

## Fuente y procedencia

No se recibieron registros reales de viajes, pasajeros, horarios o tiempos del sistema de transporte. Según la consigna, se construyó una muestra sintética usando la red académica simplificada de nueve estaciones y sus conexiones, reutilizada en las actividades 2 y 3.

`generate_dataset.py` crea una fila para cada par ordenado de estaciones diferentes: 9 orígenes por 8 destinos posibles, para un total de 72 viajes. BFS calcula el menor número de tramos en esta red y también permite calcular los rasgos topológicos de cada estación.

## Campos del CSV

| Campo | Tipo | Descripción |
|---|---|---|
| `origin` | Texto | Estación de origen. |
| `destination` | Texto | Estación de destino. |
| `segments` | Entero | Cantidad mínima de tramos según BFS. |
| `origin_connections` | Entero | Número de conexiones directas de la estación de origen. |
| `destination_connections` | Entero | Número de conexiones directas de la estación de destino. |
| `origin_average_hops` | Decimal | Promedio de tramos desde el origen hacia las demás estaciones de la red. |
| `destination_average_hops` | Decimal | Promedio de tramos desde el destino hacia las demás estaciones de la red. |

El archivo no tiene una columna `route_class`, ni otra etiqueta objetivo. K-Means recibe los cinco campos numéricos; los nombres de las estaciones se conservan para interpretar y consultar los grupos.

## Límites de interpretación

Los registros se derivan de un grafo pequeño y didáctico, no de la operación real de TransMilenio. Cada fila representa un par origen-destino generado, no un viaje observado de una persona. Los rasgos describen tramos y conectividad, no demanda, tiempos, tarifas ni transbordos reales.

K-Means encuentra grupos según distancias entre rasgos estandarizados. Los identificadores de grupo son arbitrarios y no equivalen a clases verdaderas. El número de grupos se fija en tres para facilitar la demostración; no es una conclusión sobre la cantidad real de tipos de viaje.
