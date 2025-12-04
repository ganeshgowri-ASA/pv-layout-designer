"""
SESSION-06: Inter-Row Shading Analysis with Electrical Loss Modeling

This module implements geometric shading calculations and electrical loss modeling
for solar PV arrays with bypass diode considerations.
"""

from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime

from src.models.solar_calculations import calculate_sun_path, calculate_solar_elevation


def calculate_inter_row_shading(
    row_pitch: float,
    module_length: float,
    tilt_angle: float,
    sun_altitude: float
) -> float:
    """
    Calculate shading fraction for given sun position.
    
    This function calculates the geometric shading of one row on the next row
    based on the sun's altitude angle and the array geometry.
    
    Args:
        row_pitch: Distance between rows in meters
        module_length: Length of module in meters
        tilt_angle: Tilt angle of modules in degrees
        sun_altitude: Sun elevation angle in degrees (0-90)
        
    Returns:
        Shading fraction from 0.0 (no shade) to 1.0 (fully shaded)
        
    Algorithm:
        1. Calculate shadow length cast on ground
        2. Calculate module horizontal footprint
        3. Determine clear distance to next row
        4. Calculate shading if shadow exceeds clear distance
    """
    # Handle edge cases
    if sun_altitude <= 0:
        return 1.0  # Fully shaded when sun is below horizon
    
    if sun_altitude >= 90:
        return 0.0  # No shading when sun is directly overhead
    
    if row_pitch <= 0 or module_length <= 0:
        raise ValueError("row_pitch and module_length must be positive")
    
    if not (0 <= tilt_angle <= 90):
        raise ValueError("tilt_angle must be between 0 and 90 degrees")
    
    # Convert angles to radians for calculation
    tilt_rad = np.radians(tilt_angle)
    altitude_rad = np.radians(sun_altitude)
    
    # Shadow length on ground = (module height) / tan(sun altitude)
    # Module height = module_length * sin(tilt_angle)
    module_height = module_length * np.sin(tilt_rad)
    shadow_length = module_height / np.tan(altitude_rad)
    
    # Module horizontal footprint on ground
    module_footprint = module_length * np.cos(tilt_rad)
    
    # Clear distance to next row
    clear_distance = row_pitch - module_footprint
    
    # Calculate shading
    if shadow_length > clear_distance:
        # Shadow extends into next row
        shaded_length = shadow_length - clear_distance
        shading_fraction = min(shaded_length / module_length, 1.0)
        return shading_fraction
    
    return 0.0  # No shading


def calculate_electrical_loss(
    shading_fraction: float,
    bypass_diodes: int = 3
) -> float:
    """
    Convert geometric shading to electrical loss using bypass diode model.
    
    This function models the non-linear electrical losses due to shading,
    accounting for bypass diode activation at different shading levels.
    
    Args:
        shading_fraction: Geometric shading fraction (0.0 to 1.0)
        bypass_diodes: Number of bypass diodes per module (typically 3)
        
    Returns:
        Electrical power loss as fraction (0.0 to 1.0)
        
    Model:
        - <5%: Linear loss (minor shading, no diode activation)
        - 33%: 1 diode bypass (~33% loss)
        - 66%: 2 diodes bypass (~66% loss)
        - >66%: Full module loss (100%)
    """
    if not (0 <= shading_fraction <= 1.0):
        raise ValueError("shading_fraction must be between 0 and 1")
    
    if bypass_diodes <= 0:
        raise ValueError("bypass_diodes must be positive")
    
    # Threshold for each diode section
    diode_threshold = 1.0 / bypass_diodes
    
    # Minor shading: linear loss
    if shading_fraction < 0.05:
        return shading_fraction
    
    # Calculate which diode sections are affected
    if shading_fraction < diode_threshold:
        # First diode section partially shaded
        # Use non-linear model: small shading causes disproportionate loss
        return diode_threshold
    
    # Multiple diode sections affected
    num_diodes_bypassed = int(shading_fraction / diode_threshold)
    
    if num_diodes_bypassed >= bypass_diodes:
        # All diodes bypassed - complete module loss
        return 1.0
    
    # Partial bypass of multiple diodes
    # Each bypassed diode contributes proportional loss
    base_loss = num_diodes_bypassed * diode_threshold
    
    # Add partial loss from current diode section
    remaining_fraction = shading_fraction - (num_diodes_bypassed * diode_threshold)
    if remaining_fraction > 0.05 * diode_threshold:
        # If significant shading in current section, bypass it too
        base_loss += diode_threshold
    
    return min(base_loss, 1.0)


