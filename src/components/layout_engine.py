"""
Core layout engine for PV module placement.
Implements the main algorithm for optimized module placement with GCR calculations.
"""
import math
from typing import Dict, List, Tuple, Optional
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

from src.utils.geometry import (
    calculate_row_pitch,
    calculate_polygon_area,
    calculate_gcr,
    point_in_polygon,
    apply_margin_to_polygon
)
from src.models.solar_calculations import get_winter_solstice_angle


def calculate_usable_area(site_polygon: List[Tuple[float, float]], margin: float) -> Polygon:
    """
    Apply perimeter margins and return usable area.
    
    Args:
        site_polygon: List of (x, y) coordinate tuples defining site boundary
        margin: Perimeter setback in meters
    
    Returns:
        Shapely Polygon object representing usable area
    """
    if not site_polygon or len(site_polygon) < 3:
        raise ValueError("Site polygon must have at least 3 vertices")
    
    if margin < 0:
        raise ValueError("Margin must be non-negative")
    
    # Create polygon and apply negative buffer
    polygon = Polygon(site_polygon)
    usable = polygon.buffer(-margin)
    
    # Return empty polygon if margin too large
    if usable.is_empty or usable.area <= 0:
        return Polygon()
    
    return usable


def calculate_module_count(area_sqm: float, module_area: float, gcr: float) -> int:
    """
    Estimate module count from site area and GCR.
    
    Args:
        area_sqm: Site area in square meters
        module_area: Single module area in square meters
        gcr: Ground Coverage Ratio (0.2 to 0.7)
    
    Returns:
        Estimated number of modules
    """
    if area_sqm <= 0 or module_area <= 0:
        return 0
    
    if not 0 < gcr <= 1:
        raise ValueError(f"GCR must be between 0 and 1, got {gcr}")
    
    # Total module area = site area × GCR
    total_module_area = area_sqm * gcr
    module_count = int(total_module_area / module_area)
    
    return module_count


def place_modules(site_coords: List[Tuple[float, float]], config: Dict) -> Dict:
    """
    Main placement algorithm for PV modules.
    
    Places modules in rows with optimal spacing based on:
    - Solar elevation angle (latitude-based)
    - Module tilt angle
    - Target GCR
    - Walkway requirements
    
    Args:
        site_coords: List of (x, y) tuples defining site boundary
        config: Configuration dictionary with keys:
            - latitude: Site latitude in degrees
            - module_length: Module length in meters (tilt direction)
            - module_width: Module width in meters (perpendicular to tilt)
            - module_power: Module power rating in watts
            - tilt_angle: Tilt angle in degrees
            - orientation: 'portrait' or 'landscape'
            - gcr_target: Target Ground Coverage Ratio (0.2-0.7)
            - walkway_width: Walkway width between arrays in meters
            - margin: Perimeter setback in meters
    
    Returns:
        Dictionary containing:
            - modules: List of module dictionaries with position and rotation
            - rows: Number of rows
            - modules_per_row: Average modules per row
            - total_modules: Total module count
            - capacity_kwp: System capacity in kWp
            - actual_gcr: Achieved GCR
            - usable_area: Usable site area in square meters
            - row_pitch: Row-to-row spacing in meters
    """
    # Validate inputs
    if not site_coords or len(site_coords) < 3:
        raise ValueError("Site must have at least 3 coordinate points")
    
    required_keys = ['latitude', 'module_length', 'module_width', 'module_power', 
                     'tilt_angle', 'margin']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Extract configuration
    latitude = config['latitude']
    module_length = config['module_length']
    module_width = config['module_width']
    module_power = config['module_power']  # in watts
    tilt_angle = config['tilt_angle']
    walkway_width = config.get('walkway_width', 3.0)  # Default 3m
    margin = config['margin']
    orientation = config.get('orientation', 'portrait')
    
    # Apply margin to get usable area
    usable_polygon = calculate_usable_area(site_coords, margin)
    
    if usable_polygon.is_empty or usable_polygon.area <= 0:
        return {
            'modules': [],
            'rows': 0,
            'modules_per_row': 0,
            'total_modules': 0,
            'capacity_kwp': 0.0,
            'actual_gcr': 0.0,
            'usable_area': 0.0,
            'row_pitch': 0.0,
            'error': 'Usable area is zero after applying margins'
        }
    
    usable_area = usable_polygon.area
    
    # Get solar elevation angle for winter solstice (worst case for shading)
    solar_elevation = get_winter_solstice_angle(latitude)
    
    if solar_elevation <= 0:
        return {
            'modules': [],
            'rows': 0,
            'modules_per_row': 0,
            'total_modules': 0,
            'capacity_kwp': 0.0,
            'actual_gcr': 0.0,
            'usable_area': usable_area,
            'row_pitch': 0.0,
            'error': f'Invalid solar elevation angle: {solar_elevation}°'
        }
    
    # Calculate row pitch (spacing between rows)
    row_pitch = calculate_row_pitch(module_length, tilt_angle, solar_elevation)
    
    # Add walkway to row spacing
    total_row_spacing = row_pitch + walkway_width
    
    # Calculate actual GCR
    actual_gcr = module_length / row_pitch
    
    # Get bounding box of usable area
    minx, miny, maxx, maxy = usable_polygon.bounds
    
    # Initialize module placement
    modules = []
    rows = []
    
    # Place rows from south to north (assuming north-south orientation)
    current_y = miny
    row_number = 0
    
    while current_y + module_length <= maxy:
        modules_in_row = []
        current_x = minx
        
        # Place modules along the row (west to east)
        while current_x + module_width <= maxx:
            # Create module rectangle
            module_polygon = box(current_x, current_y, 
                               current_x + module_width, 
                               current_y + module_length)
            
            # Check if module center is within usable area
            center_x = current_x + module_width / 2
            center_y = current_y + module_length / 2
            center_point = Point(center_x, center_y)
            
            # Only place module if center is within usable polygon
            # and module doesn't significantly extend outside
            if usable_polygon.contains(center_point):
                intersection = usable_polygon.intersection(module_polygon)
                if intersection.area >= module_polygon.area * 0.8:  # 80% overlap required
                    modules_in_row.append({
                        'position': (current_x, current_y),
                        'center': (center_x, center_y),
                        'orientation': orientation,
                        'rotation': 0,  # North-south orientation
                        'row': row_number
                    })
            
            current_x += module_width
        
        if modules_in_row:
            rows.append(modules_in_row)
            modules.extend(modules_in_row)
            row_number += 1
        
        current_y += total_row_spacing
    
    # Calculate results
    total_modules = len(modules)
    capacity_kwp = (total_modules * module_power) / 1000.0  # Convert W to kW
    avg_modules_per_row = total_modules / len(rows) if rows else 0
    
    return {
        'modules': modules,
        'rows': len(rows),
        'modules_per_row': avg_modules_per_row,
        'total_modules': total_modules,
        'capacity_kwp': capacity_kwp,
        'actual_gcr': actual_gcr,
        'usable_area': usable_area,
        'row_pitch': row_pitch,
        'row_spacing': total_row_spacing,
        'module_area': module_length * module_width,
        'solar_elevation': solar_elevation
    }


