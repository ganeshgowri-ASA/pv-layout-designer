# Quick Start Guide - SESSION-06 Shading Analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/pv-layout-designer.git
cd pv-layout-designer

# Checkout the feature branch
git checkout feature/06-shading-analysis

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest tests/test_shading_model.py -v

# Run with coverage
pytest tests/test_shading_model.py -v --cov=src/models/shading_model

# Validate syntax
python -m py_compile src/models/shading_model.py
```

## Running the Streamlit App

```bash
# Start the application
streamlit run src/app.py

# The app will open in your browser at http://localhost:8501
```

## Using the Application

### Tab 1: Daily Shading Analysis
1. Configure layout parameters in the sidebar:
   - Row Pitch (m)
   - Module Length (m)
   - Tilt Angle (°)
   - Latitude and Longitude

2. Select a date using the date picker

3. View hourly shading analysis with:
   - Power loss chart
   - Sun elevation chart
   - Summary metrics
   - Detailed hourly data table

### Tab 2: Winter Solstice Analysis
1. Click "Generate Winter Solstice Report"

2. View worst-case scenario (December 21) with:
   - Critical hours loss (9 AM - 3 PM)
   - Maximum loss
   - Daily average loss
   - Hourly breakdown chart

### Tab 3: Annual Profile
1. Click "Generate Annual Profile"

2. View seasonal comparison:
   - Winter Solstice losses
   - Summer Solstice losses
   - Equinox losses
   - Annual average
   - Seasonal comparison bar chart

## Python API Usage

### Basic Shading Calculation

```python
from src.models.shading_model import calculate_inter_row_shading

# Calculate shading for specific sun position
shading = calculate_inter_row_shading(
    row_pitch=5.0,        # meters
    module_length=2.0,    # meters
    tilt_angle=22.0,      # degrees
    sun_altitude=43.5     # degrees
)

print(f"Shading fraction: {shading:.2%}")
```

### Hourly Analysis

```python
from src.models.shading_model import calculate_hourly_shading

layout = {
    'row_pitch': 5.0,
    'module_length': 2.0,
    'tilt_angle': 22.0
}

# Analyze for specific date
hourly_data = calculate_hourly_shading(
    layout=layout,
    date='2024-12-21',  # Winter solstice
    lat=22.0,           # Gujarat latitude
    lon=72.0            # Gujarat longitude
)

# Process results
for hour in hourly_data:
    print(f"Hour {hour['hour']:02d}: "
          f"Sun elevation={hour['sun_elevation']:.1f}°, "
          f"Loss={hour['power_loss']:.1f}%")
```

### Winter Solstice Report

```python
from src.models.shading_model import generate_winter_solstice_report

report = generate_winter_solstice_report(
    layout=layout,
    lat=22.0,
    lon=72.0
)

print(f"Critical hours loss: {report['critical_hours_loss']:.2f}%")
print(f"Daily average loss: {report['daily_average_loss']:.2f}%")
```

### Annual Profile

```python
from src.models.shading_model import generate_shading_profile

location = {
    'latitude': 22.0,
    'longitude': 72.0
}

profile = generate_shading_profile(layout, location)

print(f"Annual average loss: {profile['annual_average_loss']:.2f}%")
print(f"Winter loss: {profile['winter_solstice']['average_loss']:.2f}%")
print(f"Summer loss: {profile['summer_solstice']['average_loss']:.2f}%")
```

### Bypass Diode Modeling

```python
from src.models.shading_model import calculate_electrical_loss

# Geometric shading to electrical loss
shading_fraction = 0.35  # 35% geometric shading
electrical_loss = calculate_electrical_loss(shading_fraction)

print(f"Geometric shading: {shading_fraction:.2%}")
print(f"Electrical loss: {electrical_loss:.2%}")
# Output shows non-linear relationship due to bypass diodes
```

## Example Configuration - Gujarat Solar Plant

```python
# Typical Gujarat solar plant configuration
layout = {
    'row_pitch': 5.0,      # 5 meters between rows
    'module_length': 2.0,  # 2 meter modules
    'tilt_angle': 22.0     # Latitude tilt for Gujarat
}

location = {
    'latitude': 22.0,      # ~22°N (Gujarat)
    'longitude': 72.0      # ~72°E (Gujarat)
}

# Generate complete analysis
profile = generate_shading_profile(layout, location)
```

## Understanding Results

### Shading Fraction
- **0.0**: No shading
- **0.5**: 50% of module shaded
- **1.0**: Fully shaded

### Electrical Loss (with 3 bypass diodes)
- **< 5%**: Linear loss (minor shading)
- **33%**: One diode bypassed (~33% loss)
- **66%**: Two diodes bypassed (~66% loss)
- **> 66%**: Full module loss (100%)

### Typical Daily Pattern
- **Early morning** (6-8 AM): High losses (low sun angle)
- **Mid-day** (9 AM - 3 PM): Low/zero losses (high sun angle)
- **Late afternoon** (4-6 PM): High losses (low sun angle)

### Seasonal Patterns
- **Winter**: Higher average losses (lower sun angles)
- **Summer**: Lower average losses (higher sun angles)
- **Equinox**: Moderate losses (mid-range sun angles)

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the repository root
cd /path/to/pv-layout-designer

# Install missing dependencies
pip install -r requirements.txt
```

### Test Failures
```bash
# Clean pytest cache
rm -rf .pytest_cache

# Reinstall numpy
pip install --upgrade numpy

# Run tests again
pytest tests/test_shading_model.py -v
```

### Streamlit Issues
```bash
# Clear streamlit cache
streamlit cache clear

# Run with specific port
streamlit run src/app.py --server.port 8502
```

## Support

For issues or questions:
- Review SESSION-06-SUMMARY.md for detailed documentation
- Check test files for usage examples
- Review the code comments in shading_model.py

## Next Steps

After SESSION-06, integrate with:
- **SESSION-04**: Enhanced solar position calculations
- **SESSION-05**: Real layout engine integration
- **SESSION-08**: Advanced 3D visualization

---

**Last Updated**: December 4, 2024
**Version**: 1.0.0
**Status**: Production Ready ✅
