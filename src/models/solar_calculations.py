"""
Solar calculations for PV layout design.

Provides sun position and angle calculations for shading analysis.
This module supports both pvlib-based calculations (when available)
and fallback math-based calculations.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Try to import pvlib and pytz for accurate calculations
try:
    import pvlib
    import pytz
    import pandas as pd
    PVLIB_AVAILABLE = True
except ImportError:
    PVLIB_AVAILABLE = False

# Import constants
try:
    from ..utils.constants import (
        EARTH_TILT,
        GUJARAT_LATITUDE,
        GUJARAT_LONGITUDE,
        WINTER_SOLSTICE_DAY,
        DEFAULT_TIMEZONE,
        CRITICAL_START_HOUR,
        CRITICAL_END_HOUR,
    )
except ImportError:
    # Fallback defaults
    EARTH_TILT = 23.5
    GUJARAT_LATITUDE = 23.0225
    GUJARAT_LONGITUDE = 72.5714
    WINTER_SOLSTICE_DAY = 355
    DEFAULT_TIMEZONE = 'Asia/Kolkata'
    CRITICAL_START_HOUR = 9
    CRITICAL_END_HOUR = 15


def get_winter_solstice_angle(latitude: float) -> float:
    """
    Calculate solar elevation angle at winter solstice noon.

    This is the worst-case scenario for shading analysis.
    Formula: alpha = 90 - |latitude| - 23.5 (solar declination at winter solstice)

    For Northern Hemisphere: alpha = 90 - latitude - 23.5
    For Southern Hemisphere: alpha = 90 + latitude - 23.5

    Args:
        latitude: Site latitude in degrees (-90 to 90)

    Returns:
        Solar elevation angle in degrees
    """
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90 degrees, got {latitude}")

    # Calculate solar elevation at noon
    if latitude >= 0:
        # For northern hemisphere winter solstice (Dec 21)
        solar_elevation = 90 - latitude - EARTH_TILT
    else:
        # For southern hemisphere winter solstice (Jun 21)
        solar_elevation = 90 + latitude - EARTH_TILT

    return max(0, solar_elevation)  # Ensure non-negative


def calculate_solar_elevation(
    latitude: float,
    longitude_or_day: float = None,
    day_or_hour: int = None,
    hour: float = None,
    dt: datetime = None
) -> float:
    """
    Calculate solar elevation angle for a given time and location.

    Supports multiple calling conventions:
    - calculate_solar_elevation(lat, lon, day_of_year, hour) - 4-arg version
    - calculate_solar_elevation(lat, day_of_year, hour) - 3-arg version
    - calculate_solar_elevation(lat, lon, dt=datetime) - datetime version

    Args:
        latitude: Site latitude in degrees
        longitude_or_day: Longitude or day_of_year depending on call style
        day_or_hour: Day of year or hour depending on call style
        hour: Hour of day in decimal (0-24)
        dt: Optional datetime object

    Returns:
        Solar elevation angle in degrees
    """
    # Handle datetime-based call
    if dt is not None:
        day_of_year = dt.timetuple().tm_yday
        hour_val = dt.hour + dt.minute / 60.0
    elif hour is not None:
        # 4-arg version: lat, lon, day, hour
        day_of_year = day_or_hour
        hour_val = hour
    elif day_or_hour is not None and isinstance(day_or_hour, (int, float)):
        # 3-arg version: lat, day, hour
        day_of_year = int(longitude_or_day)
        hour_val = day_or_hour
    else:
        raise ValueError("Invalid arguments for calculate_solar_elevation")

    # Validate inputs
    if not 1 <= day_of_year <= 366:
        raise ValueError("Day of year must be between 1 and 366")

    if not 0 <= hour_val <= 24:
        raise ValueError("Hour must be between 0 and 24")

    # Convert to radians
    lat_rad = math.radians(latitude)

    # Solar declination (simplified equation)
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
    decl_rad = math.radians(declination)

    # Hour angle (0 at solar noon)
    hour_angle = 15 * (hour_val - 12)  # 15 degrees per hour
    ha_rad = math.radians(hour_angle)

    # Solar elevation angle
    sin_elevation = (math.sin(lat_rad) * math.sin(decl_rad) +
                     math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad))

    # Clamp to valid range [-1, 1] to handle floating-point precision errors
    elevation = math.degrees(math.asin(max(-1, min(1, sin_elevation))))

    return max(0, elevation)  # Return 0 if sun is below horizon


def calculate_solar_azimuth(
    latitude: float,
    longitude_or_day: float = None,
    day_or_hour: int = None,
    hour: float = None,
    dt: datetime = None
) -> float:
    """
    Calculate solar azimuth angle for a given time and location.

    Args:
        latitude: Site latitude in degrees
        longitude_or_day: Longitude or day_of_year depending on call style
        day_or_hour: Day of year or hour depending on call style
        hour: Hour of day in decimal (0-24)
        dt: Optional datetime object

    Returns:
        Solar azimuth angle in degrees (0=North, 90=East, 180=South, 270=West)
    """
    # Handle datetime-based call
    if dt is not None:
        day_of_year = dt.timetuple().tm_yday
        hour_val = dt.hour + dt.minute / 60.0
    elif hour is not None:
        # 4-arg version: lat, lon, day, hour
        day_of_year = day_or_hour
        hour_val = hour
    elif day_or_hour is not None and isinstance(day_or_hour, (int, float)):
        # 3-arg version: lat, day, hour
        day_of_year = int(longitude_or_day)
        hour_val = day_or_hour
    else:
        raise ValueError("Invalid arguments for calculate_solar_azimuth")

    lat_rad = math.radians(latitude)

    # Solar declination
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))
    decl_rad = math.radians(declination)

    # Hour angle
    hour_angle = 15 * (hour_val - 12)
    ha_rad = math.radians(hour_angle)

    # Calculate elevation first
    elevation = calculate_solar_elevation(latitude, day_of_year, hour_val)
    elev_rad = math.radians(elevation)

    if elevation <= 0:
        return 180.0  # Default to south when sun is below horizon

    # Solar azimuth calculation
    cos_azimuth = ((math.sin(decl_rad) - math.sin(lat_rad) * math.sin(elev_rad)) /
                   (math.cos(lat_rad) * math.cos(elev_rad)))

    cos_azimuth = max(-1, min(1, cos_azimuth))
    azimuth = math.degrees(math.acos(cos_azimuth))

    # Adjust for afternoon (hour_angle > 0)
    if hour_angle > 0:
        azimuth = 360 - azimuth

    return azimuth


def calculate_sun_path(
    latitude: float,
    longitude: float,
    date: str
) -> List[Dict]:
    """
    Calculate hourly sun path for a given day.

    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        date: Date string in format 'YYYY-MM-DD'

    Returns:
        List of dictionaries with hourly sun position data
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    sun_path = []

    for hour in range(24):
        current_time = dt.replace(hour=hour, minute=0, second=0)
        day_of_year = current_time.timetuple().tm_yday

        elevation = calculate_solar_elevation(latitude, day_of_year, hour)
        azimuth = calculate_solar_azimuth(latitude, day_of_year, hour)

        sun_path.append({
            'hour': hour,
            'elevation': elevation,
            'azimuth': azimuth,
            'timestamp': current_time.isoformat()
        })

    return sun_path


