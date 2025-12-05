"""
Interactive Map Viewer Component for PV Layout Designer.
Provides Folium map with drawing tools, satellite imagery, and module visualization.
"""

import folium
from folium import plugins
from folium.plugins import Draw, MousePosition, MeasureControl
import math
from typing import Dict, List, Tuple, Optional, Any


# Satellite tile layers
SATELLITE_TILES = {
    'Google Satellite': {
        'tiles': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'attr': 'Google',
        'name': 'Google Satellite'
    },
    'ESRI Satellite': {
        'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attr': 'Esri',
        'name': 'ESRI Satellite'
    },
    'Google Hybrid': {
        'tiles': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        'attr': 'Google',
        'name': 'Google Hybrid'
    }
}

# BoP component icons and colors
BOP_STYLES = {
    'walkway': {'color': '#9E9E9E', 'fillColor': '#BDBDBD', 'fillOpacity': 0.4, 'weight': 2},
    'porta_cabin': {'color': '#795548', 'fillColor': '#A1887F', 'fillOpacity': 0.7, 'weight': 2},
    'dcdb': {'color': '#FF9800', 'fillColor': '#FFB74D', 'fillOpacity': 0.8, 'weight': 2},
    'inverter': {'color': '#F44336', 'fillColor': '#EF5350', 'fillOpacity': 0.8, 'weight': 2},
    'transformer': {'color': '#4CAF50', 'fillColor': '#66BB6A', 'fillOpacity': 0.8, 'weight': 2},
    'cable_tray': {'color': '#607D8B', 'fillColor': '#90A4AE', 'fillOpacity': 0.5, 'weight': 2}
}

# Module visualization colors
MODULE_COLORS = {
    'default': {'color': '#2196F3', 'fillColor': '#42A5F5', 'fillOpacity': 0.6, 'weight': 1},
    'selected': {'color': '#FFC107', 'fillColor': '#FFD54F', 'fillOpacity': 0.8, 'weight': 2},
    'shaded': {'color': '#9E9E9E', 'fillColor': '#BDBDBD', 'fillOpacity': 0.5, 'weight': 1}
}


def create_map(
    center: Tuple[float, float] = (23.0225, 72.5714),
    zoom: int = 18,
    satellite: bool = True
) -> folium.Map:
    """
    Create a Folium map with satellite imagery and multiple tile layers.

    Args:
        center: (latitude, longitude) tuple for map center
        zoom: Initial zoom level (18 is good for site-level viewing)
        satellite: Whether to use satellite imagery as default layer

    Returns:
        folium.Map object with configured layers
    """
    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=None,  # Don't add default tiles
        control_scale=True,
        prefer_canvas=True
    )

    # Add OpenStreetMap as base layer
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        show=not satellite
    ).add_to(m)

    # Add satellite layers
    for name, config in SATELLITE_TILES.items():
        folium.TileLayer(
            tiles=config['tiles'],
            attr=config['attr'],
            name=name,
            show=(satellite and name == 'Google Satellite')
        ).add_to(m)

    return m


def add_drawing_tools(m: folium.Map) -> folium.Map:
    """
    Add Leaflet drawing tools for boundary selection.

    Enables drawing of:
    - Rectangles (for quick rectangular sites)
    - Polygons (for irregular site boundaries)

    Args:
        m: Folium map object

    Returns:
        Map with drawing controls added
    """
    draw = Draw(
        draw_options={
            'polyline': False,
            'polygon': {
                'allowIntersection': False,
                'showArea': True,
                'shapeOptions': {
                    'color': '#FFD700',
                    'fillColor': '#FFD700',
                    'fillOpacity': 0.2,
                    'weight': 3
                }
            },
            'rectangle': {
                'showArea': True,
                'shapeOptions': {
                    'color': '#FFD700',
                    'fillColor': '#FFD700',
                    'fillOpacity': 0.2,
                    'weight': 3
                }
            },
            'circle': False,
            'circlemarker': False,
            'marker': False
        },
        edit_options={
            'edit': True,
            'remove': True
        },
        position='topleft'
    )
    draw.add_to(m)

    return m


def add_mouse_position(m: folium.Map) -> folium.Map:
    """
    Add mouse position display showing coordinates on hover.

    Args:
        m: Folium map object

    Returns:
        Map with mouse position control
    """
    MousePosition(
        position='bottomleft',
        separator=' | ',
        prefix='Coordinates:',
        lat_first=True,
        num_digits=6
    ).add_to(m)

    return m


def add_measure_control(m: folium.Map) -> folium.Map:
    """
    Add measurement tools for distance and area calculation.

    Args:
        m: Folium map object

    Returns:
        Map with measure control
    """
    MeasureControl(
        position='bottomright',
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares'
    ).add_to(m)

    return m


def add_fullscreen(m: folium.Map) -> folium.Map:
    """
    Add fullscreen control to the map.

    Args:
        m: Folium map object

    Returns:
        Map with fullscreen control
    """
    plugins.Fullscreen(
        position='topright',
        title='Fullscreen',
        title_cancel='Exit Fullscreen',
        force_separate_button=True
    ).add_to(m)

    return m