def optimize_layout(site_area: float, module_dims: Dict, target_gcr: float, 
                   latitude: float, tilt_angle: float) -> Dict:
    """
    Optimize module placement for given constraints.
    
    Args:
        site_area: Available site area in square meters
        module_dims: Dictionary with 'length', 'width', 'power' in meters and watts
        target_gcr: Target Ground Coverage Ratio (0.2-0.7)
        latitude: Site latitude in degrees
        tilt_angle: Module tilt angle in degrees
    
    Returns:
        Dictionary with optimized layout parameters:
            - recommended_modules: Estimated module count
            - row_pitch: Optimal row spacing
            - gcr: Achieved GCR
            - capacity_kwp: Expected capacity
    """
    if not 0.2 <= target_gcr <= 0.7:
        raise ValueError(f"Target GCR must be between 0.2 and 0.7, got {target_gcr}")
    
    module_length = module_dims['length']
    module_width = module_dims['width']
    module_power = module_dims['power']
    module_area = module_length * module_width
    
    # Get solar angle
    solar_elevation = get_winter_solstice_angle(latitude)
    
    if solar_elevation <= 0:
        raise ValueError(f"Invalid solar elevation angle: {solar_elevation}°")
    
    # Calculate row pitch for no shading
    row_pitch_no_shading = calculate_row_pitch(module_length, tilt_angle, solar_elevation)
    
    # Calculate row pitch for target GCR
    row_pitch_target = module_length / target_gcr
    
    # Use the larger of the two (more conservative)
    row_pitch = max(row_pitch_no_shading, row_pitch_target)
    
    # Recalculate actual GCR
    actual_gcr = module_length / row_pitch
    
    # Estimate module count
    estimated_modules = calculate_module_count(site_area, module_area, actual_gcr)
    
    # Calculate capacity
    capacity_kwp = (estimated_modules * module_power) / 1000.0
    
    return {
        'recommended_modules': estimated_modules,
        'row_pitch': row_pitch,
        'gcr': actual_gcr,
        'capacity_kwp': capacity_kwp,
        'module_area': module_area,
        'total_module_area': estimated_modules * module_area,
        'solar_elevation': solar_elevation
    }