def calculate_hourly_shading(
    layout: Dict,
    date: str,
    lat: float,
    lon: float
) -> List[Dict]:
    """
    Hourly shading analysis for entire day.
    
    This function calculates shading and electrical losses for each hour
    of the specified day, integrating with solar position calculations.
    
    Args:
        layout: Dictionary containing:
            - row_pitch: Distance between rows (m)
            - module_length: Module length (m)
            - tilt_angle: Tilt angle (degrees)
        date: Date string in format 'YYYY-MM-DD'
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        List of dictionaries with hourly data:
            - hour: Hour of day (0-23)
            - sun_elevation: Solar elevation angle (degrees)
            - shading_fraction: Geometric shading (0-1)
            - electrical_loss: Electrical power loss (0-1)
    """
    # Get sun path for the day
    sun_path = calculate_sun_path(lat, lon, date)
    
    results = []
    
    for hour_data in sun_path:
        if hour_data['elevation'] > 0:  # Daytime only
            # Calculate geometric shading
            shading = calculate_inter_row_shading(
                row_pitch=layout['row_pitch'],
                module_length=layout['module_length'],
                tilt_angle=layout['tilt_angle'],
                sun_altitude=hour_data['elevation']
            )
            
            # Calculate electrical loss
            electrical_loss = calculate_electrical_loss(shading)
            
            results.append({
                'hour': hour_data['hour'],
                'sun_elevation': hour_data['elevation'],
                'shading_fraction': shading,
                'electrical_loss': electrical_loss,
                'power_loss': electrical_loss * 100  # As percentage
            })
    
    return results


def generate_shading_profile(
    layout: Dict,
    location: Dict
) -> Dict:
    """
    Annual shading analysis for key dates.
    
    This function analyzes shading for critical dates (winter solstice,
    summer solstice) and calculates annual average losses.
    
    Args:
        layout: Dictionary containing:
            - row_pitch: Distance between rows (m)
            - module_length: Module length (m)
            - tilt_angle: Tilt angle (degrees)
        location: Dictionary containing:
            - latitude: Latitude in degrees
            - longitude: Longitude in degrees
            
    Returns:
        Dictionary containing:
            - winter_solstice: Hourly data for Dec 21
            - summer_solstice: Hourly data for Jun 21
            - equinox: Hourly data for Mar 21
            - annual_average_loss: Average loss percentage
            - worst_case_loss: Maximum loss percentage
    """
    lat = location['latitude']
    lon = location['longitude']
    
    # Key dates for analysis
    winter_solstice = '2024-12-21'  # Worst case - lowest sun angle
    summer_solstice = '2024-06-21'  # Best case - highest sun angle
    equinox = '2024-03-21'  # Mid-case
    
    # Calculate hourly shading for each date
    winter_data = calculate_hourly_shading(layout, winter_solstice, lat, lon)
    summer_data = calculate_hourly_shading(layout, summer_solstice, lat, lon)
    equinox_data = calculate_hourly_shading(layout, equinox, lat, lon)
    
    # Calculate average losses
    def calculate_average_loss(data: List[Dict]) -> float:
        if not data:
            return 0.0
        total_loss = sum(d['electrical_loss'] for d in data)
        return (total_loss / len(data)) * 100  # As percentage
    
    winter_avg = calculate_average_loss(winter_data)
    summer_avg = calculate_average_loss(summer_data)
    equinox_avg = calculate_average_loss(equinox_data)
    
    # Annual average (weighted by season)
    annual_average_loss = (winter_avg * 0.25 + summer_avg * 0.25 + equinox_avg * 0.5)
    
    # Worst case loss
    all_losses = [d['electrical_loss'] * 100 for d in winter_data + summer_data + equinox_data]
    worst_case_loss = max(all_losses) if all_losses else 0.0
    
    return {
        'winter_solstice': {
            'date': winter_solstice,
            'hourly_data': winter_data,
            'average_loss': winter_avg
        },
        'summer_solstice': {
            'date': summer_solstice,
            'hourly_data': summer_data,
            'average_loss': summer_avg
        },
        'equinox': {
            'date': equinox,
            'hourly_data': equinox_data,
            'average_loss': equinox_avg
        },
        'annual_average_loss': annual_average_loss,
        'worst_case_loss': worst_case_loss
    }


