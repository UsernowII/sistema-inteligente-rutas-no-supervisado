"""Knowledge base for the simplified TransMilenio network."""

from collections import deque
import unicodedata


CONNECTIONS = {
    "Portal Norte": ["Calle 100"],
    "Calle 100": ["Portal Norte", "Calle 72"],
    "Calle 72": ["Calle 100", "Héroes"],
    "Héroes": ["Calle 72", "Calle 26"],
    "Calle 26": ["Héroes", "Museo Nacional", "Ricaurte"],
    "Museo Nacional": ["Calle 26"],
    "Ricaurte": ["Calle 26", "Portal Américas"],
    "Portal Américas": ["Ricaurte", "Bosa"],
    "Bosa": ["Portal Américas"],
}

STATIONS = list(CONNECTIONS)

FEATURE_NAMES = (
    "segments",
    "origin_connections",
    "destination_connections",
    "origin_average_hops",
    "destination_average_hops",
)


def normalize_station_name(station):
    """Normalize accents, spaces, and case for station-name comparison."""
    normalized = " ".join(station.strip().split()).casefold()
    decomposed = unicodedata.normalize("NFD", normalized)
    return "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )


def get_canonical_station(station):
    """Return the canonical station name, or None when it is unknown."""
    if not isinstance(station, str):
        return None

    normalized = normalize_station_name(station)
    for official_name in STATIONS:
        if normalize_station_name(official_name) == normalized:
            return official_name
    return None


def get_neighbors(station):
    """Return a copy of the station's neighbors, or an empty list."""
    canonical_station = get_canonical_station(station)
    if canonical_station is None:
        return []
    return list(CONNECTIONS[canonical_station])


def get_station_profiles():
    """Calculate connection count and mean network distance for each station."""
    profiles = {}
    for station in STATIONS:
        distances = {station: 0}
        queue = deque([station])

        while queue:
            current_station = queue.popleft()
            for neighbor in CONNECTIONS[current_station]:
                if neighbor not in distances:
                    distances[neighbor] = distances[current_station] + 1
                    queue.append(neighbor)

        if len(distances) != len(STATIONS):
            raise ValueError("The simplified network contains disconnected stations.")

        average_hops = sum(distances.values()) / (len(STATIONS) - 1)
        profiles[station] = {
            "connections": len(CONNECTIONS[station]),
            "average_hops": average_hops,
        }

    return profiles


def get_trip_features(origin, destination):
    """Build unlabeled numeric features for one distinct origin-destination pair."""
    origin_station = get_canonical_station(origin)
    destination_station = get_canonical_station(destination)

    if origin_station is None:
        raise ValueError("La estación de origen no pertenece a la red del ejemplo.")
    if destination_station is None:
        raise ValueError("La estación de destino no pertenece a la red del ejemplo.")
    if origin_station == destination_station:
        raise ValueError("El origen y el destino deben ser estaciones diferentes.")

    distances = {origin_station: 0}
    queue = deque([origin_station])
    while queue:
        current_station = queue.popleft()
        if current_station == destination_station:
            break
        for neighbor in CONNECTIONS[current_station]:
            if neighbor not in distances:
                distances[neighbor] = distances[current_station] + 1
                queue.append(neighbor)

    if destination_station not in distances:
        raise ValueError("No existe una conexión entre las estaciones indicadas.")

    profiles = get_station_profiles()
    origin_profile = profiles[origin_station]
    destination_profile = profiles[destination_station]

    return {
        "segments": distances[destination_station],
        "origin_connections": origin_profile["connections"],
        "destination_connections": destination_profile["connections"],
        "origin_average_hops": origin_profile["average_hops"],
        "destination_average_hops": destination_profile["average_hops"],
    }
