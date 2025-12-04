"""Input validation utilities."""

from typing import List, Tuple, Optional


def validate_coordinates(coordinates: List[Tuple[float, float]]) -> bool:
    """Validate that coordinates are within valid lat/lon ranges.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        bool: True if all coordinates are valid.
    """
    for lat, lon in coordinates:
        if not (-90 <= lat <= 90):
            return False
        if not (-180 <= lon <= 180):
            return False
    return True


def validate_polygon(coordinates: List[Tuple[float, float]]) -> bool:
    """Validate that coordinates form a valid polygon.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        bool: True if coordinates form a valid polygon (>= 3 points).
    """
    if len(coordinates) < 3:
        return False
    return validate_coordinates(coordinates)


def validate_tilt_angle(tilt: float) -> bool:
    """Validate tilt angle is within reasonable range.

    Args:
        tilt: Tilt angle in degrees.

    Returns:
        bool: True if tilt is valid (0-90 degrees).
    """
    return 0 <= tilt <= 90


def validate_gcr(gcr: float) -> bool:
    """Validate Ground Coverage Ratio.

    Args:
        gcr: Ground Coverage Ratio (0-1).

    Returns:
        bool: True if GCR is valid.
    """
    return 0 < gcr <= 1


def validate_azimuth(azimuth: float) -> bool:
    """Validate azimuth angle.

    Args:
        azimuth: Azimuth angle in degrees (0-360).

    Returns:
        bool: True if azimuth is valid.
    """
    return 0 <= azimuth < 360
