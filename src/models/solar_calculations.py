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
        freq='h'  # Use lowercase 'h' for hour (pandas 2.2+ compatibility)
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
