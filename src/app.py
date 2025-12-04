"""Solar PV Plant Layout Designer - Main Application.

A Streamlit-based web application for designing solar PV plant layouts.
This application allows users to:
1. Select a site location on an interactive map
2. Configure PV module parameters
3. Generate optimized panel layouts
4. Export designs in various formats

Usage:
    streamlit run src/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from components.map_selector import render_map_selector, format_area


def main():
    """Main application entry point."""

    # Page configuration
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="🌞",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF6B35;
            margin-bottom: 0.5rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .metric-box {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .stSuccess {
            background-color: #d4edda;
            border-color: #c3e6cb;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main title
    st.markdown('<p class="main-header">🌞 Solar PV Plant Layout Designer</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design optimized solar PV layouts with interactive tools</p>',
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("📍 Design Steps")
        st.markdown("---")

        # Step indicator
        st.markdown("### Step 1: Select Site Location")
        st.info("Draw your site boundary on the map using the drawing tools.")

        st.markdown("### Step 2: Configure Parameters")
        st.markdown("*Coming in next session...*")

        st.markdown("### Step 3: Generate Layout")
        st.markdown("*Coming soon...*")

        st.markdown("### Step 4: Export Design")
        st.markdown("*Coming soon...*")

        st.markdown("---")

        # Quick help
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. **Rectangle**: Click and drag to draw a rectangular site boundary
            2. **Polygon**: Click to add vertices, double-click to finish
            3. **Circle**: Click center, drag to set radius
            4. **Edit**: Click a shape to modify it
            5. **Delete**: Use the trash icon to remove shapes
            """)

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("🗺️ Site Selection Map")
        st.caption("Use the drawing tools on the left side of the map to define your site boundary")

        # Render the map selector
        result = render_map_selector(
            center=(23.0225, 72.5714),  # Gujarat, India
            zoom=13,
            height=550
        )

    with col2:
        st.subheader("📊 Site Info")

        if result:
            # Display success message with coordinates
            st.success("✅ Site boundary defined!")

            # Area metric
            st.metric(
                label="Site Area",
                value=format_area(result['area_sqm'])
            )

            # Shape type
            shape_type = result.get('type', 'polygon').capitalize()
            st.metric(
                label="Shape Type",
                value=shape_type
            )

            # Center coordinates
            center = result['center']
            st.metric(
                label="Center Latitude",
                value=f"{center[0]:.6f}°"
            )
            st.metric(
                label="Center Longitude",
                value=f"{center[1]:.6f}°"
            )

            # Bounding box
            with st.expander("📐 Bounding Box"):
                bounds = result['bounds']
                st.write(f"**South:** {bounds[0][0]:.6f}°")
                st.write(f"**West:** {bounds[0][1]:.6f}°")
                st.write(f"**North:** {bounds[1][0]:.6f}°")
                st.write(f"**East:** {bounds[1][1]:.6f}°")

            # Coordinates
            with st.expander("📍 Vertex Coordinates"):
                coords = result['coordinates']
                st.write(f"**Vertices:** {len(coords)}")
                for i, (lat, lon) in enumerate(coords[:10]):  # Show first 10
                    st.text(f"{i+1}. ({lat:.6f}, {lon:.6f})")
                if len(coords) > 10:
                    st.text(f"... and {len(coords) - 10} more")

            # Additional info for circles
            if result.get('type') == 'circle' and 'radius_m' in result:
                st.metric(
                    label="Radius",
                    value=f"{result['radius_m']:.1f} m"
                )

        else:
            st.info("👆 Draw a shape on the map to define your site boundary")

            st.markdown("---")
            st.markdown("**Quick Stats Preview:**")
            st.metric(label="Site Area", value="—")
            st.metric(label="Center", value="—")

    # Footer
    st.markdown("---")
    st.caption("PV Layout Designer v0.1.0 | Built with Streamlit & Folium")


if __name__ == "__main__":
    main()
