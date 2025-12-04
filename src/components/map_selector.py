"""Interactive map selector component for site boundary definition.

This module provides an interactive Folium map with drawing tools
for selecting and defining PV plant site boundaries.

Example:
    from components.map_selector import render_map_selector

    result = render_map_selector()
    if result:
        print(f"Site area: {result['area_sqm']:.2f} sq meters")
        print(f"Center: {result['center']}")
"""

import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
from shapely.geometry import Polygon, shape
from shapely.ops import transform
import pyproj
from functools import partial
from typing import Dict, List, Tuple, Optional, Any

# Default map settings (Gujarat, India)
DEFAULT_LATITUDE = 23.0225
DEFAULT_LONGITUDE = 72.5714
DEFAULT_ZOOM = 13


def _extract_coordinates_from_geojson(geojson_data: Dict) -> List[Tuple[float, float]]:
    """Extract coordinates from GeoJSON geometry.

    Args:
        geojson_data: GeoJSON geometry dict.

    Returns:
        List of (lat, lon) tuples.
    """
    geometry_type = geojson_data.get('type', '')
    coordinates = geojson_data.get('coordinates', [])

    if geometry_type == 'Polygon':
        # Polygon coordinates are [[[lon, lat], ...]]
        if coordinates and len(coordinates) > 0:
            return [(coord[1], coord[0]) for coord in coordinates[0]]

    elif geometry_type == 'Rectangle' or geometry_type == 'Polygon':
        # Rectangle is stored as Polygon in GeoJSON
        if coordinates and len(coordinates) > 0:
            return [(coord[1], coord[0]) for coord in coordinates[0]]

    elif geometry_type == 'Point':
        # Circle center point - we'll handle this separately
        return [(coordinates[1], coordinates[0])]

    return []


def _calculate_area_sqm(coordinates: List[Tuple[float, float]]) -> float:
    """Calculate area of a polygon in square meters using Shapely.

    Uses a local UTM projection for accurate area calculation.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        Area in square meters.
    """
    if len(coordinates) < 3:
        return 0.0

    # Convert to (lon, lat) for Shapely
    coords_lonlat = [(lon, lat) for lat, lon in coordinates]

    try:
        polygon = Polygon(coords_lonlat)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # Fix invalid polygons

        # Get centroid for UTM zone calculation
        centroid = polygon.centroid

        # Determine UTM zone from longitude
        utm_zone = int((centroid.x + 180) / 6) + 1
        hemisphere = 'north' if centroid.y >= 0 else 'south'

        # Create projection transformer (WGS84 to UTM)
        wgs84 = pyproj.CRS('EPSG:4326')
        utm = pyproj.CRS(f'+proj=utm +zone={utm_zone} +{hemisphere} +ellps=WGS84')

        project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform

        # Transform and calculate area
        polygon_utm = transform(project, polygon)

        return polygon_utm.area

    except Exception as e:
        st.warning(f"Area calculation error: {e}")
        return 0.0


def _calculate_circle_area(radius_m: float) -> float:
    """Calculate area of a circle in square meters.

    Args:
        radius_m: Radius in meters.

    Returns:
        Area in square meters.
    """
    import math
    return math.pi * radius_m ** 2


