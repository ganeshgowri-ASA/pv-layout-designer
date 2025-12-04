"""
PV Layout Designer - Main Streamlit Application
Interactive Solar PV Plant Layout Designer
"""

import streamlit as st
from datetime import datetime
from src.components.exporter import generate_excel_boq, generate_pdf_report, generate_dxf_export


def init_session_state():
    """Initialize session state variables"""
    if 'layout' not in st.session_state:
        # Sample layout data for demonstration
        st.session_state['layout'] = {
            'site_area': 50000,
            'usable_area': 45000,
            'total_modules': 5000,
            'total_capacity_kwp': 2750,
            'num_rows': 178,
            'gcr': 0.35,
            'inter_row_spacing': 4.5,
            'modules': [],
            'site_boundary': []
        }
    
    if 'config' not in st.session_state:
        # Sample configuration
        st.session_state['config'] = {
            'project_name': 'Sample Solar Plant',
            'location': 'Gujarat, India',
            'latitude': 23.0225,
            'longitude': 72.5714,
            'designer': 'PV Layout Designer',
            'module_power': 550,
            'module_length': 2.278,
            'module_width': 1.134,
            'tilt_angle': 25,
            'orientation': 'Portrait',
            'row_orientation': 'North-South',
            'module_height': 1.5,
            'modules_per_structure': 28
        }


