"""
PV Layout Designer - Main Streamlit Application

Advanced Solar PV Plant Layout Designer with Interactive Mapping,
Real-time Analysis & Automated Reporting
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import streamlit as st
from src.components.input_panel import render_input_panel


def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="🌞",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">🌞 PV Layout Designer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Advanced Solar PV Plant Layout Designer with Interactive Mapping & Real-time Analysis</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar Configuration Panel
    with st.sidebar:
        st.title("⚙️ Configuration")
        st.markdown("---")
        
        # Render input panel
        config = render_input_panel()
        
        # Store in session state
        if 'config' not in st.session_state or st.session_state.config != config:
            st.session_state.config = config
    
    # Main content area
    st.markdown("---")
    
    # Display current configuration summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📐 Module Specs")
        if 'config' in st.session_state:
            module_config = st.session_state.config.get('module', {})
            st.metric("Module Power", f"{module_config.get('power', 'N/A')} Wp")
            st.metric("Module Area", f"{module_config.get('area', 'N/A'):.2f} m²")
            st.metric("Efficiency", f"{module_config.get('efficiency', 'N/A')}%")
            st.info(f"**Orientation:** {module_config.get('orientation', 'N/A')}")
    
    with col2:
        st.subheader("🏗️ Layout Config")
        if 'config' in st.session_state:
            layout_config = st.session_state.config.get('layout', {})
            st.metric("Tilt Angle", f"{layout_config.get('tilt_angle', 'N/A')}°")
            st.metric("GCR", f"{layout_config.get('gcr', 'N/A'):.2f}")
            st.metric("Modules/Structure", f"{layout_config.get('modules_per_structure', 'N/A')}")
            st.info(f"**Row Orientation:** {layout_config.get('row_orientation', 'N/A')}")
    
    with col3:
        st.subheader("🏭 Site Config")
        if 'config' in st.session_state:
            site_config = st.session_state.config.get('site', {})
            st.metric("Walkway Width", f"{site_config.get('walkway_width', 'N/A')} m")
            st.metric("Perimeter Margin", f"{site_config.get('perimeter_margin', 'N/A')} m")
            st.metric("Equipment Spacing", f"{site_config.get('equipment_spacing', 'N/A')} m")
    
    st.markdown("---")
    
    # Placeholder for future features
    st.info("🚧 **Coming Soon:**")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        - 🗺️ **Interactive Map Selection** - Draw site boundaries using Folium
        - 📐 **Automated Layout Generation** - Optimized module placement
        - 🌓 **Shading Analysis** - Inter-row shading prediction
        """)
    
    with feature_col2:
        st.markdown("""
        - 🧹 **Soiling Loss Modeling** - Regional soiling rates with seasonal variations
        - 📊 **3D Visualization** - Interactive isometric views with PyDeck
        - 📄 **Automated Reporting** - Excel BoQ, PDF layouts, DXF exports
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            Built with ❤️ for the Solar PV Industry | 
            <a href='https://github.com/ganeshgowri-ASA/pv-layout-designer' target='_blank'>GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
