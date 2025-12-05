"""
PV Layout Designer - Main Application
Streamlit app demonstrating the layout engine integration.
"""
import streamlit as st
from src.components.layout_engine import place_modules, optimize_layout


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="🌞",
        layout="wide"
    )
    
    st.title("🌞 PV Layout Designer")
    st.markdown("### SESSION-05: Core Layout Engine Demo")
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Site parameters
    st.sidebar.subheader("Site Parameters")
    site_length = st.sidebar.number_input("Site Length (m)", value=100.0, min_value=10.0, max_value=1000.0)
    site_width = st.sidebar.number_input("Site Width (m)", value=100.0, min_value=10.0, max_value=1000.0)
    margin = st.sidebar.number_input("Perimeter Margin (m)", value=5.0, min_value=0.0, max_value=20.0)
    latitude = st.sidebar.number_input("Latitude (°)", value=23.0225, min_value=-90.0, max_value=90.0)
    
    # Module parameters
    st.sidebar.subheader("Module Specifications")
    module_length = st.sidebar.number_input("Module Length (m)", value=2.278, min_value=1.0, max_value=3.0, step=0.001)
    module_width = st.sidebar.number_input("Module Width (m)", value=1.134, min_value=0.5, max_value=2.0, step=0.001)
    module_power = st.sidebar.number_input("Module Power (W)", value=545, min_value=100, max_value=1000)
    tilt_angle = st.sidebar.number_input("Tilt Angle (°)", value=15, min_value=0, max_value=45)
    
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
    col1.metric("Site Area", f"{site_area:,.0f} m²")
    col2.metric("Module Area", f"{module_length * module_width:.2f} m²")
    col3.metric("Latitude", f"{latitude}°")
    
    # Generate Layout button
    if st.button("🚀 Generate Layout", type="primary"):
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
            st.success("✅ Layout Generated Successfully!")
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Modules", f"{layout_result['total_modules']:,}")
            col2.metric("System Capacity", f"{layout_result['capacity_kwp']:.1f} kWp")
            col3.metric("Number of Rows", layout_result['rows'])
            col4.metric("Actual GCR", f"{layout_result['actual_gcr']:.2%}")
            
            # Details in expandable section
            with st.expander("📊 Detailed Layout Information"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Spacing & Coverage:**")
                    st.write(f"- Row Pitch: {layout_result['row_pitch']:.2f} m")
                    st.write(f"- Row Spacing (with walkway): {layout_result['row_spacing']:.2f} m")
                    st.write(f"- Usable Area: {layout_result['usable_area']:,.1f} m²")
                    st.write(f"- Avg Modules per Row: {layout_result['modules_per_row']:.1f}")
                
                with col2:
                    st.write("**Solar & Power:**")
                    st.write(f"- Solar Elevation: {layout_result['solar_elevation']:.2f}°")
                    st.write(f"- Module Area: {layout_result['module_area']:.2f} m²")
                    st.write(f"- Total Module Area: {layout_result['total_modules'] * layout_result['module_area']:,.1f} m²")
                    st.write(f"- Land Utilization: {(layout_result['total_modules'] * layout_result['module_area'] / site_area):.2%}")
            
            # Display sample module positions
            with st.expander("📍 Sample Module Positions (First 10)"):
                if layout_result['modules']:
                    st.write("First 10 modules:")
                    for i, module in enumerate(layout_result['modules'][:10]):
                        st.write(f"Module {i+1}: Position ({module['position'][0]:.2f}, {module['position'][1]:.2f}) m, Row {module['row']}")
    
    # Show stored layout if available
    if 'layout' in st.session_state:
        st.divider()
        st.subheader("💾 Current Layout Summary")
        layout = st.session_state['layout']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Modules", f"{layout['total_modules']:,}")
        col2.metric("Capacity", f"{layout['capacity_kwp']:.1f} kWp")
        col3.metric("GCR", f"{layout['actual_gcr']:.2%}")


if __name__ == "__main__":
    main()
PV Layout Designer - Main Streamlit Application
SESSION-08: Visualization Integration Example
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to Python path for imports
src_path = Path(__file__).parent.parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from components.visualizer import render_all_views, display_in_streamlit, VisualizerConfig

# Page configuration
st.set_page_config(
    page_title="PV Layout Designer",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🌞 PV Layout Designer - Visualization Demo")
st.markdown("**SESSION-08: 2D/3D Multi-View Visualization**")

# Sidebar for configuration
with st.sidebar:
    st.header("Layout Configuration")
    
    tilt_angle = st.slider("Tilt Angle (degrees)", 0, 90, 20)
    num_rows = st.slider("Number of Rows", 1, 10, 3)
    row_spacing = st.slider("Row Spacing (meters)", 3.0, 10.0, 5.0, 0.5)
    module_length = st.slider("Module Length (meters)", 1.0, 3.0, 2.0, 0.1)
    ground_clearance = st.slider("Ground Clearance (meters)", 0.2, 2.0, 0.5, 0.1)
    
    st.markdown("---")
    st.header("Visualization Settings")
    
    map_zoom = st.slider("Map Zoom Level", 10, 20, 15)
    pitch_3d = st.slider("3D View Pitch", 0, 90, 45)
    
    generate_btn = st.button("🔄 Generate Visualization", type="primary", use_container_width=True)

# Main content area
st.markdown("---")

# Sample layout data (would come from SESSION-05 in production)
if generate_btn or 'layout' not in st.session_state:
    # Generate sample layout
    layout = {
        'center': [23.0225, 72.5714],  # Gujarat, India
        'boundaries': [
            [23.0220, 72.5710],
            [23.0230, 72.5710],
            [23.0230, 72.5720],
            [23.0220, 72.5720]
        ],
        'modules': [],
        'walkways': [],
        'equipment': [
            {
                'type': 'inverter',
                'position': [23.0225, 72.5712],
                'name': 'Central Inverter'
            },
            {
                'type': 'transformer',
                'position': [23.0226, 72.5718],
                'name': 'Main Transformer'
            }
        ],
        'margins': [
            {
                'coords': [
                    [23.0219, 72.5709],
                    [23.0231, 72.5709],
                    [23.0231, 72.5721],
                    [23.0219, 72.5721]
                ]
            }
        ],
        'tilt_angle': tilt_angle,
        'module_length': module_length,
        'module_height': 0.04,
        'ground_clearance': ground_clearance,
        'num_rows': num_rows,
        'row_spacing': row_spacing
    }
    
    # Generate module positions (simplified)
    lat_start = 23.0222
    lon_start = 72.5713
    module_width_deg = 0.00001
    module_length_deg = 0.00002
    
    for row in range(num_rows):
        for col in range(5):  # 5 modules per row
            lat_offset = row * 0.00003
            lon_offset = col * 0.00003
            
            module_coords = [
                [lat_start + lat_offset, lon_start + lon_offset],
                [lat_start + lat_offset + module_length_deg, lon_start + lon_offset],
                [lat_start + lat_offset + module_length_deg, lon_start + lon_offset + module_width_deg],
                [lat_start + lat_offset, lon_start + lon_offset + module_width_deg]
            ]
            
            layout['modules'].append({
                'coords': module_coords,
                'tilt': tilt_angle,
                'azimuth': 180,
                'length': module_length,
                'ground_clearance': ground_clearance
            })
    
    # Add walkways between rows
    for row in range(num_rows - 1):
        lat_offset = row * 0.00003 + module_length_deg
        walkway_coords = [
            [lat_start + lat_offset, lon_start - 0.00001],
            [lat_start + lat_offset + 0.00001, lon_start - 0.00001],
            [lat_start + lat_offset + 0.00001, lon_start + 0.00015],
            [lat_start + lat_offset, lon_start + 0.00015]
        ]
        layout['walkways'].append({'coords': walkway_coords})
    
    st.session_state['layout'] = layout
    
    # Sample shading analysis (would come from SESSION-06 in production)
    st.session_state['shading_analysis'] = {
        'shaded_areas': [
            {
                'coords': layout['modules'][0]['coords'],
                'shade_percentage': 25.0,
                'time': '09:00'
            }
        ]
    }

# Display status
if 'layout' in st.session_state:
    layout = st.session_state['layout']
    shading = st.session_state.get('shading_analysis', None)
    
    # Show summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Modules", len(layout.get('modules', [])))
    with col2:
        st.metric("Tilt Angle", f"{layout.get('tilt_angle', 0)}°")
    with col3:
        st.metric("Row Spacing", f"{layout.get('row_spacing', 0):.1f}m")
    with col4:
        st.metric("Equipment", len(layout.get('equipment', [])))
    
    st.markdown("---")
    
    # Create visualization config
    config = VisualizerConfig(
        map_center=layout['center'],
        zoom_start=map_zoom,
        initial_view_state={
            'latitude': layout['center'][0],
            'longitude': layout['center'][1],
            'zoom': map_zoom,
            'pitch': pitch_3d,
            'bearing': 0
        }
    )
    
    # Render all views
    with st.spinner('Generating visualizations...'):
        views = render_all_views(layout, shading_analysis=shading, config=config)
    
    # Display in tabs
    display_in_streamlit(views)
    
    st.markdown("---")
    st.success("✅ Visualization complete! Use tabs above to explore different views.")
    
    # Additional information
    with st.expander("ℹ️ About This Visualization"):
        st.markdown("""
        ### Features:
        - **2D Top View**: Interactive Folium map with module overlay
        - **Side Profile**: Matplotlib view showing tilt angle and row spacing
        - **3D Isometric**: PyDeck interactive 3D visualization
        
        ### Color Coding:
        - 🔵 **Blue**: Solar modules (#4A90E2)
        - ⚪ **Grey**: Walkways (#9E9E9E)
        - 🔴 **Red**: Inverters (#FF5252)
        - 🟢 **Green**: Transformers (#4CAF50)
        - 🟡 **Yellow**: Safety margins (#FFD600)
        - ⚫ **Dark Grey**: Shaded areas (#424242)
        
        ### Integration:
        - Requires: SESSION-05 (Layout Engine)
        - Optional: SESSION-06 (Shading Analysis), SESSION-07 (Soiling)
        - Supports: SESSION-10 (Export - PNG/SVG generation)
        """)

else:
    st.info("👈 Configure layout parameters in the sidebar and click 'Generate Visualization'")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>PV Layout Designer | SESSION-08: Visualization | Built with Streamlit, Folium, PyDeck & Matplotlib</small>
    </div>
    """,
    unsafe_allow_html=True
)