def calculate_critical_hours_elevation(
    lat: float,
    lon: float,
    date: str = "2024-12-21"
) -> Dict:
    """
    Get sun elevations for critical hours (9 AM - 3 PM) on winter solstice.

    Critical hours are defined as 9 AM to 3 PM, which are the most important
    hours for energy generation.

    Args:
        lat: Latitude in degrees (-90 to 90, positive North)
        lon: Longitude in degrees (-180 to 180, positive East)
        date: Date string in format "YYYY-MM-DD" (default: winter solstice)

    Returns:
        Dictionary mapping hours to solar positions:
        {
            9: {'elevation': float, 'azimuth': float},
            10: {'elevation': float, 'azimuth': float},
            ...
            15: {'elevation': float, 'azimuth': float}
        }
    """
    dt = datetime.strptime(date, "%Y-%m-%d")
    day_of_year = dt.timetuple().tm_yday

    result = {}
    for hour in range(CRITICAL_START_HOUR, CRITICAL_END_HOUR + 1):
        elevation = calculate_solar_elevation(lat, day_of_year, hour)
        azimuth = calculate_solar_azimuth(lat, day_of_year, hour)

        result[hour] = {
            'elevation': elevation,
            'azimuth': azimuth
        }

    return result


def get_optimal_tilt_angle(latitude: float) -> float:
    """
    Calculate optimal tilt angle for maximum annual energy production.

    Rule of thumb: Optimal tilt is approximately equal to latitude for fixed-tilt systems.

    Args:
        latitude: Site latitude in degrees

    Returns:
        Recommended tilt angle in degrees
    """
    return abs(latitude)
