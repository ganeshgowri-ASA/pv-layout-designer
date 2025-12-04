"""
SESSION-08: 2D/3D Visualization Component
Multi-view visualization: 2D top, side profile, 3D isometric

Author: PV Layout Designer Team
"""

import folium
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pydeck as pdk
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any


# Color Coding Constants
COLORS = {
    'modules': '#4A90E2',        # Blue
    'walkways': '#9E9E9E',       # Grey
    'equipment_inverter': '#FF5252',  # Red
    'equipment_transformer': '#4CAF50',  # Green
    'margins': '#FFD600',        # Yellow
    'shading': '#424242',        # Dark grey for shaded areas
}


class VisualizerConfig:
    """Configuration for visualization rendering"""
    def __init__(
        self,
        map_center: Tuple[float, float] = (23.0225, 72.5714),  # Default: Gujarat, India
        zoom_start: int = 15,
        map_style: str = 'OpenStreetMap',
        figure_size: Tuple[int, int] = (12, 6),
        dpi: int = 100,
        initial_view_state: Optional[Dict] = None
    ):
        self.map_center = map_center
        self.zoom_start = zoom_start
        self.map_style = map_style
        self.figure_size = figure_size
        self.dpi = dpi
        self.initial_view_state = initial_view_state or {
            'latitude': map_center[0],
            'longitude': map_center[1],
            'zoom': 15,
            'pitch': 45,
            'bearing': 0
        }


def render_top_view(layout: Dict[str, Any], folium_map: Optional[folium.Map] = None, 
                    config: Optional[VisualizerConfig] = None) -> folium.Map:
    """
    Render 2D top view of the PV layout using Folium
    
    Args:
        layout: Dictionary containing layout data with keys:
            - 'modules': List of module positions with [lat, lon, width, height]
            - 'walkways': List of walkway positions
            - 'equipment': List of equipment positions
            - 'boundaries': Site boundary coordinates
            - 'center': [lat, lon] site center
        folium_map: Optional existing Folium map object
        config: Optional VisualizerConfig object
        
    Returns:
        folium.Map: Interactive Folium map with overlay
    """
    if config is None:
        config = VisualizerConfig()
    
    # Create or use existing map
    if folium_map is None:
        map_center = layout.get('center', config.map_center)
        folium_map = folium.Map(
            location=map_center,
            zoom_start=config.zoom_start,
            tiles=config.map_style
        )
    
    # Render site boundaries if available
    if 'boundaries' in layout and layout['boundaries']:
        folium.Polygon(
            locations=layout['boundaries'],
            color=COLORS['margins'],
            weight=3,
            fill=False,
            popup='Site Boundary'
        ).add_to(folium_map)
    
    # Render margins
    if 'margins' in layout:
        for margin in layout['margins']:
            folium.Polygon(
                locations=margin.get('coords', []),
                color=COLORS['margins'],
                weight=2,
                fill=True,
                fillOpacity=0.1,
                popup='Safety Margin'
            ).add_to(folium_map)
    
    # Render walkways
    if 'walkways' in layout:
        for idx, walkway in enumerate(layout['walkways']):
            folium.Polygon(
                locations=walkway.get('coords', []),
                color=COLORS['walkways'],
                weight=1,
                fill=True,
                fillColor=COLORS['walkways'],
                fillOpacity=0.3,
                popup=f'Walkway {idx + 1}'
            ).add_to(folium_map)
    
    # Render modules
    if 'modules' in layout:
        for idx, module in enumerate(layout['modules']):
            coords = module.get('coords', [])
            if coords:
                folium.Polygon(
                    locations=coords,
                    color=COLORS['modules'],
                    weight=1,
                    fill=True,
                    fillColor=COLORS['modules'],
                    fillOpacity=0.6,
                    popup=f"Module {idx + 1}<br>Tilt: {module.get('tilt', 'N/A')}°<br>Azimuth: {module.get('azimuth', 'N/A')}°"
                ).add_to(folium_map)
    
    # Render equipment (inverters, transformers)
    if 'equipment' in layout:
        for equipment in layout['equipment']:
            eq_type = equipment.get('type', 'inverter')
            color = COLORS['equipment_inverter'] if eq_type == 'inverter' else COLORS['equipment_transformer']
            
            folium.CircleMarker(
                location=equipment.get('position', [0, 0]),
                radius=8,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                popup=f"{equipment.get('name', eq_type.capitalize())}<br>Type: {eq_type}"
            ).add_to(folium_map)
    
    # Add layer control
    folium.LayerControl().add_to(folium_map)
    
    return folium_map


