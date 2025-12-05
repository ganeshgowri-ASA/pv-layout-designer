"""
Physical and geographical constants for PV layout design.

This module contains fundamental constants used across the application
for solar calculations, geographical defaults, and physical parameters.
"""

# Orientation options
ORIENTATION_PORTRAIT = "Portrait"
ORIENTATION_LANDSCAPE = "Landscape"
ORIENTATIONS = [ORIENTATION_PORTRAIT, ORIENTATION_LANDSCAPE]

# Row orientation options
ROW_ORIENTATION_NS = "North-South"
ROW_ORIENTATION_EW = "East-West"
ROW_ORIENTATIONS = [ROW_ORIENTATION_NS, ROW_ORIENTATION_EW]

# Physical constants
GRAVITY = 9.81  # m/s^2
SOLAR_CONSTANT = 1367  # W/m^2 (Solar constant)

# Conversion factors
MM_TO_M = 0.001
M_TO_MM = 1000

# Solar and Earth Constants
EARTH_TILT = 23.5  # Earth's axial tilt in degrees

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
CRITICAL_END_HOUR = 15    # 3 PM (inclusive range: 9,10,11,12,13,14,15 = 7 hours)
