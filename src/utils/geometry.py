"""
Geometry utilities for PV layout calculations.
Provides spatial calculation functions for module placement.
"""
import math
from typing import List, Tuple
from shapely.geometry import Polygon, Point


def calculate_row_pitch(module_length: float, tilt_angle: float, solar_elevation: float) -> float:
    """
    Calculate row-to-row spacing for no shading at winter solstice.
    
    Formula: R = L×cos(β) + L×sin(β)/tan(α)
    Where:
        R = Row pitch (spacing between rows)
        L = Module length (in direction of tilt)
        β = Tilt angle (degrees)
        α = Solar elevation angle (degrees)
    
    Args:
        module_length: Module length in meters
        tilt_angle: Module tilt angle in degrees
        solar_elevation: Solar elevation angle in degrees
    
    Returns:
        Row pitch in meters
    """
    # Convert angles to radians
    beta_rad = math.radians(tilt_angle)
    alpha_rad = math.radians(solar_elevation)
    
    # Prevent division by zero
    if alpha_rad <= 0 or alpha_rad >= math.pi/2:
        raise ValueError(f"Solar elevation angle must be between 0 and 90 degrees, got {solar_elevation}")
    
    # Calculate row pitch
    horizontal_projection = module_length * math.cos(beta_rad)
    shadow_length = module_length * math.sin(beta_rad) / math.tan(alpha_rad)
    row_pitch = horizontal_projection + shadow_length
    
    return row_pitch


def calculate_polygon_area(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calculate area of a polygon from coordinates.
    
    Args:
        coordinates: List of (x, y) or (lon, lat) tuples
    
    Returns:
        Area in square meters (or square units of input coordinates)
    """
    if len(coordinates) < 3:
        raise ValueError("Polygon must have at least 3 vertices")
    
    polygon = Polygon(coordinates)
    return polygon.area


def calculate_gcr(module_length: float, row_pitch: float) -> float:
    """
    Calculate Ground Coverage Ratio.
    
    GCR = Module length / Row pitch
    
    Args:
        module_length: Module length in meters
        row_pitch: Row-to-row spacing in meters
    
    Returns:
        GCR as a decimal (e.g., 0.40 for 40%)
    """
    if row_pitch <= 0:
        raise ValueError("Row pitch must be positive")
    
    return module_length / row_pitch


def point_in_polygon(point: Tuple[float, float], polygon_coords: List[Tuple[float, float]]) -> bool:
    """
    Check if a point is inside a polygon.
    
    Args:
        point: (x, y) tuple
        polygon_coords: List of (x, y) tuples defining polygon
    
    Returns:
        True if point is inside polygon, False otherwise
    """
    polygon = Polygon(polygon_coords)
    point_obj = Point(point)
    return polygon.contains(point_obj)


def apply_margin_to_polygon(polygon_coords: List[Tuple[float, float]], margin: float) -> List[Tuple[float, float]]:
    """
    Apply a negative buffer (margin) to a polygon to get usable area.
    
    Args:
        polygon_coords: List of (x, y) tuples
        margin: Margin distance in meters (positive value shrinks polygon)
    
    Returns:
        List of coordinates for the buffered polygon
    """
    if margin < 0:
        raise ValueError("Margin must be non-negative")
    
    polygon = Polygon(polygon_coords)
    buffered = polygon.buffer(-margin)
    
    # Handle case where buffer results in empty polygon
    if buffered.is_empty:
        return []
    
    # Extract coordinates
    if hasattr(buffered, 'exterior'):
        return list(buffered.exterior.coords)
    else:
        return []


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: (x, y) tuple
        point2: (x, y) tuple
    
    Returns:
        Distance in same units as input coordinates
    """
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