def calculate_shadow_length(
    module_height: float,
    sun_elevation: float
) -> float:
    """
    Calculate shadow length cast by a module.
    
    Args:
        module_height: Height of the module in meters
        sun_elevation: Solar elevation angle in degrees
        
    Returns:
        Shadow length in meters
    """
    if sun_elevation <= 0:
        return float('inf')  # Infinite shadow when sun is below horizon
    
    if sun_elevation >= 90:
        return 0.0  # No shadow when sun is directly overhead
    
    if module_height < 0:
        raise ValueError("module_height must be non-negative")
    
    elevation_rad = np.radians(sun_elevation)
    shadow_length = module_height / np.tan(elevation_rad)
    
    return shadow_length


def analyze_inter_row_shading(
    layout: Dict,
    solar_position: Dict,
    datetime_obj: datetime
) -> Dict:
    """
    Analyze inter-row shading for a specific moment in time.
    
    Args:
        layout: Dictionary containing layout parameters
        solar_position: Dictionary with 'elevation' and 'azimuth' in degrees
        datetime_obj: Python datetime object
        
    Returns:
        Dictionary with shading analysis results
    """
    shading_fraction = calculate_inter_row_shading(
        row_pitch=layout['row_pitch'],
        module_length=layout['module_length'],
        tilt_angle=layout['tilt_angle'],
        sun_altitude=solar_position['elevation']
    )
    
    electrical_loss = calculate_electrical_loss(shading_fraction)
    
    module_height = layout['module_length'] * np.sin(np.radians(layout['tilt_angle']))
    shadow_length = calculate_shadow_length(module_height, solar_position['elevation'])
    
    return {
        'timestamp': datetime_obj.isoformat(),
        'sun_elevation': solar_position['elevation'],
        'sun_azimuth': solar_position.get('azimuth', 0),
        'shading_fraction': shading_fraction,
        'electrical_loss': electrical_loss,
        'power_loss_percent': electrical_loss * 100,
        'shadow_length': shadow_length,
        'module_height': module_height
    }


def model_bypass_diode_losses(shading_percentage: float) -> float:
    """
    Model bypass diode losses for a given shading percentage.
    
    This is a wrapper function for calculate_electrical_loss that accepts
    percentage input and returns percentage output.
    
    Args:
        shading_percentage: Shading as percentage (0-100)
        
    Returns:
        Power loss as percentage (0-100)
    """
    shading_fraction = shading_percentage / 100.0
    electrical_loss = calculate_electrical_loss(shading_fraction)
    return electrical_loss * 100.0


def generate_winter_solstice_report(layout: Dict, lat: float, lon: float = 0.0) -> Dict:
    """
    Generate worst-case shading analysis for winter solstice.
    
    Args:
        layout: Dictionary containing layout parameters
        lat: Latitude in degrees
        lon: Longitude in degrees (optional, defaults to 0)
        
    Returns:
        Dictionary with winter solstice analysis
    """
    winter_date = '2024-12-21'
    
    hourly_data = calculate_hourly_shading(
        layout=layout,
        date=winter_date,
        lat=lat,
        lon=lon
    )
    
    # Critical hours (9 AM to 3 PM)
    critical_hours = [d for d in hourly_data if 9 <= d['hour'] <= 15]
    
    # Calculate metrics
    if critical_hours:
        critical_avg_loss = sum(d['electrical_loss'] for d in critical_hours) / len(critical_hours) * 100
        max_loss = max(d['electrical_loss'] for d in critical_hours) * 100
    else:
        critical_avg_loss = 0.0
        max_loss = 0.0
    
    daily_avg_loss = sum(d['electrical_loss'] for d in hourly_data) / len(hourly_data) * 100 if hourly_data else 0.0
    
    return {
        'date': winter_date,
        'latitude': lat,
        'hourly_data': hourly_data,
        'critical_hours_loss': critical_avg_loss,
        'max_loss': max_loss,
        'daily_average_loss': daily_avg_loss,
        'total_daylight_hours': len(hourly_data)
    }
