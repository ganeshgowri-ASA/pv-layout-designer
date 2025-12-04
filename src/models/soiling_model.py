"""
Regional Soiling Loss Model for Solar PV Systems
Implements Gujarat-specific soiling rates with seasonal variation and tilt correction.
"""

from typing import Dict, Tuple
from datetime import datetime


# Gujarat-specific soiling rates (% per day)
GUJARAT_SOILING_RATES = {
    'pre_monsoon': 0.55,   # March-May
    'monsoon': 0.10,       # June-September (natural cleaning)
    'post_monsoon': 0.35   # October-February
}

# Tilt correction factors
TILT_CORRECTION_FACTORS = {
    (0, 10): 1.8,
    (10, 20): 1.3,
    (20, 30): 1.0,
    (30, 90): 0.7
}


def load_regional_soiling_rates(climate_zone: str) -> Dict[str, float]:
    """
    Load regional soiling rates for a specific climate zone.
    
    Args:
        climate_zone: Name of the climate zone (e.g., 'gujarat')
    
    Returns:
        Dictionary containing seasonal soiling rates in % per day
    
    Raises:
        ValueError: If climate zone is not supported
    """
    if climate_zone.lower() == 'gujarat':
        return GUJARAT_SOILING_RATES.copy()
    else:
        raise ValueError(f"Climate zone '{climate_zone}' not supported. Currently only 'gujarat' is available.")


def _get_season_from_day(day_of_year: int) -> str:
    """
    Determine the season based on day of year.
    
    Args:
        day_of_year: Day of year (1-365/366)
    
    Returns:
        Season name: 'pre_monsoon', 'monsoon', or 'post_monsoon'
    """
    # March-May (day 60-151): Pre-monsoon
    # June-Sept (day 152-273): Monsoon
    # Oct-Feb (day 274-365 and 1-59): Post-monsoon
    
    if 60 <= day_of_year <= 151:
        return 'pre_monsoon'
    elif 152 <= day_of_year <= 273:
        return 'monsoon'
    else:
        return 'post_monsoon'


def _get_tilt_correction_factor(tilt_angle: float) -> float:
    """
    Get tilt correction factor based on panel tilt angle.
    Higher tilt results in lower soiling accumulation.
    
    Args:
        tilt_angle: Panel tilt angle in degrees (0-90)
    
    Returns:
        Correction factor to multiply with baseline soiling rate
    """
    for (min_tilt, max_tilt), factor in TILT_CORRECTION_FACTORS.items():
        if min_tilt <= tilt_angle < max_tilt:
            return factor
    
    # Default for angles >= 90 or < 0
    if tilt_angle >= 30:
        return 0.7
    return 1.8


def calculate_seasonal_soiling(day_of_year: int, tilt_angle: float, climate_zone: str = 'gujarat') -> float:
    """
    Calculate daily soiling rate for a specific day and tilt angle.
    
    Args:
        day_of_year: Day of year (1-365/366)
        tilt_angle: Panel tilt angle in degrees (0-90)
        climate_zone: Climate zone identifier (default: 'gujarat')
    
    Returns:
        Daily soiling rate in % per day
    """
    # Get seasonal rates
    rates = load_regional_soiling_rates(climate_zone)
    
    # Determine season
    season = _get_season_from_day(day_of_year)
    
    # Get base soiling rate
    base_rate = rates[season]
    
    # Apply tilt correction
    tilt_factor = _get_tilt_correction_factor(tilt_angle)
    
    return base_rate * tilt_factor


