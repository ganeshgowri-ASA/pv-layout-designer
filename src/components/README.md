# Visualizer Component - SESSION-08

## Overview
Multi-view visualization component for PV Layout Designer providing 2D top view, side profile, and 3D isometric views.

## Features

### 1. 2D Top View (`render_top_view`)
- Interactive Folium map with module overlay
- Color-coded components:
  - Modules: Blue (#4A90E2)
  - Walkways: Grey (#9E9E9E)
  - Inverters: Red (#FF5252)
  - Transformers: Green (#4CAF50)
  - Margins: Yellow (#FFD600)
- Site boundary visualization
- Equipment markers with popups
- Layer controls for toggling visibility

### 2. Side Profile View (`render_side_view`)
- Matplotlib-based side profile
- Shows tilt angle correctly
- Displays row spacing
- Ground clearance visualization
- Support structure representation
- Configurable dimensions

### 3. 3D Isometric View (`render_3d_isometric`)
- PyDeck interactive 3D visualization
- Extruded module geometry based on tilt
- Interactive controls (zoom, pan, rotate)
- Equipment markers in 3D space
- Configurable pitch and bearing
- Tooltip with module information

### 4. Shading Overlay (`add_shading_overlay`)
- Overlay shading analysis on 2D map
- Opacity varies with shade percentage
- Time-based shading information
- Integration with SESSION-06 shading analysis

## Usage

### Basic Usage

```python
from src.components.visualizer import render_all_views, VisualizerConfig

# Define layout data
layout = {
    'center': [23.0225, 72.5714],  # [lat, lon]
    'modules': [...],
    'walkways': [...],
    'equipment': [...],
    'boundaries': [...],
    'tilt_angle': 20,
    'module_length': 2.0,
    'ground_clearance': 0.5,
    'num_rows': 3,
    'row_spacing': 5.0
}

# Create configuration (optional)
config = VisualizerConfig(
    map_center=(23.0225, 72.5714),
    zoom_start=15,
    initial_view_state={
        'pitch': 45,
        'bearing': 0
    }
)

# Render all views
views = render_all_views(layout, config=config)

# Access individual views
top_view_map = views['top_view']
side_view_fig = views['side_view']
isometric_3d = views['3d_view']
```

### With Shading Analysis

```python
# Include shading data
shading_analysis = {
    'shaded_areas': [
        {
            'coords': [[lat1, lon1], [lat2, lon2], ...],
            'shade_percentage': 30.5,
            'time': '09:00'
        }
    ]
}

# Render with shading overlay
views = render_all_views(layout, shading_analysis=shading_analysis)
```

### Streamlit Integration

```python
import streamlit as st
from src.components.visualizer import render_all_views, display_in_streamlit

# Render views
views = render_all_views(st.session_state['layout'])

# Display in tabs
display_in_streamlit(views)
```

## Layout Data Structure

### Required Fields
```python
layout = {
    'center': [lat, lon],  # Site center coordinates
}
```

### Optional Fields
```python
layout = {
    'boundaries': [[lat, lon], ...],  # Site boundary polygon
    'modules': [
        {
            'coords': [[lat, lon], ...],  # Module polygon
            'tilt': 20,  # degrees
            'azimuth': 180,  # degrees
            'length': 2.0,  # meters
            'ground_clearance': 0.5  # meters
        }
    ],
    'walkways': [
        {
            'coords': [[lat, lon], ...]  # Walkway polygon
        }
    ],
    'equipment': [
        {
            'type': 'inverter' | 'transformer',
            'position': [lat, lon],
            'name': 'Equipment Name'
        }
    ],
    'margins': [
        {
            'coords': [[lat, lon], ...]  # Margin polygon
        }
    ],
    # Side view specific
    'tilt_angle': 20,  # degrees
    'module_length': 2.0,  # meters
    'module_height': 0.04,  # meters (thickness)
    'ground_clearance': 0.5,  # meters
    'num_rows': 3,
    'row_spacing': 5.0  # meters
}
```

## Configuration Options

### VisualizerConfig

```python
config = VisualizerConfig(
    map_center=(lat, lon),  # Default: (23.0225, 72.5714)
    zoom_start=15,  # Map zoom level
    map_style='OpenStreetMap',  # Folium map style
    figure_size=(12, 6),  # Matplotlib figure size
    dpi=100,  # Figure DPI
    initial_view_state={
        'latitude': lat,
        'longitude': lon,
        'zoom': 15,
        'pitch': 45,  # 3D view pitch angle
        'bearing': 0   # 3D view bearing angle
    }
)
```

## Color Coding

| Component | Color | Hex Code |
|-----------|-------|----------|
| Modules | Blue | #4A90E2 |
| Walkways | Grey | #9E9E9E |
| Inverters | Red | #FF5252 |
| Transformers | Green | #4CAF50 |
| Margins | Yellow | #FFD600 |
| Shading | Dark Grey | #424242 |

## Dependencies

Required packages (see requirements.txt):
- folium >= 0.14.0
- pydeck >= 0.8.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0
- pandas >= 2.0.0
- streamlit >= 1.28.0 (for UI integration)

## Testing

Run tests with:
```bash
pytest tests/test_visualizer.py -v
```

All 22 tests should pass:
- Configuration tests (2)
- Top view rendering tests (5)
- Side view rendering tests (3)
- 3D isometric tests (3)
- Shading overlay tests (2)
- Render all views tests (2)
- Color constants tests (2)
- Edge cases tests (3)

## Integration

### Required by:
- SESSION-10: Export (needs rendered views as PNG/SVG)

### Depends on:
- SESSION-05: Layout Engine (layout data structure)
- SESSION-06: Shading Analysis (optional shading overlay)
- SESSION-07: Soiling Model (future integration)

## Export Capabilities

Views can be exported to various formats:

### Folium Map (2D Top View)
```python
top_view.save('top_view.html')
```

### Matplotlib Figure (Side Profile)
```python
side_view.savefig('side_profile.png', dpi=300, bbox_inches='tight')
side_view.savefig('side_profile.svg', format='svg')
```

### PyDeck (3D Isometric)
```python
# In Streamlit:
st.pydeck_chart(isometric_3d)
```

## Examples

See `src/app.py` for a complete Streamlit application example demonstrating all visualization features.

## Notes

- All coordinate systems use WGS84 (lat/lon)
- Module coordinates should be in [lat, lon] format
- Tilt angles are in degrees (0-90)
- Distances are in meters
- The 3D view uses meters converted to millimeters for better visibility

## Future Enhancements

- [ ] Animation support for time-based shading
- [ ] Export to CAD formats (DXF)
- [ ] Virtual reality (VR) view option
- [ ] Real-time shadow simulation
- [ ] Performance optimization for large layouts (>10,000 modules)