def main():
    """Main application"""
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="🌞",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🌞 PV Layout Designer")
    st.markdown("### Advanced Solar PV Plant Layout Designer")
    st.markdown("---")
    
    # Sidebar - Project Configuration
    with st.sidebar:
        st.header("📋 Project Configuration")
        
        project_name = st.text_input(
            "Project Name",
            value=st.session_state['config']['project_name']
        )
        st.session_state['config']['project_name'] = project_name
        
        location = st.text_input(
            "Location",
            value=st.session_state['config']['location']
        )
        st.session_state['config']['location'] = location
        
        st.markdown("---")
        st.header("⚙️ Module Specifications")
        
        module_power = st.number_input(
            "Module Power (Wp)",
            min_value=300,
            max_value=800,
            value=st.session_state['config']['module_power']
        )
        st.session_state['config']['module_power'] = module_power
        
        tilt_angle = st.slider(
            "Tilt Angle (°)",
            min_value=0,
            max_value=45,
            value=st.session_state['config']['tilt_angle']
        )
        st.session_state['config']['tilt_angle'] = tilt_angle
        
        modules_per_structure = st.number_input(
            "Modules per Structure",
            min_value=1,
            max_value=50,
            value=st.session_state['config']['modules_per_structure']
        )
        st.session_state['config']['modules_per_structure'] = modules_per_structure
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Layout Summary", "📥 Export Reports", "ℹ️ About"])
    
    # Tab 1: Layout Summary
    with tab1:
        st.header("Layout Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Modules",
                f"{st.session_state['layout']['total_modules']:,}"
            )
        
        with col2:
            st.metric(
                "Total Capacity",
                f"{st.session_state['layout']['total_capacity_kwp'] / 1000:.2f} MWp"
            )
        
        with col3:
            st.metric(
                "Site Area",
                f"{st.session_state['layout']['site_area'] / 10000:.2f} Ha"
            )
        
        with col4:
            st.metric(
                "GCR",
                f"{st.session_state['layout']['gcr']:.1%}"
            )
        
        st.markdown("---")
        
        # Display technical details
        st.subheader("Technical Specifications")
        
        specs_col1, specs_col2 = st.columns(2)
        
        with specs_col1:
            st.write("**Layout Parameters:**")
            st.write(f"- Number of Rows: {st.session_state['layout']['num_rows']}")
            st.write(f"- Inter-Row Spacing: {st.session_state['layout']['inter_row_spacing']:.2f} m")
            st.write(f"- Module Orientation: {st.session_state['config']['orientation']}")
            st.write(f"- Row Orientation: {st.session_state['config']['row_orientation']}")
        
        with specs_col2:
            st.write("**Module Specifications:**")
            st.write(f"- Module Power: {st.session_state['config']['module_power']} Wp")
            st.write(f"- Tilt Angle: {st.session_state['config']['tilt_angle']}°")
            st.write(f"- Module Dimensions: {st.session_state['config']['module_length']:.2f} × {st.session_state['config']['module_width']:.2f} m")
            st.write(f"- Modules per Structure: {st.session_state['config']['modules_per_structure']}")
    
    # Tab 2: Export Reports
    with tab2:
        st.header("📥 Export Reports")
        st.markdown("Download professional reports and CAD files for your PV layout design.")
        
        st.markdown("---")
        
        # Excel Export
        st.subheader("📊 Excel Bill of Quantities (BoQ)")
        st.write("Comprehensive Excel workbook with project summary, module list, and detailed BoQ.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**Includes:**")
            st.write("- Sheet 1: Project Summary with key metrics")
            st.write("- Sheet 2: Detailed Module List with coordinates")
            st.write("- Sheet 3: Bill of Quantities with equipment and materials")
        
        with col2:
            if st.button("🔄 Generate Excel", use_container_width=True):
                with st.spinner("Generating Excel BoQ..."):
                    try:
                        excel_file = generate_excel_boq(
                            st.session_state['layout'],
                            st.session_state['config']
                        )
                        st.session_state['excel_file'] = excel_file
                        st.success("✅ Excel generated!")
                    except Exception as e:
                        st.error(f"Error generating Excel: {str(e)}")
        
        with col3:
            if 'excel_file' in st.session_state:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=st.session_state['excel_file'],
                    file_name=f"PV_Layout_BoQ_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.markdown("---")
        
        # PDF Export
        st.subheader("📄 PDF Layout Report")
        st.write("Professional PDF report with layout specifications, visualizations, and equipment summary.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**Includes:**")
            st.write("- Cover page with project details")
            st.write("- Layout specifications table")
            st.write("- Equipment summary and BoQ")
            st.write("- Professional formatting and styling")
        
        with col2:
            if st.button("🔄 Generate PDF", use_container_width=True):
                with st.spinner("Generating PDF Report..."):
                    try:
                        pdf_file = generate_pdf_report(
                            st.session_state['layout'],
                            st.session_state['config'],
                            images=None  # Can pass images dictionary if available
                        )
                        st.session_state['pdf_file'] = pdf_file
                        st.success("✅ PDF generated!")
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
        
        with col3:
            if 'pdf_file' in st.session_state:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=st.session_state['pdf_file'],
                    file_name=f"PV_Layout_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        st.markdown("---")
        
        # DXF Export
        st.subheader("📐 DXF CAD Export (Optional)")
        st.write("Export layout to DXF format for use in AutoCAD and other CAD software.")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**Includes:**")
            st.write("- Site boundary outline")
            st.write("- Module positions and IDs")
            st.write("- Layered organization (modules, structures, dimensions)")
            st.write("- Compatible with AutoCAD 2010+")
        
        with col2:
            if st.button("🔄 Generate DXF", use_container_width=True):
                with st.spinner("Generating DXF file..."):
                    try:
                        dxf_file = generate_dxf_export(st.session_state['layout'])
                        st.session_state['dxf_file'] = dxf_file
                        st.success("✅ DXF generated!")
                    except Exception as e:
                        st.error(f"Error generating DXF: {str(e)}")
        
        with col3:
            if 'dxf_file' in st.session_state:
                st.download_button(
                    label="⬇️ Download DXF",
                    data=st.session_state['dxf_file'],
                    file_name=f"PV_Layout_{datetime.now().strftime('%Y%m%d')}.dxf",
                    mime="application/dxf",
                    use_container_width=True
                )
        
        st.markdown("---")
        st.info("💡 **Tip:** Generate all reports after finalizing your layout design for best results.")
    
    # Tab 3: About
    with tab3:
        st.header("ℹ️ About PV Layout Designer")
        
        st.markdown("""
        ### Overview
        PV Layout Designer is an advanced web-based tool for designing solar PV plant layouts with:
        
        - 🗺️ **Interactive Map Selection** - Draw site boundaries using Folium
        - 📐 **Automated Layout Generation** - Optimized module placement with GCR calculations
        - 🌓 **Shading Analysis** - Inter-row shading prediction
        - 📊 **3D Visualization** - Interactive isometric views
        - 📄 **Automated Reporting** - Excel BoQ, PDF layouts, DXF exports
        
        ### Technology Stack
        - **Frontend:** Streamlit
        - **Exports:** Pandas, OpenPyXL, ReportLab, ezdxf
        - **Visualization:** PyDeck, Folium
        
        ### Session 10: Export & Reporting
        This module provides professional report generation capabilities:
        - Excel BoQ with multiple sheets
        - PDF reports with layout specifications
        - DXF files for CAD software integration
        
        ### Developer
        **Ganesh Gowri** - [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)
        
        ---
        Built with ❤️ for the Solar PV Industry
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: gray;'>PV Layout Designer v1.0 | "
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
