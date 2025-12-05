"""
PV Layout Designer - Main Streamlit Application

Interactive PV layout design tool with Folium map visualization,
drawing tools for boundary selection, and real-time module placement.
"""

import streamlit as st
from pathlib import Path
import sys
import json

# Add src to Python path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import layout engine
try:
    from components.layout_engine import place_modules, optimize_layout
    LAYOUT_ENGINE_AVAILABLE = True
except ImportError as e:
    LAYOUT_ENGINE_AVAILABLE = False
    LAYOUT_ENGINE_ERROR = str(e)

# Import map viewer
try:
    from components.map_viewer import (
        create_interactive_map,
        add_site_boundary,
        add_modules_to_map,
        add_bop_component,
        calculate_boundary_from_params,
        meters_to_degrees,
        get_map_html
    )
    MAP_VIEWER_AVAILABLE = True
except ImportError as e:
    MAP_VIEWER_AVAILABLE = False
    MAP_VIEWER_ERROR = str(e)

# Import streamlit-folium for bidirectional communication
try:
    from streamlit_folium import st_folium, folium_static
    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError:
    STREAMLIT_FOLIUM_AVAILABLE = False


def init_session_state():
    """Initialize session state variables."""
    if 'layout' not in st.session_state:
        st.session_state['layout'] = None
    if 'drawn_boundary' not in st.session_state:
        st.session_state['drawn_boundary'] = None
    if 'bop_components' not in st.session_state:
        st.session_state['bop_components'] = []
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = (23.0225, 72.5714)


def render_sidebar():
    """Render the configuration sidebar and return parameters."""
    st.sidebar.header("Configuration")

    # Site parameters
    st.sidebar.subheader("Site Parameters")
    site_length = st.sidebar.number_input(
        "Site Length (m)", value=100.0, min_value=10.0, max_value=1000.0, step=5.0,
        help="East-West dimension of the site"
    )
    site_width = st.sidebar.number_input(
        "Site Width (m)", value=100.0, min_value=10.0, max_value=1000.0, step=5.0,
        help="North-South dimension of the site"
    )
    margin = st.sidebar.number_input(
        "Perimeter Margin (m)", value=5.0, min_value=0.0, max_value=20.0, step=0.5,
        help="Setback distance from site boundary"
    )

    st.sidebar.subheader("Site Location")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        latitude = st.number_input(
            "Latitude", value=23.0225, min_value=-90.0, max_value=90.0, step=0.0001,
            format="%.4f"
        )
    with col2:
        longitude = st.number_input(
            "Longitude", value=72.5714, min_value=-180.0, max_value=180.0, step=0.0001,
            format="%.4f"
        )

    # Update map center when location changes
    st.session_state['map_center'] = (latitude, longitude)

    # Module parameters
    st.sidebar.subheader("Module Specifications")
    module_length = st.sidebar.number_input(
        "Module Length (mm)", value=2278, min_value=1000, max_value=3000, step=1,
        help="Module dimension in tilt direction"
    )
    module_width = st.sidebar.number_input(
        "Module Width (mm)", value=1134, min_value=500, max_value=2000, step=1,
        help="Module dimension perpendicular to tilt"
    )
    module_power = st.sidebar.number_input(
        "Module Power (Wp)", value=545, min_value=100, max_value=1000, step=5
    )
    tilt_angle = st.sidebar.slider(
        "Tilt Angle (deg)", min_value=0, max_value=45, value=15,
        help="Module tilt angle from horizontal"
    )

    # Layout parameters
    st.sidebar.subheader("Layout Parameters")
    orientation = st.sidebar.selectbox(
        "Module Orientation",
        ["portrait", "landscape"],
        help="Portrait: long side in tilt direction"
    )
    walkway_width = st.sidebar.number_input(
        "Walkway Width (m)", value=3.0, min_value=0.0, max_value=10.0, step=0.5,
        help="Maintenance walkway between rows"
    )
    row_gap = st.sidebar.number_input(
        "Row Gap (m)", value=0.02, min_value=0.0, max_value=0.5, step=0.01,
        help="Gap between modules in same row"
    )
    modules_per_table = st.sidebar.number_input(
        "Modules per Table", value=20, min_value=1, max_value=50, step=1,
        help="Number of modules per mounting table"
    )

    # Convert mm to meters for calculations
    module_length_m = module_length / 1000.0
    module_width_m = module_width / 1000.0

    return {
        'site_length': site_length,
        'site_width': site_width,
        'margin': margin,
        'latitude': latitude,
        'longitude': longitude,
        'module_length': module_length_m,
        'module_width': module_width_m,
        'module_power': module_power,
        'tilt_angle': tilt_angle,
        'orientation': orientation,
        'walkway_width': walkway_width,
        'row_gap': row_gap,
        'modules_per_table': modules_per_table
    }


