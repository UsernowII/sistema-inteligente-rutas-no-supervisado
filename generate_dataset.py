"""Generate a small unlabeled dataset of trips on the academic network."""

import csv
from pathlib import Path

from knowledge_base import FEATURE_NAMES, STATIONS, get_trip_features


DATA_PATH = Path(__file__).parent / "data" / "trips_for_clustering.csv"
CSV_FIELDS = ("origin", "destination", *FEATURE_NAMES)


def build_dataset_rows():
    """Return one feature record for each ordered pair of different stations."""
    rows = []
    for origin in STATIONS:
        for destination in STATIONS:
            if origin == destination:
                continue
            rows.append(
                {
                    "origin": origin,
                    "destination": destination,
                    **get_trip_features(origin, destination),
                }
            )
    return rows


def write_dataset(output_path=DATA_PATH):
    """Write the generated records to a CSV file and return its row count."""
    rows = build_dataset_rows()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


if __name__ == "__main__":
    row_count = write_dataset()
    print("Dataset sintético generado: {} viajes sin etiqueta.".format(row_count))
    print("Archivo: {}".format(DATA_PATH))
