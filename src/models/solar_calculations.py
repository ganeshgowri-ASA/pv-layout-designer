"""
Solar calculations for PV layout design.
Provides sun position and angle calculations for shading analysis.
"""
import math
from datetime import datetime, timedelta


def get_winter_solstice_angle(latitude: float) -> float:
    """
    Calculate solar elevation angle at winter solstice noon.
    
    This is the worst-case scenario for shading analysis.
    Formula: α = 90° - |latitude| - 23.5° (solar declination at winter solstice)
    
    For Northern Hemisphere: α = 90° - latitude - 23.5°
    For Southern Hemisphere: α = 90° + latitude - 23.5°
    
    Args:
        latitude: Site latitude in degrees (-90 to 90)
    
    Returns:
        Solar elevation angle in degrees
    """
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90 degrees, got {latitude}")
    
    # Solar declination at winter solstice
    declination = -23.5 if latitude >= 0 else 23.5
    
    # Calculate solar elevation at noon
    # For northern hemisphere winter solstice (Dec 21)
    if latitude >= 0:
        solar_elevation = 90 - latitude - 23.5
    else:
        # For southern hemisphere winter solstice (Jun 21)
        solar_elevation = 90 + latitude - 23.5
    
    return max(0, solar_elevation)  # Ensure non-negative


def calculate_solar_elevation(latitude: float, day_of_year: int, hour: float) -> float:
    """
    Calculate solar elevation angle for a given time and location.
    
    Args:
        latitude: Site latitude in degrees
        day_of_year: Day number (1-365)
        hour: Hour of day in decimal (0-24, e.g., 13.5 for 1:30 PM)
    
    Returns:
        Solar elevation angle in degrees
    """
    if not 1 <= day_of_year <= 365:
        raise ValueError("Day of year must be between 1 and 365")
    
    if not 0 <= hour <= 24:
        raise ValueError("Hour must be between 0 and 24")
    
    # Convert to radians
    lat_rad = math.radians(latitude)
    
    # Solar declination (simplified equation)
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
    decl_rad = math.radians(declination)
    
    # Hour angle (0 at solar noon)
    hour_angle = 15 * (hour - 12)  # 15 degrees per hour
    ha_rad = math.radians(hour_angle)
    
    # Solar elevation angle
    sin_elevation = (math.sin(lat_rad) * math.sin(decl_rad) + 
                     math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad))
    
    # Clamp to valid range [-1, 1] to handle potential floating-point precision errors
    # that could occur in edge cases near sunrise/sunset
    elevation = math.degrees(math.asin(max(-1, min(1, sin_elevation))))
    
    return max(0, elevation)  # Return 0 if sun is below horizon


def calculate_solar_azimuth(latitude: float, day_of_year: int, hour: float) -> float:
    """
    Calculate solar azimuth angle for a given time and location.
    
    Args:
        latitude: Site latitude in degrees
        day_of_year: Day number (1-365)
        hour: Hour of day in decimal (0-24)
    
    Returns:
        Solar azimuth angle in degrees (0 = North, 90 = East, 180 = South, 270 = West)
    """
    lat_rad = math.radians(latitude)
    
    # Solar declination
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
    decl_rad = math.radians(declination)
    
    # Hour angle
    hour_angle = 15 * (hour - 12)
    ha_rad = math.radians(hour_angle)
    
    # Calculate elevation first
    elevation = calculate_solar_elevation(latitude, day_of_year, hour)
    elev_rad = math.radians(elevation)
    
    if elevation <= 0:
        return 0  # Sun below horizon
    
    # Solar azimuth
    sin_azimuth = (math.cos(decl_rad) * math.sin(ha_rad)) / math.cos(elev_rad)
    sin_azimuth = max(-1, min(1, sin_azimuth))  # Clamp to valid range
    
    azimuth = math.degrees(math.asin(sin_azimuth))
    
    # Adjust azimuth to 0-360 range
    cos_azimuth = (math.sin(decl_rad) - math.sin(lat_rad) * math.sin(elev_rad)) / (math.cos(lat_rad) * math.cos(elev_rad))
    
    if cos_azimuth < 0:
        azimuth = 180 - azimuth
    elif azimuth < 0:
        azimuth = 360 + azimuth
    
    return azimuth


def get_optimal_tilt_angle(latitude: float) -> float:
    """
    Calculate optimal tilt angle for maximum annual energy production.
    
    Rule of thumb: Optimal tilt ≈ latitude for fixed-tilt systems
    
    Args:
        latitude: Site latitude in degrees
    
    Returns:
        Recommended tilt angle in degrees
    """
    return abs(latitude)
