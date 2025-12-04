"""
Physical and geographical constants for PV layout design.

This module contains fundamental constants used across the application
for solar calculations, geographical defaults, and physical parameters.
"""

# Solar and Earth Constants
EARTH_TILT = 23.5  # Earth's axial tilt in degrees
SOLAR_CONSTANT = 1367  # Solar constant in W/m²

# Gujarat, India - Default Location
GUJARAT_LATITUDE = 23.0225  # Latitude in degrees (North)
GUJARAT_LONGITUDE = 72.5714  # Longitude in degrees (East)

# Key Dates (Day of Year)
WINTER_SOLSTICE_DAY = 355  # December 21 (typically day 355 in non-leap years)
SUMMER_SOLSTICE_DAY = 172  # June 21 (typically day 172)
SPRING_EQUINOX_DAY = 80    # March 21 (typically day 80)
AUTUMN_EQUINOX_DAY = 266   # September 23 (typically day 266)

# Timezone
DEFAULT_TIMEZONE = 'Asia/Kolkata'  # Indian Standard Time (IST)

# Critical Hours for Shading Analysis
CRITICAL_START_HOUR = 9   # 9 AM
CRITICAL_END_HOUR = 15    # 3 PM (exclusive, so 9 AM to 3 PM gives 7 hours: 9,10,11,12,13,14,15)
