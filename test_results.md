# Pruebas del componente de aprendizaje no supervisado

Las pruebas automatizadas se ejecutaron desde la carpeta del proyecto con:

```bash
python3 -m unittest -v
```

## Casos ejecutados

| Caso | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|
| Generación de viajes | 72 pares ordenados sin origen igual al destino y sin etiqueta de clase | 72 pares distintos; no se genera `route_class` | Aprobada |
| Escritura y lectura del CSV | El generador escribe y el cargador lee las 72 filas | 72 filas cargadas con las cinco características numéricas | Aprobada |
| Simetría de la red | Invertir el viaje conserva los tramos e intercambia los rasgos de origen y destino | Se conserva la distancia y se intercambian las características | Aprobada |
| Estandarización | Cada característica transformada tiene media cercana a cero | Medias verificadas con tolerancia numérica | Aprobada |
| Entrenamiento reproducible | La misma semilla produce los mismos centroides y asignaciones | Se obtuvieron tres grupos reproducibles y se asignaron las 72 filas | Aprobada |
| Asignación de una consulta | La predicción de una muestra conocida coincide con su grupo entrenado | La asignación coincide | Aprobada |
| Estación desconocida | La entrada inválida se rechaza con un error claro | Se rechazó la estación y se informó el campo de origen | Aprobada |

Resultado: `Ran 7 tests`, `OK`.

## Ejecución de muestra

Con la semilla 42 y tres grupos, la aplicación procesó 72 viajes. El resumen fue:

| Grupo | Viajes | Promedio de tramos | Conexiones promedio origen/destino |
|---:|---:|---:|---:|
| 0 | 30 | 2,50 | 2,27 / 1,47 |
| 1 | 27 | 2,26 | 1,52 / 2,30 |
| 2 | 15 | 5,33 | 1,27 / 1,47 |

La consulta `Portal Norte` → `Bosa` quedó en el grupo 2, cuyo promedio en esta muestra es 5,33 tramos. Los números de grupo pueden cambiar si cambian los datos, las características, la cantidad de grupos o la semilla. No se calcula exactitud porque no hay etiquetas verdaderas contra las cuales comparar el agrupamiento.

En esta ejecución, los grupos 0 y 1 tienen promedios de tramos cercanos, pero se diferencian en cuántas conexiones tienen en promedio sus estaciones de origen y destino. El grupo 2 reúne viajes con un promedio mayor de tramos. Esta lectura describe los rasgos de los grupos; no convierte los identificadores arbitrarios de K-Means en etiquetas verdaderas.
