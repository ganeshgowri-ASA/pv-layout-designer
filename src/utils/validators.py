"""
Input validation functions for PV Layout Designer
"""
from typing import Tuple, Optional


def validate_module_dimensions(
    length: float,
    width: float,
    thickness: float,
    min_length: float = 500,
    max_length: float = 3000,
    min_width: float = 500,
    max_width: float = 2500,
    min_thickness: float = 30,
    max_thickness: float = 50,
) -> Tuple[bool, Optional[str]]:
    """
    Validate module dimensions.
    
    Args:
        length: Module length in mm
        width: Module width in mm
        thickness: Module thickness in mm
        min_length, max_length: Length range in mm
        min_width, max_width: Width range in mm
        min_thickness, max_thickness: Thickness range in mm
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (min_length <= length <= max_length):
        return False, f"Module length must be between {min_length} and {max_length} mm"
    
    if not (min_width <= width <= max_width):
        return False, f"Module width must be between {min_width} and {max_width} mm"
    
    if not (min_thickness <= thickness <= max_thickness):
        return False, f"Module thickness must be between {min_thickness} and {max_thickness} mm"
    
    return True, None


def validate_tilt_angle(
    tilt_angle: float,
    min_angle: float = 0,
    max_angle: float = 90
) -> Tuple[bool, Optional[str]]:
    """
    Validate tilt angle.
    
    Args:
        tilt_angle: Tilt angle in degrees
        min_angle, max_angle: Angle range in degrees
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (min_angle <= tilt_angle <= max_angle):
        return False, f"Tilt angle must be between {min_angle}° and {max_angle}°"
    
    return True, None


def validate_gcr(
    gcr: float,
    min_gcr: float = 0.20,
    max_gcr: float = 0.70
) -> Tuple[bool, Optional[str]]:
    """
    Validate Ground Coverage Ratio.
    
    Args:
        gcr: Ground Coverage Ratio
        min_gcr, max_gcr: GCR range
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (min_gcr <= gcr <= max_gcr):
        return False, f"GCR must be between {min_gcr} and {max_gcr}"
    
    return True, None


def validate_module_count(
    count: int,
    min_count: int = 1,
    max_count: int = 100
) -> Tuple[bool, Optional[str]]:
    """
    Validate module count per structure.
    
    Args:
        count: Number of modules
        min_count, max_count: Count range
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(count, int):
        return False, "Module count must be an integer"
    
    if not (min_count <= count <= max_count):
        return False, f"Module count must be between {min_count} and {max_count}"
    
    return True, None


def validate_height(
    height: float,
    min_height: float = 0.5,
    max_height: float = 3.0
) -> Tuple[bool, Optional[str]]:
    """
    Validate height from ground.
    
    Args:
        height: Height in meters
        min_height, max_height: Height range in meters
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (min_height <= height <= max_height):
        return False, f"Height must be between {min_height} and {max_height} m"
    
    return True, None


def validate_spacing(
    spacing: float,
    min_spacing: float,
    max_spacing: float,
    name: str = "Spacing"
) -> Tuple[bool, Optional[str]]:
    """
    Validate spacing/distance values.
    
    Args:
        spacing: Spacing value in meters
        min_spacing, max_spacing: Spacing range in meters
        name: Name of the spacing parameter for error messages
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (min_spacing <= spacing <= max_spacing):
        return False, f"{name} must be between {min_spacing} and {max_spacing} m"
    
    return True, None
