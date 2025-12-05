"""
PV Layout Designer - Main Streamlit Application

Main application entry point with visualization integration.
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to Python path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from components.layout_engine import place_modules, optimize_layout
    LAYOUT_ENGINE_AVAILABLE = True
except ImportError:
    LAYOUT_ENGINE_AVAILABLE = False

try:
    from components.visualizer import render_all_views, display_in_streamlit, VisualizerConfig
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("☀️ PV Layout Designer")
    st.markdown("### Solar PV Layout Design and Visualization Tool")

    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # Site parameters
    st.sidebar.subheader("Site Parameters")
    site_length = st.sidebar.number_input("Site Length (m)", value=100.0, min_value=10.0, max_value=1000.0)
    site_width = st.sidebar.number_input("Site Width (m)", value=100.0, min_value=10.0, max_value=1000.0)
    margin = st.sidebar.number_input("Perimeter Margin (m)", value=5.0, min_value=0.0, max_value=20.0)
    latitude = st.sidebar.number_input("Latitude (deg)", value=23.0225, min_value=-90.0, max_value=90.0)

    # Module parameters
    st.sidebar.subheader("Module Specifications")
    module_length = st.sidebar.number_input("Module Length (m)", value=2.278, min_value=1.0, max_value=3.0, step=0.001)
    module_width = st.sidebar.number_input("Module Width (m)", value=1.134, min_value=0.5, max_value=2.0, step=0.001)
    module_power = st.sidebar.number_input("Module Power (W)", value=545, min_value=100, max_value=1000)
    tilt_angle = st.sidebar.number_input("Tilt Angle (deg)", value=15, min_value=0, max_value=45)

    # Layout parameters
    st.sidebar.subheader("Layout Parameters")
    walkway_width = st.sidebar.number_input("Walkway Width (m)", value=3.0, min_value=0.0, max_value=10.0)
    orientation = st.sidebar.selectbox("Orientation", ["portrait", "landscape"])

    # Create site coordinates (rectangular)
    site_coords = [
        (0, 0),
        (site_length, 0),
        (site_length, site_width),
        (0, site_width)
    ]

    # Display site info
    site_area = site_length * site_width
    col1, col2, col3 = st.columns(3)
    col1.metric("Site Area", f"{site_area:,.0f} m2")
    col2.metric("Module Area", f"{module_length * module_width:.2f} m2")
    col3.metric("Latitude", f"{latitude} deg")

    # Generate Layout button
    if st.button("Generate Layout", type="primary"):
        if not LAYOUT_ENGINE_AVAILABLE:
            st.error("Layout engine not available. Please check dependencies.")
            return

        with st.spinner("Calculating optimal layout..."):
            # Prepare configuration
            config = {
                'latitude': latitude,
                'module_length': module_length,
                'module_width': module_width,
                'module_power': module_power,
                'tilt_angle': tilt_angle,
                'orientation': orientation,
                'walkway_width': walkway_width,
                'margin': margin
            }

            # Generate layout
            layout_result = place_modules(site_coords, config)

            # Store in session state
            st.session_state['layout'] = layout_result

            # Display results
            st.success("Layout Generated Successfully!")

            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Modules", f"{layout_result['total_modules']:,}")
            col2.metric("System Capacity", f"{layout_result['capacity_kwp']:.1f} kWp")
            col3.metric("Number of Rows", layout_result['rows'])
            col4.metric("Actual GCR", f"{layout_result['actual_gcr']:.2%}")

            # Details in expandable section
            with st.expander("Detailed Layout Information"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Spacing & Coverage:**")
                    st.write(f"- Row Pitch: {layout_result['row_pitch']:.2f} m")
                    st.write(f"- Row Spacing (with walkway): {layout_result['row_spacing']:.2f} m")
                    st.write(f"- Usable Area: {layout_result['usable_area']:,.1f} m2")
                    st.write(f"- Avg Modules per Row: {layout_result['modules_per_row']:.1f}")

                with col2:
                    st.write("**Solar & Power:**")
                    st.write(f"- Solar Elevation: {layout_result['solar_elevation']:.2f} deg")
                    st.write(f"- Module Area: {layout_result['module_area']:.2f} m2")
                    st.write(f"- Total Module Area: {layout_result['total_modules'] * layout_result['module_area']:,.1f} m2")
                    st.write(f"- Land Utilization: {(layout_result['total_modules'] * layout_result['module_area'] / site_area):.2%}")

            # Display sample module positions
            with st.expander("Sample Module Positions (First 10)"):
                if layout_result['modules']:
                    st.write("First 10 modules:")
                    for i, module in enumerate(layout_result['modules'][:10]):
                        st.write(f"Module {i+1}: Position ({module['position'][0]:.2f}, {module['position'][1]:.2f}) m, Row {module['row']}")

    # Show stored layout if available
    if 'layout' in st.session_state:
        st.divider()
        st.subheader("Current Layout Summary")
        layout = st.session_state['layout']

        col1, col2, col3 = st.columns(3)
        col1.metric("Modules", f"{layout['total_modules']:,}")
        col2.metric("Capacity", f"{layout['capacity_kwp']:.1f} kWp")
        col3.metric("GCR", f"{layout['actual_gcr']:.2%}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <small>PV Layout Designer | Built with Streamlit</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
