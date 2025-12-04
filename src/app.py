"""
PV Layout Designer - Main Streamlit Application
SESSION-08: Visualization Integration Example
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
