"""Constants used throughout the PV Layout Designer."""

# Default map settings
DEFAULT_LATITUDE = 23.0225  # Gujarat, India
DEFAULT_LONGITUDE = 72.5714
DEFAULT_ZOOM = 13

# Common PV module dimensions (in meters)
MODULE_DIMENSIONS = {
    "standard_60_cell": {"width": 0.992, "height": 1.640},
    "standard_72_cell": {"width": 0.992, "height": 2.000},
    "bifacial_72_cell": {"width": 1.134, "height": 2.278},
    "thin_film": {"width": 1.200, "height": 0.600},
}

# Standard module power ratings (in Watts)
MODULE_POWER = {
    "standard_60_cell": 300,
    "standard_72_cell": 400,
    "bifacial_72_cell": 550,
    "thin_film": 120,
}

# Ground Coverage Ratio limits
GCR_MIN = 0.2
GCR_MAX = 0.8
GCR_DEFAULT = 0.4

# Tilt angle limits
TILT_MIN = 0
TILT_MAX = 60
TILT_DEFAULT = 15

# Row spacing constraints (in meters)
MIN_ROW_SPACING = 0.5
MAX_ROW_SPACING = 10.0

# Azimuth (degrees from North)
AZIMUTH_DEFAULT = 180  # South-facing

# Conversion factors
SQFT_TO_SQM = 0.092903
ACRE_TO_SQM = 4046.86
HECTARE_TO_SQM = 10000

# Map tile providers
TILE_PROVIDERS = {
    "OpenStreetMap": "OpenStreetMap",
    "CartoDB Positron": "CartoDB positron",
    "CartoDB Dark": "CartoDB dark_matter",
    "Esri Satellite": "Esri.WorldImagery",
}