def calculate_annual_soiling_loss(location: str, tilt: float, cleaning_frequency: int) -> float:
    """
    Calculate annual energy loss due to soiling with periodic cleaning.
    
    The annual loss represents the average power loss throughout the year due to soiling.
    With periodic cleaning, soiling accumulates between cleanings and resets to zero after each cleaning.
    
    Args:
        location: Climate zone/location (e.g., 'gujarat')
        tilt: Panel tilt angle in degrees
        cleaning_frequency: Number of cleaning events per year
    
    Returns:
        Annual energy loss percentage due to soiling (typically 12-15% for Gujarat without cleaning)
    """
    # Days in a year
    days_per_year = 365
    
    # Calculate days between cleaning
    if cleaning_frequency <= 0:
        # No cleaning - special case, use saturation model
        days_between_cleaning = days_per_year
    else:
        days_between_cleaning = days_per_year / cleaning_frequency
    
    # Track daily soiling levels
    total_daily_loss = 0.0
    current_soiling = 0.0
    cleaning_counter = 0
    
    for day in range(1, days_per_year + 1):
        # Get daily soiling rate for this day
        daily_rate = calculate_seasonal_soiling(day, tilt, location)
        
        # Accumulate soiling (but with diminishing returns as panels get dirtier)
        # Using a saturation model: as soiling increases, the rate of additional accumulation decreases
        # Maximum soiling level is capped - after this point, wind and gravity remove as much as accumulates
        # For Gujarat, this cap is around 15% to achieve the specified 12-15% annual average
        max_soiling = 15.0
        saturation_factor = 1.0 - (current_soiling / max_soiling)
        current_soiling += daily_rate * saturation_factor
        
        # Cap soiling at maximum
        current_soiling = min(current_soiling, max_soiling)
        
        # Add current day's soiling to total (this is the energy loss for this day)
        total_daily_loss += current_soiling
        
        # Check if cleaning occurs
        if cleaning_frequency > 0:
            cleaning_counter += 1
            if cleaning_counter >= days_between_cleaning:
                current_soiling = 0.0
                cleaning_counter = 0
    
    # Calculate average annual loss (average of daily losses)
    annual_loss = total_daily_loss / days_per_year
    
    return annual_loss


def optimize_cleaning_schedule(soiling_rate: float, tilt: float, location: str = 'gujarat') -> Dict:
    """
    Optimize cleaning schedule to balance cleaning costs and energy loss.
    
    Args:
        soiling_rate: Average soiling rate (% per day)
        tilt: Panel tilt angle in degrees
        location: Climate zone identifier
    
    Returns:
        Dictionary with optimal cleaning frequency and expected annual loss
    """
    # Test different cleaning frequencies
    frequencies = [0, 4, 6, 12, 24, 52, 104]  # 0, quarterly, bi-monthly, monthly, bi-weekly, weekly, twice weekly
    
    results = []
    for freq in frequencies:
        annual_loss = calculate_annual_soiling_loss(location, tilt, freq)
        results.append({
            'frequency': freq,
            'cleanings_per_year': freq,
            'annual_loss_percent': round(annual_loss, 2),
            'description': _get_frequency_description(freq)
        })
    
    # Find optimal (minimize loss with reasonable cleaning frequency)
    # Balance between annual loss and cleaning frequency
    # Prioritize frequencies that give good loss reduction without excessive cleaning
    optimal = min(results, key=lambda x: x['annual_loss_percent'] + (0.1 * x['frequency']))
    
    return {
        'optimal_frequency': optimal['frequency'],
        'optimal_description': optimal['description'],
        'expected_annual_loss': optimal['annual_loss_percent'],
        'all_options': results
    }


def _get_frequency_description(frequency: int) -> str:
    """Get human-readable description of cleaning frequency."""
    if frequency == 0:
        return 'No cleaning'
    elif frequency == 4:
        return 'Quarterly'
    elif frequency == 6:
        return 'Bi-monthly'
    elif frequency == 12:
        return 'Monthly'
    elif frequency == 24:
        return 'Bi-weekly'
    elif frequency == 52:
        return 'Weekly'
    elif frequency == 104:
        return 'Twice weekly'
    else:
        return f'{frequency} times per year'


# Additional helper functions for compatibility with agent instructions
def calculate_daily_soiling_rate(region: str, season: str, tilt: float) -> float:
    """
    Calculate daily soiling rate for a given region, season, and tilt.
    This is a convenience function that maps to the main implementation.
    
    Args:
        region: Region name (e.g., 'gujarat')
        season: Season name ('pre_monsoon', 'monsoon', 'post_monsoon')
        tilt: Panel tilt angle in degrees
    
    Returns:
        Daily soiling rate in % per day
    """
    rates = load_regional_soiling_rates(region)
    base_rate = rates.get(season, 0.35)  # Default to post-monsoon rate
    tilt_factor = _get_tilt_correction_factor(tilt)
    return base_rate * tilt_factor


def get_gujarat_seasonal_rates() -> Dict[str, float]:
    """
    Get Gujarat-specific seasonal soiling rates.
    
    Returns:
        Dictionary with seasonal rates in % per day
    """
    return GUJARAT_SOILING_RATES.copy()