def meters_to_degrees(meters: float, latitude: float) -> Tuple[float, float]:
    """
    Convert meters to degrees for lat/lon at given latitude.

    Args:
        meters: Distance in meters
        latitude: Reference latitude for conversion

    Returns:
        (lat_degrees, lon_degrees) tuple
    """
    # 1 degree of latitude is approximately 111,320 meters
    lat_degrees = meters / 111320.0

    # 1 degree of longitude varies with latitude
    lon_degrees = meters / (111320.0 * math.cos(math.radians(latitude)))

    return lat_degrees, lon_degrees


def create_module_polygon(
    center_lat: float,
    center_lon: float,
    width_m: float,
    length_m: float,
    rotation: float = 0
) -> List[Tuple[float, float]]:
    """
    Create polygon coordinates for a PV module at given center.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        width_m: Module width in meters
        length_m: Module length in meters
        rotation: Rotation angle in degrees (0 = north-south)

    Returns:
        List of (lat, lon) tuples for polygon corners
    """
    # Convert dimensions to degrees
    half_length_lat, _ = meters_to_degrees(length_m / 2, center_lat)
    _, half_width_lon = meters_to_degrees(width_m / 2, center_lat)

    # Create corners (unrotated)
    corners = [
        (center_lat - half_length_lat, center_lon - half_width_lon),  # SW
        (center_lat - half_length_lat, center_lon + half_width_lon),  # SE
        (center_lat + half_length_lat, center_lon + half_width_lon),  # NE
        (center_lat + half_length_lat, center_lon - half_width_lon),  # NW
    ]

    if rotation != 0:
        # Rotate corners around center
        rad = math.radians(rotation)
        rotated_corners = []
        for lat, lon in corners:
            # Translate to origin
            d_lat = lat - center_lat
            d_lon = lon - center_lon
            # Rotate
            new_lat = d_lat * math.cos(rad) - d_lon * math.sin(rad)
            new_lon = d_lat * math.sin(rad) + d_lon * math.cos(rad)
            # Translate back
            rotated_corners.append((center_lat + new_lat, center_lon + new_lon))
        corners = rotated_corners

    return corners


def add_site_boundary(
    m: folium.Map,
    boundary_coords: List[Tuple[float, float]],
    style: Optional[Dict] = None
) -> folium.Map:
    """
    Add site boundary polygon to map.

    Args:
        m: Folium map object
        boundary_coords: List of (lat, lon) tuples
        style: Optional style dictionary

    Returns:
        Map with boundary added
    """
    default_style = {
        'color': '#FFD700',
        'weight': 3,
        'fillColor': '#FFD700',
        'fillOpacity': 0.1
    }

    if style:
        default_style.update(style)

    folium.Polygon(
        locations=boundary_coords,
        popup='Site Boundary',
        tooltip='Site Boundary',
        **default_style
    ).add_to(m)

    return m


def add_modules_to_map(
    m: folium.Map,
    modules: List[Dict],
    module_length: float,
    module_width: float,
    center_lat: float,
    center_lon: float,
    site_origin: Tuple[float, float] = (0, 0)
) -> folium.Map:
    """
    Add module rectangles to map with tooltips.

    Args:
        m: Folium map object
        modules: List of module dictionaries with 'position', 'row' keys
        module_length: Module length in meters
        module_width: Module width in meters
        center_lat: Site center latitude
        center_lon: Site center longitude
        site_origin: (x, y) origin of site in meters

    Returns:
        Map with modules added
    """
    # Create feature group for modules
    module_group = folium.FeatureGroup(name='PV Modules', show=True)

    for idx, module in enumerate(modules):
        # Convert local position (meters) to lat/lon
        x_m, y_m = module['position']

        # Calculate offset from site center
        lat_offset, _ = meters_to_degrees(y_m - site_origin[1], center_lat)
        _, lon_offset = meters_to_degrees(x_m - site_origin[0], center_lat)

        module_lat = center_lat + lat_offset
        module_lon = center_lon + lon_offset

        # Create module polygon
        corners = create_module_polygon(
            module_lat + meters_to_degrees(module_length/2, center_lat)[0],
            module_lon + meters_to_degrees(module_width/2, center_lat)[1],
            module_width,
            module_length,
            rotation=module.get('rotation', 0)
        )

        # Add polygon to map
        row = module.get('row', 0)
        table_id = f"R{row+1}-M{(idx % 20) + 1}"

        folium.Polygon(
            locations=corners,
            popup=f"<b>Module {idx + 1}</b><br>Table: {table_id}<br>Row: {row + 1}",
            tooltip=f"Table {table_id}",
            color=MODULE_COLORS['default']['color'],
            weight=MODULE_COLORS['default']['weight'],
            fillColor=MODULE_COLORS['default']['fillColor'],
            fillOpacity=MODULE_COLORS['default']['fillOpacity']
        ).add_to(module_group)

    module_group.add_to(m)

    return m


