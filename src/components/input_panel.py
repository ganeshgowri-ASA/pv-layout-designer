"""
Input Configuration Panel Component for PV Layout Designer

Provides Streamlit sidebar inputs for:
- Module specifications
- Layout configuration
- Site configuration
"""
import streamlit as st
import yaml
from pathlib import Path
from typing import Dict, Any

from src.utils.validators import (
    validate_module_dimensions,
    validate_tilt_angle,
    validate_gcr,
    validate_module_count,
    validate_height,
    validate_spacing,
)
from src.utils.constants import ORIENTATIONS, ROW_ORIENTATIONS


def load_default_settings() -> Dict[str, Any]:
    """Load default settings from config/settings.yaml"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'settings.yaml'
    
    try:
        with open(config_path, 'r') as f:
            settings = yaml.safe_load(f)
        return settings
    except FileNotFoundError:
        st.error(f"Configuration file not found: {config_path}")
        # Return fallback defaults
        return {
            'modules': {
                'length': 2278,
                'width': 1134,
                'thickness': 35,
                'power': 550,
                'efficiency': 21.4,
                'orientation': 'Portrait',
            },
            'layout': {
                'tilt_angle': 15,
                'height_from_ground': 1.0,
                'modules_per_structure': 28,
                'gcr': 0.40,
                'row_orientation': 'North-South',
            },
            'site': {
                'walkway_width': 3.0,
                'perimeter_margin': 3.0,
                'equipment_spacing': 5.0,
            },
            'constraints': {
                'module_length': {'min': 500, 'max': 3000},
                'module_width': {'min': 500, 'max': 2500},
                'module_thickness': {'min': 30, 'max': 50},
                'module_power': {'min': 200, 'max': 800},
                'module_efficiency': {'min': 15.0, 'max': 25.0},
                'tilt_angle': {'min': 0, 'max': 90},
                'height_from_ground': {'min': 0.5, 'max': 3.0},
                'modules_per_structure': {'min': 1, 'max': 100},
                'gcr': {'min': 0.20, 'max': 0.70},
                'walkway_width': {'min': 2.0, 'max': 10.0},
                'perimeter_margin': {'min': 1.0, 'max': 10.0},
                'equipment_spacing': {'min': 3.0, 'max': 15.0},
            }
        }


def render_input_panel() -> Dict[str, Any]:
    """
    Render configuration inputs in Streamlit sidebar.
    
    Returns:
        dict: Configuration dictionary with keys:
            - 'module': Module specifications
            - 'layout': Layout configuration
            - 'site': Site configuration
    """
    # Load settings
    settings = load_default_settings()
    defaults = settings.get('modules', {})
    layout_defaults = settings.get('layout', {})
    site_defaults = settings.get('site', {})
    constraints = settings.get('constraints', {})
    
    config = {
        'module': {},
        'layout': {},
        'site': {}
    }
    
    # Module Specifications Section
    with st.expander("📐 Module Specifications", expanded=True):
        st.markdown("*Configure solar module physical properties*")
        
        # Module dimensions
        module_length = st.number_input(
            "Module Length (mm)",
            min_value=constraints.get('module_length', {}).get('min', 500),
            max_value=constraints.get('module_length', {}).get('max', 3000),
            value=defaults.get('length', 2278),
            step=1,
            help="Typical bifacial modules: 2278mm (portrait)"
        )
        
        module_width = st.number_input(
            "Module Width (mm)",
            min_value=constraints.get('module_width', {}).get('min', 500),
            max_value=constraints.get('module_width', {}).get('max', 2500),
            value=defaults.get('width', 1134),
            step=1,
            help="Typical bifacial modules: 1134mm"
        )
        
        module_thickness = st.number_input(
            "Module Thickness (mm)",
            min_value=constraints.get('module_thickness', {}).get('min', 30),
            max_value=constraints.get('module_thickness', {}).get('max', 50),
            value=defaults.get('thickness', 35),
            step=1,
            help="Standard thickness including frame: 35-40mm"
        )
        
        # Validate dimensions
        is_valid, error_msg = validate_module_dimensions(
            module_length, 
            module_width, 
            module_thickness,
            min_length=constraints.get('module_length', {}).get('min', 500),
            max_length=constraints.get('module_length', {}).get('max', 3000),
            min_width=constraints.get('module_width', {}).get('min', 500),
            max_width=constraints.get('module_width', {}).get('max', 2500),
            min_thickness=constraints.get('module_thickness', {}).get('min', 30),
            max_thickness=constraints.get('module_thickness', {}).get('max', 50),
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Module electrical specs
        module_power = st.number_input(
            "Module Power (Wp)",
            min_value=constraints.get('module_power', {}).get('min', 200),
            max_value=constraints.get('module_power', {}).get('max', 800),
            value=defaults.get('power', 550),
            step=10,
            help="Rated peak power at STC conditions"
        )
        
        module_efficiency = st.number_input(
            "Module Efficiency (%)",
            min_value=constraints.get('module_efficiency', {}).get('min', 15.0),
            max_value=constraints.get('module_efficiency', {}).get('max', 25.0),
            value=defaults.get('efficiency', 21.4),
            step=0.1,
            format="%.1f",
            help="Module conversion efficiency (e.g., 21.4% for high-efficiency bifacial)"
        )
        
        # Orientation
        orientation = st.radio(
            "Module Orientation",
            options=ORIENTATIONS,
            index=ORIENTATIONS.index(defaults.get('orientation', 'Portrait')),
            horizontal=True,
            help="Portrait: Longer dimension vertical, Landscape: Longer dimension horizontal"
        )
        
        # Show calculated module area
        module_area = (module_length * module_width) / 1_000_000  # Convert mm² to m²
        st.metric(
            "Module Area",
            f"{module_area:.2f} m²",
            help="Calculated from length × width"
        )
        
        # Store module config
        config['module'] = {
            'length': module_length,
            'width': module_width,
            'thickness': module_thickness,
            'power': module_power,
            'efficiency': module_efficiency,
            'orientation': orientation,
            'area': module_area,
        }
    
    # Layout Configuration Section
    with st.expander("🏗️ Layout Configuration", expanded=True):
        st.markdown("*Configure array layout and structure parameters*")
        
        # Tilt angle
        tilt_angle = st.slider(
            "Tilt Angle (°)",
            min_value=constraints.get('tilt_angle', {}).get('min', 0),
            max_value=constraints.get('tilt_angle', {}).get('max', 90),
            value=layout_defaults.get('tilt_angle', 15),
            step=1,
            help="Recommended: 15° for Gujarat (latitude ~23°N)"
        )
        
        # Validate tilt angle
        is_valid, error_msg = validate_tilt_angle(
            tilt_angle,
            min_angle=constraints.get('tilt_angle', {}).get('min', 0),
            max_angle=constraints.get('tilt_angle', {}).get('max', 90),
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Height from ground
        height_from_ground = st.number_input(
            "Height from Ground (m)",
            min_value=constraints.get('height_from_ground', {}).get('min', 0.5),
            max_value=constraints.get('height_from_ground', {}).get('max', 3.0),
            value=layout_defaults.get('height_from_ground', 1.0),
            step=0.1,
            format="%.1f",
            help="Ground clearance at lowest edge (accounting for tilt)"
        )
        
        # Validate height
        is_valid, error_msg = validate_height(
            height_from_ground,
            min_height=constraints.get('height_from_ground', {}).get('min', 0.5),
            max_height=constraints.get('height_from_ground', {}).get('max', 3.0),
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Modules per structure
        modules_per_structure = st.number_input(
            "Modules per Structure",
            min_value=constraints.get('modules_per_structure', {}).get('min', 1),
            max_value=constraints.get('modules_per_structure', {}).get('max', 100),
            value=layout_defaults.get('modules_per_structure', 28),
            step=1,
            help="Typical configurations: 14, 28, 42, 56 modules (2 strings)"
        )
        
        # Validate module count
        is_valid, error_msg = validate_module_count(
            modules_per_structure,
            min_count=constraints.get('modules_per_structure', {}).get('min', 1),
            max_count=constraints.get('modules_per_structure', {}).get('max', 100),
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # GCR
        gcr = st.slider(
            "GCR (Ground Coverage Ratio)",
            min_value=constraints.get('gcr', {}).get('min', 0.20),
            max_value=constraints.get('gcr', {}).get('max', 0.70),
            value=layout_defaults.get('gcr', 0.40),
            step=0.01,
            format="%.2f",
            help="Ratio of module area to total ground area. Lower = more spacing"
        )
        
        # Validate GCR
        is_valid, error_msg = validate_gcr(
            gcr,
            min_gcr=constraints.get('gcr', {}).get('min', 0.20),
            max_gcr=constraints.get('gcr', {}).get('max', 0.70),
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Row orientation
        row_orientation = st.selectbox(
            "Row Orientation",
            options=ROW_ORIENTATIONS,
            index=ROW_ORIENTATIONS.index(layout_defaults.get('row_orientation', 'North-South')),
            help="North-South recommended for most latitudes to minimize shading"
        )
        
        # Show calculated pitch (row-to-row spacing)
        if orientation == 'Portrait':
            module_length_m = module_length / 1000
        else:
            module_length_m = module_width / 1000
        
        # Pitch calculation based on GCR
        if gcr > 0:
            pitch = module_length_m / gcr
            st.metric(
                "Calculated Row Pitch",
                f"{pitch:.2f} m",
                help="Row-to-row center distance based on GCR"
            )
        
        # Store layout config
        config['layout'] = {
            'tilt_angle': tilt_angle,
            'height_from_ground': height_from_ground,
            'modules_per_structure': modules_per_structure,
            'gcr': gcr,
            'row_orientation': row_orientation,
        }
    
    # Site Configuration Section
    with st.expander("🏭 Site Configuration", expanded=True):
        st.markdown("*Configure site-specific parameters and clearances*")
        
        # Walkway width
        walkway_width = st.number_input(
            "Walkway Width (m)",
            min_value=constraints.get('walkway_width', {}).get('min', 2.0),
            max_value=constraints.get('walkway_width', {}).get('max', 10.0),
            value=site_defaults.get('walkway_width', 3.0),
            step=0.5,
            format="%.1f",
            help="Width of maintenance access paths between array blocks"
        )
        
        # Validate walkway width
        is_valid, error_msg = validate_spacing(
            walkway_width,
            min_spacing=constraints.get('walkway_width', {}).get('min', 2.0),
            max_spacing=constraints.get('walkway_width', {}).get('max', 10.0),
            name="Walkway width"
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Perimeter margin
        perimeter_margin = st.number_input(
            "Perimeter Margin (m)",
            min_value=constraints.get('perimeter_margin', {}).get('min', 1.0),
            max_value=constraints.get('perimeter_margin', {}).get('max', 10.0),
            value=site_defaults.get('perimeter_margin', 3.0),
            step=0.5,
            format="%.1f",
            help="Setback distance from site boundary to first module row"
        )
        
        # Validate perimeter margin
        is_valid, error_msg = validate_spacing(
            perimeter_margin,
            min_spacing=constraints.get('perimeter_margin', {}).get('min', 1.0),
            max_spacing=constraints.get('perimeter_margin', {}).get('max', 10.0),
            name="Perimeter margin"
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Equipment spacing
        equipment_spacing = st.number_input(
            "Equipment Spacing (m)",
            min_value=constraints.get('equipment_spacing', {}).get('min', 3.0),
            max_value=constraints.get('equipment_spacing', {}).get('max', 15.0),
            value=site_defaults.get('equipment_spacing', 5.0),
            step=0.5,
            format="%.1f",
            help="Spacing around inverters, transformers, and other equipment"
        )
        
        # Validate equipment spacing
        is_valid, error_msg = validate_spacing(
            equipment_spacing,
            min_spacing=constraints.get('equipment_spacing', {}).get('min', 3.0),
            max_spacing=constraints.get('equipment_spacing', {}).get('max', 15.0),
            name="Equipment spacing"
        )
        if not is_valid:
            st.error(f"❌ {error_msg}")
        
        # Store site config
        config['site'] = {
            'walkway_width': walkway_width,
            'perimeter_margin': perimeter_margin,
            'equipment_spacing': equipment_spacing,
        }
    
    # Add a reset button
    if st.button("🔄 Reset to Defaults", help="Reset all inputs to default values"):
        st.rerun()
    
    return config
