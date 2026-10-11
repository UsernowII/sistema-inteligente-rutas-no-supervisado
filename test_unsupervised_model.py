"""Tests for dataset generation and unsupervised trip clustering."""

import tempfile
import unittest
from pathlib import Path

from generate_dataset import CSV_FIELDS, build_dataset_rows, write_dataset
from kmeans_model import (
    fit_kmeans,
    fit_scaler,
    load_samples,
    predict_cluster,
    transform_features,
)
from knowledge_base import FEATURE_NAMES, get_trip_features


class UnsupervisedModelTests(unittest.TestCase):
    def test_dataset_contains_72_ordered_trips_without_labels(self):
        rows = build_dataset_rows()
        pairs = {(row["origin"], row["destination"]) for row in rows}

        self.assertEqual(len(rows), 72)
        self.assertEqual(len(pairs), 72)
        self.assertTrue(all(row["origin"] != row["destination"] for row in rows))
        self.assertNotIn("route_class", CSV_FIELDS)

    def test_generated_csv_can_be_loaded(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "sample.csv"
            self.assertEqual(write_dataset(csv_path), 72)
            samples = load_samples(csv_path)

        self.assertEqual(len(samples), 72)
        self.assertTrue(all(name in samples[0] for name in FEATURE_NAMES))

    def test_trip_features_are_symmetric_for_undirected_network(self):
        forward = get_trip_features("Portal Norte", "Bosa")
        reverse = get_trip_features("Bosa", "Portal Norte")

        self.assertEqual(forward["segments"], reverse["segments"])
        self.assertEqual(forward["origin_connections"], reverse["destination_connections"])
        self.assertEqual(
            forward["destination_connections"], reverse["origin_connections"]
        )

    def test_scaler_standardizes_each_feature(self):
        samples = build_dataset_rows()
        scaler = fit_scaler(samples)
        points = transform_features(samples, scaler)

        for feature_index in range(len(FEATURE_NAMES)):
            values = [point[feature_index] for point in points]
            self.assertAlmostEqual(sum(values) / len(values), 0.0, places=7)

    def test_kmeans_is_reproducible_and_assigns_every_sample(self):
        samples = build_dataset_rows()
        scaler = fit_scaler(samples)
        points = transform_features(samples, scaler)
        first_model, first_assignments = fit_kmeans(points, n_clusters=3, seed=42)
        second_model, second_assignments = fit_kmeans(points, n_clusters=3, seed=42)

        self.assertEqual(first_assignments, second_assignments)
        self.assertEqual(first_model["centroids"], second_model["centroids"])
        self.assertEqual(len(first_assignments), 72)
        self.assertEqual(set(first_assignments), {0, 1, 2})
        self.assertGreaterEqual(first_model["inertia"], 0)

    def test_prediction_matches_training_assignment_for_sample(self):
        samples = build_dataset_rows()
        scaler = fit_scaler(samples)
        points = transform_features(samples, scaler)
        model, assignments = fit_kmeans(points, n_clusters=3, seed=42)

        self.assertEqual(predict_cluster(model, samples[0], scaler), assignments[0])

    def test_unknown_station_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "origen"):
            get_trip_features("Estación inventada", "Bosa")


if __name__ == "__main__":
    unittest.main()