def add_bop_component(
    m: folium.Map,
    component_type: str,
    position: Tuple[float, float],
    name: str = None,
    size: Tuple[float, float] = None
) -> folium.Map:
    """
    Add a Balance of Plant component to the map.

    Args:
        m: Folium map object
        component_type: One of 'walkway', 'porta_cabin', 'dcdb', 'inverter', 'transformer', 'cable_tray'
        position: (lat, lon) tuple
        name: Optional display name
        size: Optional (width, height) in meters for rectangular components

    Returns:
        Map with component added
    """
    style = BOP_STYLES.get(component_type, BOP_STYLES['inverter'])
    display_name = name or component_type.replace('_', ' ').title()

    if size and component_type in ['walkway', 'porta_cabin', 'cable_tray']:
        # Create rectangle for larger components
        lat, lon = position
        half_w_deg = size[0] / 111320.0 / 2 / math.cos(math.radians(lat))
        half_h_deg = size[1] / 111320.0 / 2

        corners = [
            (lat - half_h_deg, lon - half_w_deg),
            (lat - half_h_deg, lon + half_w_deg),
            (lat + half_h_deg, lon + half_w_deg),
            (lat + half_h_deg, lon - half_w_deg)
        ]

        folium.Polygon(
            locations=corners,
            popup=f"<b>{display_name}</b><br>Size: {size[0]}m x {size[1]}m",
            tooltip=display_name,
            **style
        ).add_to(m)
    else:
        # Use circle marker for point components
        icon_html = get_bop_icon_html(component_type)

        folium.CircleMarker(
            location=position,
            radius=8,
            popup=f"<b>{display_name}</b>",
            tooltip=display_name,
            color=style['color'],
            fillColor=style['fillColor'],
            fillOpacity=style['fillOpacity'],
            weight=style['weight']
        ).add_to(m)

    return m


def get_bop_icon_html(component_type: str) -> str:
    """
    Get HTML icon for BoP component type.

    Args:
        component_type: Component type string

    Returns:
        HTML string for icon
    """
    icons = {
        'inverter': '⚡',
        'transformer': '🔌',
        'dcdb': '📦',
        'porta_cabin': '🏠',
        'walkway': '🚶',
        'cable_tray': '➖'
    }
    return icons.get(component_type, '📍')


def create_interactive_map(
    center: Tuple[float, float],
    zoom: int = 18,
    enable_drawing: bool = True,
    enable_measure: bool = True,
    enable_fullscreen: bool = True
) -> folium.Map:
    """
    Create a fully interactive map with all tools enabled.

    Args:
        center: (latitude, longitude) tuple
        zoom: Initial zoom level
        enable_drawing: Enable drawing tools
        enable_measure: Enable measurement tools
        enable_fullscreen: Enable fullscreen button

    Returns:
        Fully configured folium.Map object
    """
    m = create_map(center=center, zoom=zoom, satellite=True)

    if enable_drawing:
        m = add_drawing_tools(m)

    m = add_mouse_position(m)

    if enable_measure:
        m = add_measure_control(m)

    if enable_fullscreen:
        m = add_fullscreen(m)

    # Add layer control
    folium.LayerControl(position='topright').add_to(m)

    return m


def calculate_boundary_from_params(
    center_lat: float,
    center_lon: float,
    length_m: float,
    width_m: float
) -> List[Tuple[float, float]]:
    """
    Calculate rectangular boundary coordinates from center and dimensions.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        length_m: Site length in meters (E-W direction)
        width_m: Site width in meters (N-S direction)

    Returns:
        List of (lat, lon) tuples for boundary corners
    """
    half_width_lat, _ = meters_to_degrees(width_m / 2, center_lat)
    _, half_length_lon = meters_to_degrees(length_m / 2, center_lat)

    # Create corners: SW, SE, NE, NW
    corners = [
        (center_lat - half_width_lat, center_lon - half_length_lon),  # SW
        (center_lat - half_width_lat, center_lon + half_length_lon),  # SE
        (center_lat + half_width_lat, center_lon + half_length_lon),  # NE
        (center_lat + half_width_lat, center_lon - half_length_lon),  # NW
    ]

    return corners


def convert_local_to_latlon(
    local_coords: List[Tuple[float, float]],
    center_lat: float,
    center_lon: float,
    origin: Tuple[float, float] = (0, 0)
) -> List[Tuple[float, float]]:
    """
    Convert local meter coordinates to lat/lon.

    Args:
        local_coords: List of (x, y) tuples in meters
        center_lat: Reference latitude
        center_lon: Reference longitude
        origin: Local coordinate origin offset

    Returns:
        List of (lat, lon) tuples
    """
    latlon_coords = []

    for x, y in local_coords:
        # Apply origin offset
        x_offset = x - origin[0]
        y_offset = y - origin[1]

        # Convert to degrees
        lat_offset, _ = meters_to_degrees(y_offset, center_lat)
        _, lon_offset = meters_to_degrees(x_offset, center_lat)

        latlon_coords.append((center_lat + lat_offset, center_lon + lon_offset))

    return latlon_coords


def get_map_html(m: folium.Map, height: int = 600) -> str:
    """
    Get the HTML representation of the map.

    Args:
        m: Folium map object
        height: Map height in pixels

    Returns:
        HTML string
    """
    return m._repr_html_()
