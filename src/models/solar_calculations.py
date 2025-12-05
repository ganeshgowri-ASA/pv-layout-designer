"""
Solar position calculation functions for PV shading analysis.

This module provides accurate solar position calculations using the pvlib library,
which implements the NREL SPA (Solar Position Algorithm) for high-precision
sun position calculations.

Functions:
    calculate_solar_elevation: Calculate solar elevation angle in degrees
    calculate_solar_azimuth: Calculate solar azimuth angle in degrees
    get_winter_solstice_angle: Get solar elevation at winter solstice noon
    calculate_sun_path: Calculate hourly sun positions for entire day
    calculate_critical_hours_elevation: Get sun elevations for critical hours
"""

from datetime import datetime, timedelta
from typing import List, Dict
import pytz
import pvlib
import pandas as pd

from ..utils.constants import (
    EARTH_TILT,
    GUJARAT_LATITUDE,
    GUJARAT_LONGITUDE,
    WINTER_SOLSTICE_DAY,
    DEFAULT_TIMEZONE,
    CRITICAL_START_HOUR,
    CRITICAL_END_HOUR,
)


def calculate_solar_elevation(
    lat: float, lon: float, day_of_year: int, hour: float
) -> float:
    """
    Calculate solar elevation angle in degrees (0-90°).
    
    The elevation angle is measured from the horizon (0°) to directly overhead (90°).
    Negative values indicate the sun is below the horizon (nighttime).
    
    Args:
        lat: Latitude in degrees (-90 to 90, positive North)
        lon: Longitude in degrees (-180 to 180, positive East)
        day_of_year: Day of year (1-365/366)
        hour: Hour of day in decimal format (0.0-24.0, e.g., 13.5 = 1:30 PM)
    
    Returns:
        Solar elevation angle in degrees. Range: -90° to 90°
        Positive values indicate sun above horizon.
        
    Example:
        >>> # Solar noon on winter solstice in Gujarat
        >>> elevation = calculate_solar_elevation(23.0225, 72.5714, 355, 12.0)
        >>> print(f"Elevation: {elevation:.2f}°")
        Elevation: 43.48°
    """
    # Convert to datetime
    year = 2024  # Use a non-leap year for consistency
    dt = datetime(year, 1, 1) + timedelta(days=day_of_year - 1, hours=hour)
    
    # Localize to timezone
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    dt_local = tz.localize(dt)
    
    # Calculate solar position using pvlib
    solpos = pvlib.solarposition.get_solarposition(dt_local, lat, lon)
    
    # Return elevation (altitude) angle
    return float(solpos['elevation'].values[0])


def calculate_solar_azimuth(
    lat: float, lon: float, day_of_year: int, hour: float
) -> float:
    """
    Calculate solar azimuth angle in degrees (0-360°).
    
    The azimuth angle is measured clockwise from North:
    - 0° = North
    - 90° = East
    - 180° = South
    - 270° = West
    
    Args:
        lat: Latitude in degrees (-90 to 90, positive North)
        lon: Longitude in degrees (-180 to 180, positive East)
        day_of_year: Day of year (1-365/366)
        hour: Hour of day in decimal format (0.0-24.0)
    
    Returns:
        Solar azimuth angle in degrees. Range: 0° to 360°
        
    Example:
        >>> # Solar position at 10 AM on winter solstice
        >>> azimuth = calculate_solar_azimuth(23.0225, 72.5714, 355, 10.0)
        >>> print(f"Azimuth: {azimuth:.2f}°")
    """
    # Convert to datetime
    year = 2024
    dt = datetime(year, 1, 1) + timedelta(days=day_of_year - 1, hours=hour)
    
    # Localize to timezone
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    dt_local = tz.localize(dt)
    
    # Calculate solar position using pvlib
    solpos = pvlib.solarposition.get_solarposition(dt_local, lat, lon)
    
    # Return azimuth angle
    return float(solpos['azimuth'].values[0])


def get_winter_solstice_angle(latitude: float) -> float:
    """
    Calculate solar elevation at solar noon on winter solstice.
    
    Uses the simplified formula for solar elevation at solar noon:
    α = 90° - 23.5° - |latitude|
    
    This represents the worst-case scenario for solar elevation,
    which is critical for inter-row shading calculations.
    
    Args:
        latitude: Latitude in degrees (-90 to 90, positive North)
    
    Returns:
        Solar elevation angle at solar noon on winter solstice in degrees
        
    Example:
        >>> # Gujarat winter solstice angle
        >>> angle = get_winter_solstice_angle(23.0225)
        >>> print(f"Winter solstice angle: {angle:.2f}°")
        Winter solstice angle: 43.48°
    """
    # Formula: α = 90° - 23.5° - |latitude|
    angle = 90.0 - EARTH_TILT - abs(latitude)
    return angle


