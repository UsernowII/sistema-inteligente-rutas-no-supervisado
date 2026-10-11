"""Console application for clustering trips without known categories."""

from generate_dataset import DATA_PATH, write_dataset
from knowledge_base import get_trip_features
from kmeans_model import (
    fit_kmeans,
    fit_scaler,
    load_samples,
    predict_cluster,
    summarize_clusters,
    transform_features,
)


def main():
    if not DATA_PATH.exists():
        write_dataset()

    samples = load_samples(DATA_PATH)
    scaler = fit_scaler(samples)
    points = transform_features(samples, scaler)
    model, assignments = fit_kmeans(points, n_clusters=3, seed=42)
    summaries = summarize_clusters(samples, assignments, n_clusters=3)

    print("Agrupamiento no supervisado de viajes en la red simplificada")
    print("Muestras agrupadas: {}".format(len(samples)))
    print("Características: segmentos y estructura de las estaciones")
    print("Inercia del modelo: {:.3f}".format(model["inertia"]))
    print("\nResumen de grupos (los números no representan categorías predefinidas):")
    for summary in summaries:
        average_segments = summary.get("mean_segments")
        if average_segments is None:
            print("Grupo {}: sin muestras".format(summary["cluster"]))
            continue
        print(
            "Grupo {}: {} viajes; promedio de {:.2f} tramos; "
            "conexiones promedio origen/destino: {:.2f}/{:.2f}".format(
                summary["cluster"],
                summary["count"],
                average_segments,
                summary["mean_origin_connections"],
                summary["mean_destination_connections"],
            )
        )

    print("\nConsulta un viaje de la red (no ingreses la misma estación dos veces).")
    origin = input("Estación de origen: ")
    destination = input("Estación de destino: ")

    try:
        features = get_trip_features(origin, destination)
        cluster_index = predict_cluster(model, features, scaler)
    except ValueError as error:
        print("\nNo se pudo clasificar el viaje: {}".format(error))
        return

    cluster_summary = summaries[cluster_index]
    print("\nEl viaje pertenece al grupo {}.".format(cluster_index))
    print(
        "En la muestra, este grupo contiene {} viajes y tiene un promedio de "
        "{:.2f} tramos.".format(
            cluster_summary["count"], cluster_summary["mean_segments"]
        )
    )
    print(
        "El grupo se descubrió sin usar etiquetas de tipo corto, medio o largo; "
        "su número es solo un identificador."
    )


if __name__ == "__main__":
    main()
