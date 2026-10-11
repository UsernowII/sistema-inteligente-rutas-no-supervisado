# Agrupamiento no supervisado de viajes en una red simplificada

Aplicación de consola en Python que usa K-Means para encontrar grupos de viajes parecidos en una red académica simplificada de TransMilenio. El modelo no recibe categorías de viaje correctas: descubre grupos a partir de características numéricas.

## Relación con las actividades anteriores

- **Actividad 2:** BFS encuentra y devuelve una ruta con la menor cantidad de tramos entre dos estaciones.
- **Actividad 3:** un árbol de decisión supervisado aprende de ejemplos con etiquetas `corta`, `media` o `larga` y predice una de esas categorías.
- **Actividad 4:** K-Means agrupa viajes sin etiquetas. Se conserva la red y se reutiliza BFS para calcular rasgos, pero el algoritmo no recibe `route_class` ni aprende categorías predefinidas.

En esta actividad se explora qué viajes tienen características parecidas según el número de tramos, las conexiones de las estaciones y su distancia promedio al resto de la red. Los números de grupo son identificadores arbitrarios; el programa resume cada grupo para facilitar su interpretación.

## Datos

No se proporcionaron datos operativos reales, así que el proyecto genera una muestra sintética de 72 pares ordenados de estaciones distintas. La descripción de procedencia y de cada columna está en [data_description.md](data_description.md). El archivo CSV no contiene etiquetas de clase.

## Requisitos

- Python 3.
- No se requieren paquetes externos ni conexión a internet.

## Ejecutar

Desde la carpeta del proyecto:

```bash
python generate_dataset.py
python main.py
```

En macOS o Linux, usa `python3` en lugar de `python` si ese es el nombre de tu instalación. Cuando lo solicite, ingresa estaciones distintas de la red, por ejemplo `Portal Norte` y `Bosa`. El programa muestra el resumen de los grupos y asigna el viaje al grupo más cercano.

Para ejecutar las pruebas automatizadas:

```bash
python -m unittest -v
```

## Resultado de referencia

Con la semilla fija y tres grupos, la ejecución de referencia encontró grupos de 30, 27 y 15 viajes. Sus promedios fueron 2,50, 2,26 y 5,33 tramos, respectivamente. Por ejemplo, `Portal Norte` → `Bosa` queda en el grupo 2 en esta ejecución. Estos grupos describen solo la muestra sintética; K-Means no conoce categorías verdaderas y los identificadores de grupo no tienen significado por sí solos. El detalle está en [test_results.md](test_results.md).

## Archivos principales

- `knowledge_base.py`: estaciones, conexiones y características topológicas.
- `generate_dataset.py`: crea los 72 ejemplos sintéticos sin etiqueta.
- `data/trips_for_clustering.csv`: datos para el agrupamiento.
- `kmeans_model.py`: estandarización, entrenamiento K-Means, asignación y resumen de grupos.
- `main.py`: ejecuta el análisis e interactúa con el usuario.
- `test_unsupervised_model.py`: pruebas automatizadas con `unittest`.
- `data_description.md`: procedencia, campos y límites de interpretación.
- `test_results.md`: casos y resultados de las pruebas.

## Alcance

El prototipo muestra agrupamiento no supervisado sobre datos sintéticos. No calcula una ruta alternativa, no mide tiempos reales ni descubre patrones de demanda de pasajeros. Los grupos dependen de las características elegidas, del número de grupos solicitado y de la pequeña red de ejemplo.
