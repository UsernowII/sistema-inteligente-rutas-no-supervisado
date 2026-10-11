"""A small, dependency-free K-Means implementation for trip clustering."""

import csv
import math
import random

from knowledge_base import FEATURE_NAMES


def load_samples(csv_path):
    """Load trip records without adding or requiring a target label."""
    samples = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required_fields = {"origin", "destination", *FEATURE_NAMES}
        missing_fields = required_fields.difference(reader.fieldnames or [])
        if missing_fields:
            raise ValueError(
                "Faltan columnas requeridas en el CSV: {}".format(
                    ", ".join(sorted(missing_fields))
                )
            )

        for row in reader:
            sample = {"origin": row["origin"], "destination": row["destination"]}
            for feature_name in FEATURE_NAMES:
                sample[feature_name] = float(row[feature_name])
            samples.append(sample)

    if not samples:
        raise ValueError("El CSV no contiene viajes para agrupar.")
    return samples


def fit_scaler(samples):
    """Calculate feature means and standard deviations for normalization."""
    if not samples:
        raise ValueError("Se requieren muestras para calcular el escalador.")

    scaler = {}
    for feature_name in FEATURE_NAMES:
        values = [float(sample[feature_name]) for sample in samples]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        standard_deviation = math.sqrt(variance)
        scaler[feature_name] = {
            "mean": mean,
            "scale": standard_deviation if standard_deviation else 1.0,
        }
    return scaler


def transform_features(sample, scaler):
    """Standardize one sample or a list of samples with a fitted scaler."""
    if isinstance(sample, dict):
        return [
            (float(sample[name]) - scaler[name]["mean"]) / scaler[name]["scale"]
            for name in FEATURE_NAMES
        ]
    return [transform_features(item, scaler) for item in sample]


def _squared_distance(first, second):
    return sum((first[index] - second[index]) ** 2 for index in range(len(first)))


def _initialize_centroids(points, n_clusters, seed):
    """Choose reproducible K-Means++ starting centroids."""
    generator = random.Random(seed)
    first_index = generator.randrange(len(points))
    centroids = [list(points[first_index])]

    while len(centroids) < n_clusters:
        distances = [
            min(_squared_distance(point, centroid) for centroid in centroids)
            for point in points
        ]
        total_distance = sum(distances)

        if total_distance == 0:
            remaining = [point for point in points if list(point) not in centroids]
            centroids.append(list(remaining[0] if remaining else points[len(centroids)]))
            continue

        threshold = generator.random() * total_distance
        cumulative_distance = 0.0
        for point, distance in zip(points, distances):
            cumulative_distance += distance
            if cumulative_distance >= threshold:
                candidate = list(point)
                if candidate not in centroids:
                    centroids.append(candidate)
                break

        if len(centroids) < n_clusters and candidate in centroids:
            remaining = [point for point in points if list(point) not in centroids]
            if remaining:
                centroids.append(list(remaining[0]))

    return centroids


def _assign_points(points, centroids):
    return [
        min(
            range(len(centroids)),
            key=lambda cluster_index: _squared_distance(
                point, centroids[cluster_index]
            ),
        )
        for point in points
    ]


def _repair_empty_clusters(points, assignments, centroids):
    """Move a distant point from a populated cluster into each empty cluster."""
    counts = [assignments.count(index) for index in range(len(centroids))]
    for empty_index, count in enumerate(counts):
        if count:
            continue

        candidates = [
            point_index
            for point_index, assigned_index in enumerate(assignments)
            if counts[assigned_index] > 1
        ]
        if not candidates:
            raise ValueError("No se pudo recuperar un grupo vacío de K-Means.")

        point_index = max(
            candidates,
            key=lambda index: _squared_distance(
                points[index], centroids[assignments[index]]
            ),
        )
        previous_index = assignments[point_index]
        assignments[point_index] = empty_index
        counts[previous_index] -= 1
        counts[empty_index] += 1


def fit_kmeans(points, n_clusters=3, max_iterations=100, tolerance=1e-8, seed=42):
    """Fit K-Means and return a model plus the cluster of each training row."""
    if not points:
        raise ValueError("Se requieren puntos para entrenar K-Means.")
    if n_clusters < 1 or n_clusters > len(points):
        raise ValueError("La cantidad de grupos debe estar entre 1 y el número de filas.")
    feature_count = len(points[0])
    if feature_count == 0 or any(len(point) != feature_count for point in points):
        raise ValueError("Todas las muestras deben tener las mismas características.")

    normalized_points = [[float(value) for value in point] for point in points]
    centroids = _initialize_centroids(normalized_points, n_clusters, seed)
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        assignments = _assign_points(normalized_points, centroids)
        _repair_empty_clusters(normalized_points, assignments, centroids)

        new_centroids = []
        for cluster_index in range(n_clusters):
            members = [
                point
                for point, assigned_index in zip(normalized_points, assignments)
                if assigned_index == cluster_index
            ]
            new_centroids.append(
                [
                    sum(point[feature_index] for point in members) / len(members)
                    for feature_index in range(feature_count)
                ]
            )

        largest_shift = max(
            math.sqrt(_squared_distance(old, new))
            for old, new in zip(centroids, new_centroids)
        )
        centroids = new_centroids
        iterations = iteration
        if largest_shift <= tolerance:
            break

    assignments = _assign_points(normalized_points, centroids)
    inertia = sum(
        _squared_distance(point, centroids[cluster_index])
        for point, cluster_index in zip(normalized_points, assignments)
    )
    model = {
        "centroids": centroids,
        "n_clusters": n_clusters,
        "iterations": iterations,
        "inertia": inertia,
    }
    return model, assignments


def predict_cluster(model, sample, scaler):
    """Assign a new feature record to its nearest learned centroid."""
    point = transform_features(sample, scaler)
    return min(
        range(model["n_clusters"]),
        key=lambda cluster_index: _squared_distance(
            point, model["centroids"][cluster_index]
        ),
    )


def summarize_clusters(samples, assignments, n_clusters=3):
    """Describe clusters after fitting; these summaries are not model labels."""
    summaries = []
    for cluster_index in range(n_clusters):
        members = [
            sample
            for sample, assigned_index in zip(samples, assignments)
            if assigned_index == cluster_index
        ]
        summary = {"cluster": cluster_index, "count": len(members)}
        if members:
            for feature_name in FEATURE_NAMES:
                summary["mean_{}".format(feature_name)] = sum(
                    sample[feature_name] for sample in members
                ) / len(members)
        summaries.append(summary)
    return summaries