def _get_centroid(coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculate the centroid of coordinates.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        (lat, lon) tuple of centroid.
    """
    if not coordinates:
        return (DEFAULT_LATITUDE, DEFAULT_LONGITUDE)

    lat_sum = sum(c[0] for c in coordinates)
    lon_sum = sum(c[1] for c in coordinates)
    n = len(coordinates)

    return (lat_sum / n, lon_sum / n)


def _get_bounds(coordinates: List[Tuple[float, float]]) -> List[List[float]]:
    """Get bounding box of coordinates.

    Args:
        coordinates: List of (lat, lon) tuples.

    Returns:
        [[south, west], [north, east]]
    """
    if not coordinates:
        return [[DEFAULT_LATITUDE, DEFAULT_LONGITUDE],
                [DEFAULT_LATITUDE, DEFAULT_LONGITUDE]]

    lats = [c[0] for c in coordinates]
    lons = [c[1] for c in coordinates]

    return [[min(lats), min(lons)], [max(lats), max(lons)]]


def render_map_selector(
    center: Tuple[float, float] = (DEFAULT_LATITUDE, DEFAULT_LONGITUDE),
    zoom: int = DEFAULT_ZOOM,
    height: int = 500
) -> Optional[Dict[str, Any]]:
    """Render an interactive map with drawing tools for site selection.

    Provides drawing tools for rectangle, polygon, circle, and polyline.
    Calculates area automatically when a shape is drawn.

    Args:
        center: Initial map center as (lat, lon) tuple.
        zoom: Initial zoom level (1-18).
        height: Map height in pixels.

    Returns:
        Dictionary containing:
            - coordinates: List of (lat, lon) tuples for the polygon vertices
            - area_sqm: Area in square meters
            - center: (lat, lon) tuple of the centroid
            - bounds: [[south, west], [north, east]] bounding box

        Returns None if no drawing has been made.

    Example:
        result = render_map_selector()
        if result:
            st.write(f"Area: {result['area_sqm']:.2f} m²")
            st.write(f"Vertices: {len(result['coordinates'])}")
    """

    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )

    # Add drawing controls
    draw = Draw(
        draw_options={
            'polyline': True,
            'polygon': True,
            'rectangle': True,
            'circle': True,
            'marker': False,
            'circlemarker': False,
        },
        edit_options={
            'edit': True,
            'remove': True,
        }
    )
    draw.add_to(m)

    # Add layer control for different base maps
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)
    folium.LayerControl().add_to(m)

    # Render map and capture output
    output = st_folium(
        m,
        width='100%',
        height=height,
        returned_objects=['all_drawings'],
        key='map_selector'
    )

    # Process drawings
    if output and output.get('all_drawings'):
        drawings = output['all_drawings']

        # Get the last drawing (most recent)
        if drawings and len(drawings) > 0:
            last_drawing = drawings[-1]
            geometry = last_drawing.get('geometry', {})
            properties = last_drawing.get('properties', {})

            geometry_type = geometry.get('type', '')

            # Handle Circle separately (stored differently in Folium)
            if geometry_type == 'Point' and 'radius' in properties:
                # It's a circle
                center_coords = geometry.get('coordinates', [])
                radius = properties.get('radius', 0)  # radius in meters

                if center_coords and radius > 0:
                    center_lat, center_lon = center_coords[1], center_coords[0]
                    area = _calculate_circle_area(radius)

                    # Generate approximate polygon coordinates for circle
                    import math
                    num_points = 36
                    circle_coords = []
                    for i in range(num_points):
                        angle = 2 * math.pi * i / num_points
                        # Approximate lat/lon offset from meters
                        dlat = (radius * math.cos(angle)) / 111320
                        dlon = (radius * math.sin(angle)) / (111320 * math.cos(math.radians(center_lat)))
                        circle_coords.append((center_lat + dlat, center_lon + dlon))

                    return {
                        'coordinates': circle_coords,
                        'area_sqm': area,
                        'center': (center_lat, center_lon),
                        'bounds': _get_bounds(circle_coords),
                        'type': 'circle',
                        'radius_m': radius
                    }

            else:
                # Polygon or Rectangle
                coordinates = _extract_coordinates_from_geojson(geometry)

                if coordinates and len(coordinates) >= 3:
                    area = _calculate_area_sqm(coordinates)
                    centroid = _get_centroid(coordinates)
                    bounds = _get_bounds(coordinates)

                    return {
                        'coordinates': coordinates,
                        'area_sqm': area,
                        'center': centroid,
                        'bounds': bounds,
                        'type': geometry_type.lower()
                    }

    return None


def format_area(area_sqm: float) -> str:
    """Format area with appropriate units.

    Args:
        area_sqm: Area in square meters.

    Returns:
        Formatted string with appropriate units.
    """
    if area_sqm >= 10000:
        # Use hectares for large areas
        hectares = area_sqm / 10000
        return f"{hectares:,.2f} hectares ({area_sqm:,.0f} m²)"
    elif area_sqm >= 1000:
        return f"{area_sqm:,.0f} m²"
    else:
        return f"{area_sqm:.2f} m²"
