# SESSION-05: Core Layout Engine - Implementation Documentation

## Overview

This session implements the core layout engine for the PV Layout Designer application. The layout engine is responsible for:
- Calculating optimal row-to-row spacing based on solar angles
- Placing PV modules within site boundaries
- Optimizing layout for target Ground Coverage Ratio (GCR)
- Handling irregular site shapes and perimeter margins

## Implementation Summary

### Files Created

1. **src/utils/geometry.py** - Spatial calculation utilities
2. **src/models/solar_calculations.py** - Solar angle calculations
3. **src/components/layout_engine.py** - Core placement algorithm
4. **tests/test_layout_engine.py** - Comprehensive test suite (30 tests)
5. **src/app.py** - Streamlit demo application
6. **requirements.txt** - Project dependencies

### Key Features Implemented

#### 1. Row Pitch Calculation
Formula: `R = L×cos(β) + L×sin(β)/tan(α)`

Where:
- R = Row pitch (spacing between rows)
- L = Module length (in direction of tilt)
- β = Tilt angle (degrees)
- α = Solar elevation angle (degrees)

This ensures no inter-row shading at winter solstice (worst case scenario).

#### 2. Module Placement Algorithm

The `place_modules()` function:
1. Applies perimeter margins to get usable area
2. Calculates solar elevation angle based on latitude
3. Computes row pitch for no-shading spacing
4. Places modules row-by-row from south to north
5. Checks each module is within usable polygon boundaries
6. Returns comprehensive layout data including positions, capacity, and GCR

#### 3. GCR Optimization

Ground Coverage Ratio (GCR) = Module Length / Row Pitch

The system:
- Calculates actual GCR based on no-shading requirements
- Supports target GCR range of 0.2 - 0.7
- Balances between maximizing capacity and minimizing shading

#### 4. Solar Calculations

Winter solstice angle calculation for worst-case shading:
- Northern Hemisphere: `α = 90° - latitude - 23.5°`
- Southern Hemisphere: `α = 90° + latitude - 23.5°`

Also includes hourly solar elevation and azimuth calculations for detailed analysis.

## Testing Results

All 30 tests pass successfully:

### Test Coverage

1. **Row Pitch Calculation (5 tests)**
   - Basic calculation with standard parameters
   - High tilt angle scenarios
   - Low solar elevation (high latitude)
   - Zero tilt (flat modules)
   - Invalid input validation

2. **GCR Calculation (3 tests)**
   - Standard GCR calculation
   - Range validation
   - Invalid input handling

3. **Usable Area (4 tests)**
   - Rectangular sites with margins
   - Small margins
   - Excessive margins (edge case)
   - Zero margin

4. **Module Count Estimation (5 tests)**
   - Basic estimation
   - High GCR scenarios
   - Low GCR scenarios
   - Zero area edge case
   - Invalid GCR validation

5. **Module Placement (7 tests)**
   - Rectangular site placement
   - Small site handling
   - Irregular polygon support
   - Capacity calculation accuracy
   - No-overlap verification
   - Boundary containment
   - Excessive margin handling

6. **Layout Optimization (3 tests)**
   - Basic optimization
   - Different GCR targets
   - Invalid GCR handling

7. **Solar Calculations (3 tests)**
   - Gujarat latitude (23°N)
   - Equator (0°)
   - High latitude (50°N)

## Usage Examples

### Basic Layout Generation

```python
from src.components.layout_engine import place_modules

# Define site (100m x 100m square)
site_coords = [(0, 0), (100, 0), (100, 100), (0, 100)]

# Configuration
config = {
    'latitude': 23.0225,      # Ahmedabad, Gujarat
    'module_length': 2.278,   # meters
    'module_width': 1.134,    # meters
    'module_power': 545,      # watts
    'tilt_angle': 15,         # degrees
    'walkway_width': 3.0,     # meters
    'margin': 5.0             # meters
}

# Generate layout
result = place_modules(site_coords, config)

print(f"Total Modules: {result['total_modules']}")
print(f"System Capacity: {result['capacity_kwp']:.1f} kWp")
print(f"Actual GCR: {result['actual_gcr']:.2%}")
```

### Layout Optimization

```python
from src.components.layout_engine import optimize_layout

module_dims = {
    'length': 2.278,
    'width': 1.134,
    'power': 545
}

result = optimize_layout(
    site_area=10000,        # m²
    module_dims=module_dims,
    target_gcr=0.40,
    latitude=23.0,
    tilt_angle=15
)

print(f"Recommended Modules: {result['recommended_modules']}")
print(f"Row Pitch: {result['row_pitch']:.2f} m")
print(f"Capacity: {result['capacity_kwp']:.1f} kWp")
```

### Running the Demo App

```bash
streamlit run src/app.py
```

The app provides an interactive interface to:
- Configure site and module parameters
- Generate optimized layouts
- View detailed metrics and module positions
- Experiment with different configurations

## Performance

The implementation meets all performance requirements:

- **Layout Generation**: < 1 second for 10,000 m² site
- **Module Placement**: Handles 2000+ modules efficiently
- **Test Suite**: All 30 tests complete in < 1 second

## Technical Notes

### Coordinate System
- Uses Cartesian coordinates (x, y) in meters
- South-to-north row placement (y-axis)
- West-to-east module placement (x-axis)
- Assumes north-south row orientation for optimal performance

### Boundary Handling
- Modules must have center point within usable area
- Requires 80% module area overlap with usable polygon
- Supports irregular polygon shapes via Shapely library

### Margin Application
- Negative buffer applied to site polygon
- Returns empty polygon if margin too large
- Usable area calculation accounts for all boundaries

## Dependencies

Core libraries:
- **shapely** >= 2.0.0 - Polygon operations and spatial calculations
- **numpy** >= 1.24.0 - Numerical computations
- **streamlit** >= 1.28.0 - Web application framework
- **pytest** >= 7.4.0 - Testing framework

## Future Enhancements

Potential improvements for future sessions:
1. Support for east-west row orientation
2. Bifacial module optimization
3. Tracker system support
4. Equipment placement zones (inverters, DCDB)
5. Cable routing optimization
6. Multi-zone layout support
7. Terrain elevation handling

## Integration Points

This layout engine integrates with:
- **SESSION-03**: Input panel for configuration parameters
- **SESSION-04**: Solar calculations for shading analysis
- **SESSION-06**: Shading analysis module
- **SESSION-08**: Visualization components
- **SESSION-09**: Database for storing layouts
- **SESSION-10**: Export functionality

## Validation

The implementation has been validated through:
1. ✅ 30 comprehensive unit tests (all passing)
2. ✅ Python syntax validation (py_compile)
3. ✅ Manual testing with demo application
4. ✅ Edge case handling (small sites, irregular shapes, excessive margins)
5. ✅ Performance testing (< 1s for typical sites)

## Success Criteria Met

- ✅ Layout algorithm places modules correctly
- ✅ No overlaps or boundary violations
- ✅ GCR calculated accurately based on solar angles
- ✅ Walkways properly integrated
- ✅ Module count and capacity accurate
- ✅ Works with different site shapes
- ✅ Performance: < 2 seconds for 10,000 m² site

## Conclusion

SESSION-05 has been successfully implemented with a robust, well-tested core layout engine that forms the foundation for the PV Layout Designer application. The algorithm correctly handles:
- Solar-angle-based spacing calculations
- Irregular site boundaries
- Perimeter margins
- Module placement optimization
- Comprehensive error handling

All code follows best practices with comprehensive documentation, type hints, and extensive test coverage.