def render_stats_panel(layout_result: dict, site_area: float):
    """Render the statistics panel showing layout metrics."""
    st.markdown("### Layout Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Modules",
            f"{layout_result['total_modules']:,}",
            help="Number of PV modules placed"
        )

    with col2:
        capacity_mwp = layout_result['capacity_kwp'] / 1000
        if capacity_mwp >= 1:
            st.metric("System Capacity", f"{capacity_mwp:.2f} MWp")
        else:
            st.metric("System Capacity", f"{layout_result['capacity_kwp']:.1f} kWp")

    with col3:
        st.metric(
            "GCR",
            f"{layout_result['actual_gcr']:.1%}",
            help="Ground Coverage Ratio"
        )

    with col4:
        land_util = (layout_result['total_modules'] * layout_result['module_area'] / site_area) if site_area > 0 else 0
        st.metric(
            "Land Utilization",
            f"{land_util:.1%}",
            help="Percentage of site covered by modules"
        )

    # Additional details in expandable section
    with st.expander("Detailed Layout Information", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Spacing & Coverage:**")
            st.write(f"- Number of Rows: {layout_result['rows']}")
            st.write(f"- Avg Modules/Row: {layout_result['modules_per_row']:.1f}")
            st.write(f"- Row Pitch: {layout_result['row_pitch']:.2f} m")
            st.write(f"- Row Spacing: {layout_result['row_spacing']:.2f} m")
            st.write(f"- Usable Area: {layout_result['usable_area']:,.0f} m2")

        with col2:
            st.markdown("**Solar & Power:**")
            st.write(f"- Solar Elevation (Winter): {layout_result['solar_elevation']:.1f} deg")
            st.write(f"- Module Area: {layout_result['module_area']:.2f} m2")
            total_module_area = layout_result['total_modules'] * layout_result['module_area']
            st.write(f"- Total Module Area: {total_module_area:,.0f} m2")
            st.write(f"- Site Area: {site_area:,.0f} m2")


def render_map_with_layout(params: dict, layout_result: dict = None):
    """Render interactive map with site boundary and modules."""
    if not MAP_VIEWER_AVAILABLE:
        st.error(f"Map viewer not available: {MAP_VIEWER_ERROR}")
        return

    # Create interactive map
    center = (params['latitude'], params['longitude'])
    m = create_interactive_map(
        center=center,
        zoom=18,
        enable_drawing=True,
        enable_measure=True,
        enable_fullscreen=True
    )

    # Calculate and add site boundary
    boundary = calculate_boundary_from_params(
        params['latitude'],
        params['longitude'],
        params['site_length'],
        params['site_width']
    )
    m = add_site_boundary(m, boundary)

    # Add modules if layout is generated
    if layout_result and layout_result.get('modules'):
        # Calculate site origin (center of site in local coordinates)
        site_origin = (params['site_length'] / 2, params['site_width'] / 2)

        m = add_modules_to_map(
            m,
            layout_result['modules'],
            params['module_length'],
            params['module_width'],
            params['latitude'],
            params['longitude'],
            site_origin=site_origin
        )

    # Add BoP components if any
    for bop in st.session_state.get('bop_components', []):
        m = add_bop_component(
            m,
            bop['type'],
            bop['position'],
            bop.get('name'),
            bop.get('size')
        )

    # Render map using streamlit-folium or raw HTML
    if STREAMLIT_FOLIUM_AVAILABLE:
        map_data = st_folium(
            m,
            width=None,
            height=600,
            returned_objects=["all_drawings"],
            key="pv_layout_map"
        )

        # Capture drawn boundary from user
        if map_data and map_data.get("all_drawings"):
            drawings = map_data["all_drawings"]
            if drawings:
                # Get the last drawn shape
                last_drawing = drawings[-1]
                if last_drawing.get("geometry"):
                    geom = last_drawing["geometry"]
                    if geom.get("type") == "Polygon":
                        coords = geom["coordinates"][0]
                        # Convert from [lon, lat] to (lat, lon)
                        st.session_state['drawn_boundary'] = [
                            (coord[1], coord[0]) for coord in coords
                        ]
                        st.info("Boundary captured from drawing. Click 'Generate Layout' to use it.")
    else:
        # Fallback to raw HTML rendering
        st.components.v1.html(get_map_html(m), height=600, scrolling=False)
        st.info("Install streamlit-folium for interactive drawing: pip install streamlit-folium")


def render_bop_panel():
    """Render Balance of Plant component panel."""
    st.markdown("### BoP Components")

    with st.expander("Add BoP Component", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            bop_type = st.selectbox(
                "Component Type",
                ["inverter", "transformer", "dcdb", "porta_cabin", "walkway", "cable_tray"]
            )
            bop_name = st.text_input("Name (optional)", placeholder="e.g., Inverter-1")

        with col2:
            bop_lat = st.number_input(
                "Latitude", value=st.session_state['map_center'][0],
                format="%.6f", key="bop_lat"
            )
            bop_lon = st.number_input(
                "Longitude", value=st.session_state['map_center'][1],
                format="%.6f", key="bop_lon"
            )

        if st.button("Add Component"):
            component = {
                'type': bop_type,
                'position': (bop_lat, bop_lon),
                'name': bop_name if bop_name else None
            }
            st.session_state['bop_components'].append(component)
            st.success(f"Added {bop_type}")
            st.rerun()

    # Show existing components
    if st.session_state.get('bop_components'):
        st.markdown("**Placed Components:**")
        for i, bop in enumerate(st.session_state['bop_components']):
            col1, col2 = st.columns([3, 1])
            with col1:
                name = bop.get('name') or bop['type'].replace('_', ' ').title()
                st.write(f"{i+1}. {name} @ ({bop['position'][0]:.4f}, {bop['position'][1]:.4f})")
            with col2:
                if st.button("Remove", key=f"remove_bop_{i}"):
                    st.session_state['bop_components'].pop(i)
                    st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_session_state()

    # Header
    st.title("☀️ PV Layout Designer")
    st.markdown("Interactive Solar PV Layout Design with Satellite Map Visualization")

    # Check dependencies
    if not LAYOUT_ENGINE_AVAILABLE:
        st.error(f"Layout engine not available: {LAYOUT_ENGINE_ERROR}")
        st.info("Please check that all dependencies are installed correctly.")

    # Render sidebar and get parameters
    params = render_sidebar()

    # Calculate site metrics
    site_area = params['site_length'] * params['site_width']

    # Create site coordinates for layout engine (local coordinates in meters)
    site_coords = [
        (0, 0),
        (params['site_length'], 0),
        (params['site_length'], params['site_width']),
        (0, params['site_width'])
    ]

    # Main content area
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # Site info bar
        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("Site Area", f"{site_area:,.0f} m2")
        info_col2.metric("Location", f"{params['latitude']:.4f}, {params['longitude']:.4f}")
        info_col3.metric("Module Size", f"{params['module_length']*1000:.0f} x {params['module_width']*1000:.0f} mm")

        # Generate Layout button
        generate_col1, generate_col2 = st.columns([1, 4])
        with generate_col1:
            generate_clicked = st.button("Generate Layout", type="primary", use_container_width=True)

        with generate_col2:
            if st.session_state.get('drawn_boundary'):
                st.caption("Using drawn boundary from map")
            else:
                st.caption("Using rectangular site from parameters")

        # Handle layout generation
        if generate_clicked:
            if not LAYOUT_ENGINE_AVAILABLE:
                st.error("Layout engine not available. Cannot generate layout.")
            else:
                with st.spinner("Calculating optimal layout..."):
                    # Prepare configuration
                    config = {
                        'latitude': params['latitude'],
                        'module_length': params['module_length'],
                        'module_width': params['module_width'],
                        'module_power': params['module_power'],
                        'tilt_angle': params['tilt_angle'],
                        'orientation': params['orientation'],
                        'walkway_width': params['walkway_width'],
                        'margin': params['margin']
                    }

                    # Use drawn boundary if available, otherwise use rectangular site
                    if st.session_state.get('drawn_boundary'):
                        # Convert lat/lon boundary to local meters (approximate)
                        # This is a simplified conversion - in production use proper projection
                        drawn = st.session_state['drawn_boundary']
                        center_lat = sum(c[0] for c in drawn) / len(drawn)
                        center_lon = sum(c[1] for c in drawn) / len(drawn)

                        local_coords = []
                        for lat, lon in drawn:
                            # Convert to meters from center
                            y_m = (lat - center_lat) * 111320
                            x_m = (lon - center_lon) * 111320 * abs(
                                __import__('math').cos(__import__('math').radians(center_lat))
                            )
                            local_coords.append((x_m, y_m))

                        layout_result = place_modules(local_coords, config)
                    else:
                        layout_result = place_modules(site_coords, config)

                    # Store result
                    st.session_state['layout'] = layout_result

                    if layout_result.get('error'):
                        st.warning(f"Layout generated with warning: {layout_result['error']}")
                    else:
                        st.success(f"Layout generated: {layout_result['total_modules']:,} modules, {layout_result['capacity_kwp']:.1f} kWp")

        # Display statistics if layout exists
        if st.session_state.get('layout'):
            render_stats_panel(st.session_state['layout'], site_area)

        st.markdown("---")

        # Render interactive map
        st.markdown("### Site Map")
        render_map_with_layout(params, st.session_state.get('layout'))

    with col_side:
        # BoP components panel
        render_bop_panel()

        st.markdown("---")

        # Export options
        st.markdown("### Export")
        if st.session_state.get('layout'):
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                if st.button("Export CSV", use_container_width=True):
                    st.info("CSV export coming soon")
            with export_col2:
                if st.button("Export PDF", use_container_width=True):
                    st.info("PDF export coming soon")

        st.markdown("---")

        # Quick actions
        st.markdown("### Actions")
        if st.button("Clear Layout", use_container_width=True):
            st.session_state['layout'] = None
            st.session_state['drawn_boundary'] = None
            st.rerun()

        if st.button("Reset BoP", use_container_width=True):
            st.session_state['bop_components'] = []
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <small>PV Layout Designer | Interactive Solar PV Design Tool | Built with Streamlit & Folium</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