def calculate_sun_path(lat: float, lon: float, date: str) -> List[Dict]:
    """
    Return hourly sun positions for entire day.
    
    Calculates solar elevation and azimuth for each hour (0-23) on the specified date.
    This is useful for visualizing the sun path and understanding daily solar patterns.
    
    Args:
        lat: Latitude in degrees (-90 to 90, positive North)
        lon: Longitude in degrees (-180 to 180, positive East)
        date: Date string in format "YYYY-MM-DD"
    
    Returns:
        List of dictionaries containing hourly sun positions:
        [
            {'hour': 0, 'elevation': float, 'azimuth': float},
            {'hour': 1, 'elevation': float, 'azimuth': float},
            ...
            {'hour': 23, 'elevation': float, 'azimuth': float}
        ]
        
    Example:
        >>> # Get sun path for winter solstice
        >>> sun_path = calculate_sun_path(23.0225, 72.5714, "2024-12-21")
        >>> for pos in sun_path:
        ...     if pos['elevation'] > 0:
        ...         print(f"Hour {pos['hour']}: El={pos['elevation']:.1f}°, Az={pos['azimuth']:.1f}°")
    """
    # Parse the date
    dt = datetime.strptime(date, "%Y-%m-%d")
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    
    # Generate hourly timestamps for the entire day
    times = pd.date_range(
        start=tz.localize(dt),
        end=tz.localize(dt + timedelta(hours=23)),
        freq='h'  # Hourly frequency
    )
    
    # Calculate solar positions for all hours
    solpos = pvlib.solarposition.get_solarposition(times, lat, lon)
    
    # Format results
    sun_path = []
    for i, (idx, row) in enumerate(solpos.iterrows()):
        sun_path.append({
            'hour': i,
            'elevation': float(row['elevation']),
            'azimuth': float(row['azimuth'])
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
SESSION-04: Solar Position Calculations
Stub implementation for integration with SESSION-06
"""

from datetime import datetime
from typing import Dict, List
import math


def calculate_solar_elevation(latitude: float, longitude: float, dt: datetime) -> float:
    """
    Calculate solar elevation angle for given location and time.
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        dt: Datetime object
        
    Returns:
        Solar elevation angle in degrees
    """
    # Simplified solar elevation calculation
    # This is a stub - full implementation would use more accurate algorithms
    
    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour + dt.minute / 60.0
    
    # Declination angle (simplified)
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    
    # Hour angle
    solar_noon = 12.0
    hour_angle = 15 * (hour - solar_noon)
    
    # Solar elevation
    lat_rad = math.radians(latitude)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)
    
    sin_elevation = (math.sin(lat_rad) * math.sin(dec_rad) + 
                     math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad))
    
    elevation = math.degrees(math.asin(max(-1, min(1, sin_elevation))))
    
    return max(0, elevation)


def calculate_sun_path(latitude: float, longitude: float, date: str) -> List[Dict]:
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
        elevation = calculate_solar_elevation(latitude, longitude, current_time)
        
        sun_path.append({
            'hour': hour,
            'elevation': elevation,
            'timestamp': current_time.isoformat()
        })
    
    return sun_path


def calculate_critical_hours_elevation(
    lat: float, lon: float, date: str = "2024-12-21"
) -> Dict:
    """
    Get sun elevations for critical hours (9 AM - 3 PM) on winter solstice.
    
    Critical hours are defined as 9 AM to 3 PM, which are the most important
    hours for energy generation. Returns elevation and azimuth for each hour
    in this range on the specified date (default: winter solstice).
    
    Args:
        lat: Latitude in degrees (-90 to 90, positive North)
        lon: Longitude in degrees (-180 to 180, positive East)
        date: Date string in format "YYYY-MM-DD" (default: "2024-12-21" - winter solstice)
    
    Returns:
        Dictionary mapping hours to solar positions:
        {
            9: {'elevation': float, 'azimuth': float},
            10: {'elevation': float, 'azimuth': float},
            ...
            15: {'elevation': float, 'azimuth': float}
        }
        
    Example:
        >>> # Get critical hours for Gujarat on winter solstice
        >>> critical = calculate_critical_hours_elevation(23.0225, 72.5714)
        >>> for hour, pos in critical.items():
        ...     print(f"{hour}:00 - El: {pos['elevation']:.1f}°, Az: {pos['azimuth']:.1f}°")
    """
    # Parse the date
    dt = datetime.strptime(date, "%Y-%m-%d")
    tz = pytz.timezone(DEFAULT_TIMEZONE)
    
    # Generate timestamps for critical hours
    critical_hours = range(CRITICAL_START_HOUR, CRITICAL_END_HOUR + 1)
    times = [tz.localize(dt + timedelta(hours=h)) for h in critical_hours]
    times_index = pd.DatetimeIndex(times)
    
    # Calculate solar positions
    solpos = pvlib.solarposition.get_solarposition(times_index, lat, lon)
    
    # Format results
    result = {}
    for hour, (idx, row) in zip(critical_hours, solpos.iterrows()):
        result[hour] = {
            'elevation': float(row['elevation']),
            'azimuth': float(row['azimuth'])
        }
    
    return result
def calculate_solar_azimuth(latitude: float, longitude: float, dt: datetime) -> float:
    """
    Calculate solar azimuth angle for given location and time.
    
    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        dt: Datetime object
        
    Returns:
        Solar azimuth angle in degrees (0=North, 90=East, 180=South, 270=West)
    """
    # Simplified azimuth calculation
    # This is a stub - full implementation would use more accurate algorithms
    
    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour + dt.minute / 60.0
    
    # Declination angle
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    
    # Hour angle
    solar_noon = 12.0
    hour_angle = 15 * (hour - solar_noon)
    
    # Calculate azimuth (simplified)
    lat_rad = math.radians(latitude)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)
    elevation_rad = math.radians(calculate_solar_elevation(latitude, longitude, dt))
    
    if elevation_rad <= 0:
        return 180.0  # Default to south when sun is below horizon
    
    cos_azimuth = ((math.sin(dec_rad) - math.sin(lat_rad) * math.sin(elevation_rad)) / 
                   (math.cos(lat_rad) * math.cos(elevation_rad)))
    
    cos_azimuth = max(-1, min(1, cos_azimuth))
    azimuth = math.degrees(math.acos(cos_azimuth))
    
    # Adjust for afternoon (hour_angle > 0)
    if hour_angle > 0:
        azimuth = 360 - azimuth
    
    return azimuth