def render_side_view(layout: Dict[str, Any], config: Optional[VisualizerConfig] = None) -> plt.Figure:
    """
    Render side profile view showing tilt angle using Matplotlib
    
    Args:
        layout: Dictionary containing layout data with keys:
            - 'rows': List of module rows with tilt information
            - 'spacing': Inter-row spacing
            - 'module_height': Module height
            - 'tilt_angle': Tilt angle in degrees
            
    Returns:
        matplotlib.figure.Figure: Side profile figure
    """
    if config is None:
        config = VisualizerConfig()
    
    fig, ax = plt.subplots(figsize=config.figure_size, dpi=config.dpi)
    
    # Extract layout parameters
    tilt_angle = layout.get('tilt_angle', 20)  # degrees
    module_length = layout.get('module_length', 2.0)  # meters
    module_height = layout.get('module_height', 0.04)  # meters (thickness)
    ground_clearance = layout.get('ground_clearance', 0.5)  # meters
    num_rows = layout.get('num_rows', 3)
    row_spacing = layout.get('row_spacing', 5.0)  # meters
    
    # Convert tilt angle to radians
    tilt_rad = np.radians(tilt_angle)
    
    # Calculate module dimensions in side view
    module_width_projected = module_length * np.cos(tilt_rad)
    module_height_projected = module_length * np.sin(tilt_rad)
    
    # Draw ground line
    total_width = num_rows * row_spacing + module_width_projected
    ax.plot([0, total_width], [0, 0], 'k-', linewidth=2, label='Ground Level')
    
    # Draw each row of modules
    for i in range(num_rows):
        x_offset = i * row_spacing
        
        # Module corners (from ground clearance)
        x1 = x_offset
        y1 = ground_clearance
        x2 = x_offset + module_width_projected
        y2 = ground_clearance
        x3 = x_offset + module_width_projected
        y3 = ground_clearance + module_height_projected
        x4 = x_offset
        y4 = ground_clearance + module_height_projected
        
        # Draw module as filled polygon
        module_polygon = patches.Polygon(
            [(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
            closed=True,
            facecolor=COLORS['modules'],
            edgecolor='black',
            linewidth=1.5,
            alpha=0.7,
            label='PV Module' if i == 0 else ''
        )
        ax.add_patch(module_polygon)
        
        # Draw support structure (simple line)
        ax.plot([x1, x1], [0, y1], 'k-', linewidth=2, alpha=0.5)
        ax.plot([x2, x2], [0, y2], 'k-', linewidth=2, alpha=0.5)
        
        # Add angle annotation on first module
        if i == 0:
            # Draw angle arc
            arc_radius = 0.5
            angle_arc = patches.Arc(
                (x1, y1), 2 * arc_radius, 2 * arc_radius,
                angle=0, theta1=0, theta2=tilt_angle,
                color='red', linewidth=2
            )
            ax.add_patch(angle_arc)
            ax.text(
                x1 + arc_radius * 1.5, y1 + 0.2,
                f'{tilt_angle}°',
                fontsize=10, color='red', weight='bold'
            )
    
    # Annotate row spacing
    if num_rows > 1:
        y_annotation = -0.3
        ax.annotate(
            '',
            xy=(row_spacing, y_annotation),
            xytext=(0, y_annotation),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.5)
        )
        ax.text(
            row_spacing / 2, y_annotation - 0.2,
            f'Row Spacing: {row_spacing:.2f}m',
            ha='center', fontsize=9
        )
    
    # Configure axes
    ax.set_xlabel('Distance (meters)', fontsize=12)
    ax.set_ylabel('Height (meters)', fontsize=12)
    ax.set_title(f'Side Profile View - Tilt Angle: {tilt_angle}°', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_aspect('equal', adjustable='box')
    ax.legend(loc='upper right')
    
    # Set limits with some padding
    ax.set_xlim(-1, total_width + 1)
    ax.set_ylim(-1, ground_clearance + module_height_projected + 1)
    
    plt.tight_layout()
    
    return fig


def render_3d_isometric(layout: Dict[str, Any], config: Optional[VisualizerConfig] = None) -> pdk.Deck:
    """
    Render interactive 3D isometric view using PyDeck
    
    Args:
        layout: Dictionary containing layout data with keys:
            - 'modules': List of modules with [lat, lon, width, height, elevation]
            - 'center': [lat, lon] site center
            - 'tilt_angle': Tilt angle for 3D extrusion
            
    Returns:
        pydeck.Deck: Interactive 3D visualization
    """
    if config is None:
        config = VisualizerConfig()
    
    # Prepare data for 3D visualization
    modules_data = []
    
    if 'modules' in layout:
        for idx, module in enumerate(layout['modules']):
            # Get module coordinates (should be polygon coords)
            coords = module.get('coords', [])
            if coords:
                # Calculate centroid
                lats = [c[0] for c in coords]
                lons = [c[1] for c in coords]
                centroid = [np.mean(lats), np.mean(lons)]
                
                # Module elevation based on tilt
                tilt = module.get('tilt', layout.get('tilt_angle', 20))
                base_elevation = module.get('ground_clearance', 0.5)
                module_length = module.get('length', 2.0)
                
                # Calculate height for 3D extrusion (visual scaling factor)
                # Note: Scaled by 1000x for better visibility in 3D view
                height = base_elevation + module_length * np.sin(np.radians(tilt))
                
                modules_data.append({
                    'position': [lons[0], lats[0]],
                    'coordinates': [[lon, lat] for lat, lon in coords],  # PyDeck uses [lon, lat] order
                    'elevation': base_elevation * 1000,  # Scaled 1000x for visibility
                    'height': height * 1000,  # Scaled 1000x for visibility
                    'color': [74, 144, 226, 200],  # RGBA for blue modules
                    'name': f'Module {idx + 1}'
                })
    
    # Create PolygonLayer for modules
    polygon_layer = pdk.Layer(
        'PolygonLayer',
        data=modules_data,
        get_polygon='coordinates',
        get_elevation='elevation',
        get_fill_color='color',
        get_line_color=[0, 0, 0, 100],
        extruded=True,
        wireframe=True,
        elevation_scale=1,
        pickable=True,
        auto_highlight=True
    )
    
    # Create equipment markers if available
    equipment_data = []
    if 'equipment' in layout:
        for equipment in layout['equipment']:
            position = equipment.get('position', [0, 0])
            eq_type = equipment.get('type', 'inverter')
            color = [255, 82, 82, 200] if eq_type == 'inverter' else [76, 175, 80, 200]
            
            equipment_data.append({
                'position': [position[1], position[0]],  # [lon, lat]
                'elevation': 50,
                'radius': 5,
                'color': color,
                'name': equipment.get('name', eq_type.capitalize())
            })
    
    equipment_layer = pdk.Layer(
        'ScatterplotLayer',
        data=equipment_data,
        get_position='position',
        get_color='color',
        get_radius='radius',
        elevation_scale=1,
        pickable=True
    ) if equipment_data else None
    
    # Set view state
    view_state = pdk.ViewState(
        latitude=layout.get('center', config.map_center)[0],
        longitude=layout.get('center', config.map_center)[1],
        zoom=config.initial_view_state['zoom'],
        pitch=config.initial_view_state['pitch'],
        bearing=config.initial_view_state['bearing']
    )
    
    # Create deck
    layers = [polygon_layer]
    if equipment_layer:
        layers.append(equipment_layer)
    
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/satellite-v9',
        tooltip={
            'text': '{name}\nHeight: {height}mm'
        }
    )
    
    return deck


def add_shading_overlay(folium_map: folium.Map, shading_analysis: Dict[str, Any]) -> folium.Map:
    """
    Add shading analysis overlay to the map view
    
    Args:
        folium_map: Existing Folium map
        shading_analysis: Dictionary containing shading data:
            - 'shaded_areas': List of polygon coordinates representing shaded regions
            - 'shade_percentage': Percentage of shading per area
            - 'time': Time of day for shading calculation
            
    Returns:
        folium.Map: Map with shading overlay
    """
    if 'shaded_areas' in shading_analysis:
        for idx, shaded_area in enumerate(shading_analysis['shaded_areas']):
            coords = shaded_area.get('coords', [])
            shade_percent = shaded_area.get('shade_percentage', 0)
            time = shaded_area.get('time', 'N/A')
            
            # Opacity based on shade percentage
            opacity = min(0.7, shade_percent / 100 * 0.7)
            
            if coords:
                folium.Polygon(
                    locations=coords,
                    color=COLORS['shading'],
                    weight=1,
                    fill=True,
                    fillColor=COLORS['shading'],
                    fillOpacity=opacity,
                    popup=f"Shaded Area {idx + 1}<br>Shade: {shade_percent:.1f}%<br>Time: {time}"
                ).add_to(folium_map)
    
    return folium_map


def render_all_views(layout: Dict[str, Any], 
                     shading_analysis: Optional[Dict[str, Any]] = None,
                     config: Optional[VisualizerConfig] = None) -> Dict[str, Any]:
    """
    Render all visualization views (2D top, side profile, 3D isometric)
    
    Args:
        layout: Layout data dictionary
        shading_analysis: Optional shading analysis data
        config: Optional visualization configuration
        
    Returns:
        Dictionary containing all rendered views:
            - 'top_view': Folium map
            - 'side_view': Matplotlib figure
            - '3d_view': PyDeck deck
    """
    if config is None:
        config = VisualizerConfig()
    
    # Render top view
    top_view_map = render_top_view(layout, config=config)
    
    # Add shading overlay if available
    if shading_analysis:
        top_view_map = add_shading_overlay(top_view_map, shading_analysis)
    
    # Render side view
    side_view_fig = render_side_view(layout, config=config)
    
    # Render 3D isometric view
    isometric_3d = render_3d_isometric(layout, config=config)
    
    return {
        'top_view': top_view_map,
        'side_view': side_view_fig,
        '3d_view': isometric_3d
    }


def display_in_streamlit(views: Dict[str, Any], tab_names: List[str] = None):
    """
    Display all views in Streamlit tabs
    
    Args:
        views: Dictionary with 'top_view', 'side_view', '3d_view'
        tab_names: Optional custom tab names
    """
    # Import streamlit only when needed for UI integration
    try:
        import streamlit as st
    except ImportError:
        raise ImportError(
            "Streamlit is required for display_in_streamlit(). "
            "Install it with: pip install streamlit"
        )
    
    if tab_names is None:
        tab_names = ["2D Top View", "Side Profile", "3D Isometric"]
    
    tab1, tab2, tab3 = st.tabs(tab_names)
    
    with tab1:
        st.subheader("2D Top View - Interactive Map")
        if 'top_view' in views:
            st.components.v1.html(views['top_view']._repr_html_(), height=600)
    
    with tab2:
        st.subheader("Side Profile - Tilt Angle View")
        if 'side_view' in views:
            st.pyplot(views['side_view'])
    
    with tab3:
        st.subheader("3D Isometric View - Interactive")
        if '3d_view' in views:
            st.pydeck_chart(views['3d_view'])
