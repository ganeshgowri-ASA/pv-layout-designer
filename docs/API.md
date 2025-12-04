# API Documentation: PV Layout Designer

## Components

### map_selector.py

#### `render_map_selector() -> dict`

Renders an interactive map with drawing tools for site selection.

**Returns:**
```python
{
    'coordinates': [(lat1, lon1), (lat2, lon2), ...],  # Polygon vertices
    'area_sqm': float,  # Area in square meters
    'center': (lat, lon),  # Centroid of the polygon
    'bounds': [[south, west], [north, east]]  # Bounding box
}
```

**Example:**
```python
from components.map_selector import render_map_selector

result = render_map_selector()
if result:
    print(f"Selected area: {result['area_sqm']:.2f} sq meters")
```

### input_panel.py

#### `render_input_panel() -> dict`

Renders configuration inputs for PV layout parameters.

**Returns:**
```python
{
    'module_type': str,
    'module_width': float,
    'module_height': float,
    'tilt': float,
    'azimuth': float,
    'gcr': float,
    'row_spacing': float
}
```

### layout_engine.py

#### `generate_layout(site_bounds, config) -> dict`

Generates optimized PV panel layout.

**Parameters:**
- `site_bounds`: List of (lat, lon) tuples defining site boundary
- `config`: Configuration dict from input_panel

**Returns:**
```python
{
    'panels': [
        {'id': int, 'position': (x, y), 'rotation': float},
        ...
    ],
    'panel_count': int,
    'total_capacity_kw': float,
    'coverage_area_sqm': float
}
```

## Models

### SoilingModel

```python
model = SoilingModel(region_data)
loss = model.calculate_soiling_loss(days_since_cleaning=30)
```

### ShadingModel

```python
model = ShadingModel(latitude=23.0, longitude=72.5)
loss = model.calculate_inter_row_shading(tilt=15, gcr=0.4, datetime=dt)
```

## Utilities

### geometry.py

- `calculate_polygon_area(coordinates)` - Calculate area in sq meters
- `calculate_polygon_centroid(coordinates)` - Get centroid
- `get_bounding_box(coordinates)` - Get [[south, west], [north, east]]

### validators.py

- `validate_coordinates(coordinates)` - Check lat/lon ranges
- `validate_polygon(coordinates)` - Validate polygon has >= 3 points
- `validate_tilt_angle(tilt)` - Check 0-90 degrees
- `validate_gcr(gcr)` - Check 0-1 range
