"""Geometry utilities for PV layout calculations."""

import math
from typing import List, Tuple


def calculate_polygon_area(coordinates: List[Tuple[float, float]]) -> float:
    """Calculate the area of a polygon using the Shoelace formula.

    Args:
        coordinates: List of (lat, lon) tuples representing the polygon vertices.

    Returns:
        float: Area in square meters (approximate).
    """
    if len(coordinates) < 3:
        return 0.0

    # Convert to approximate meters using equirectangular projection
    # Reference point is the centroid
    center_lat = sum(c[0] for c in coordinates) / len(coordinates)
    center_lon = sum(c[1] for c in coordinates) / len(coordinates)

    # Convert to local coordinates in meters
    coords_m = []
    for lat, lon in coordinates:
        x = (lon - center_lon) * 111320 * math.cos(math.radians(center_lat))
        y = (lat - center_lat) * 110540
        coords_m.append((x, y))

    # Shoelace formula
    n = len(coords_m)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords_m[i][0] * coords_m[j][1]
        area -= coords_m[j][0] * coords_m[i][1]

    return abs(area) / 2.0


def calculate_polygon_centroid(coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the centroid of a polygon.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        tuple: (lat, lon) of the centroid.
    """
    if not coordinates:
        return (0.0, 0.0)

    lat_sum = sum(c[0] for c in coordinates)
    lon_sum = sum(c[1] for c in coordinates)
    n = len(coordinates)

    return (lat_sum / n, lon_sum / n)


def get_bounding_box(coordinates: List[Tuple[float, float]]) -> List[List[float]]:
    """Get the bounding box of a set of coordinates.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        list: [[south, west], [north, east]]
    """
    if not coordinates:
        return [[0.0, 0.0], [0.0, 0.0]]

    lats = [c[0] for c in coordinates]
    lons = [c[1] for c in coordinates]

    return [[min(lats), min(lons)], [max(lats), max(lons)]]
