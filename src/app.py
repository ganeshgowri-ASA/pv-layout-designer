"""
PV Layout Designer - Main Streamlit Application
SESSION-06: Shading Analysis Integration
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Import shading model functions
from src.models.shading_model import (
    calculate_hourly_shading,
    generate_shading_profile,
    generate_winter_solstice_report
)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="PV Layout Designer",
        page_icon="🌞",
        layout="wide"
    )
    
    st.title("🌞 PV Layout Designer")
    st.subheader("Advanced Solar PV Plant Layout with Shading Analysis")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Layout parameters
    st.sidebar.subheader("Layout Parameters")
    row_pitch = st.sidebar.number_input("Row Pitch (m)", min_value=2.0, max_value=10.0, value=5.0, step=0.5)
    module_length = st.sidebar.number_input("Module Length (m)", min_value=1.0, max_value=3.0, value=2.0, step=0.1)
    tilt_angle = st.sidebar.number_input("Tilt Angle (°)", min_value=0, max_value=45, value=22, step=1)
    
    # Location parameters
    st.sidebar.subheader("Location")
    latitude = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=22.0, step=0.1)
    longitude = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, value=72.0, step=0.1)
    
    # Create layout dictionary
    layout = {
        'row_pitch': row_pitch,
        'module_length': module_length,
        'tilt_angle': tilt_angle
    }
    
    location = {
        'latitude': latitude,
        'longitude': longitude
    }
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Shading Analysis", "📅 Winter Solstice", "📈 Annual Profile"])
    
    with tab1:
        st.header("Daily Shading Analysis")
        
        # Date selection
        selected_date = st.date_input("Select Date", value=None)
        
        if selected_date:
            date_str = selected_date.strftime('%Y-%m-%d')
            
            try:
                # Calculate hourly shading
                shading_data = calculate_hourly_shading(
                    layout=layout,
                    date=date_str,
                    lat=latitude,
                    lon=longitude
                )
                
                if shading_data:
                    # Create plot
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                    
                    hours = [d['hour'] for d in shading_data]
                    losses = [d['power_loss'] for d in shading_data]
                    elevations = [d['sun_elevation'] for d in shading_data]
                    
                    # Power loss plot
                    ax1.plot(hours, losses, marker='o', color='red', linewidth=2)
                    ax1.set_xlabel('Hour of Day')
                    ax1.set_ylabel('Power Loss (%)')
                    ax1.set_title(f'Shading Power Losses - {date_str}')
                    ax1.grid(True, alpha=0.3)
                    ax1.set_xlim(min(hours), max(hours))
                    
                    # Sun elevation plot
                    ax2.plot(hours, elevations, marker='s', color='orange', linewidth=2)
                    ax2.set_xlabel('Hour of Day')
                    ax2.set_ylabel('Sun Elevation (°)')
                    ax2.set_title('Solar Elevation Angle')
                    ax2.grid(True, alpha=0.3)
                    ax2.set_xlim(min(hours), max(hours))
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Summary metrics
                    avg_loss = sum(losses) / len(losses)
                    max_loss = max(losses)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Average Loss", f"{avg_loss:.1f}%")
                    col2.metric("Maximum Loss", f"{max_loss:.1f}%")
                    col3.metric("Daylight Hours", len(shading_data))
                    
                    # Show data table
                    with st.expander("View Hourly Data"):
                        st.dataframe(shading_data)
                else:
                    st.warning("No daylight hours for selected date")
                    
            except Exception as e:
                st.error(f"Error calculating shading: {str(e)}")
    
    with tab2:
        st.header("❄️ Winter Solstice Analysis (Worst Case)")
        
        if st.button("Generate Winter Solstice Report"):
            try:
                # Generate report
                report = generate_winter_solstice_report(
                    layout=layout,
                    lat=latitude,
                    lon=longitude
                )
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Critical Hours Loss (9-3PM)", f"{report['critical_hours_loss']:.1f}%")
                col2.metric("Maximum Loss", f"{report['max_loss']:.1f}%")
                col3.metric("Daily Average", f"{report['daily_average_loss']:.1f}%")
                col4.metric("Daylight Hours", report['total_daylight_hours'])
                
                # Plot
                hourly_data = report['hourly_data']
                hours = [d['hour'] for d in hourly_data]
                losses = [d['power_loss'] for d in hourly_data]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(hours, losses, marker='o', color='darkred', linewidth=2)
                ax.fill_between(hours, losses, alpha=0.3, color='red')
                ax.set_xlabel('Hour of Day')
                ax.set_ylabel('Power Loss (%)')
                ax.set_title('Winter Solstice Shading Losses (December 21)')
                ax.grid(True, alpha=0.3)
                
                # Highlight critical hours
                critical_hours = [h for h in hours if 9 <= h <= 15]
                critical_losses = [losses[hours.index(h)] for h in critical_hours]
                ax.scatter(critical_hours, critical_losses, color='orange', s=100, 
                          label='Critical Hours (9-3PM)', zorder=5)
                ax.legend()
                
                st.pyplot(fig)
                
                # Show data
                with st.expander("View Winter Solstice Data"):
                    st.dataframe(hourly_data)
                    
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    with tab3:
        st.header("📆 Annual Shading Profile")
        
        if st.button("Generate Annual Profile"):
            try:
                # Generate annual profile
                profile = generate_shading_profile(layout, location)
                
                # Display summary metrics
                col1, col2 = st.columns(2)
                col1.metric("Annual Average Loss", f"{profile['annual_average_loss']:.1f}%")
                col2.metric("Worst Case Loss", f"{profile['worst_case_loss']:.1f}%")
                
                # Seasonal comparison
                st.subheader("Seasonal Comparison")
                
                seasons = ['Winter Solstice', 'Equinox', 'Summer Solstice']
                avg_losses = [
                    profile['winter_solstice']['average_loss'],
                    profile['equinox']['average_loss'],
                    profile['summer_solstice']['average_loss']
                ]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                bars = ax.bar(seasons, avg_losses, color=['blue', 'green', 'orange'])
                ax.set_ylabel('Average Daily Loss (%)')
                ax.set_title('Seasonal Shading Loss Comparison')
                ax.grid(True, alpha=0.3, axis='y')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%',
                           ha='center', va='bottom')
                
                st.pyplot(fig)
                
                # Detailed seasonal data
                with st.expander("View Seasonal Details"):
                    st.subheader("Winter Solstice (Dec 21)")
                    st.write(f"Average Loss: {profile['winter_solstice']['average_loss']:.1f}%")
                    
                    st.subheader("Equinox (Mar 21)")
                    st.write(f"Average Loss: {profile['equinox']['average_loss']:.1f}%")
                    
                    st.subheader("Summer Solstice (Jun 21)")
                    st.write(f"Average Loss: {profile['summer_solstice']['average_loss']:.1f}%")
                    
            except Exception as e:
                st.error(f"Error generating annual profile: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("**SESSION-06: Inter-Row Shading Analysis with Electrical Loss Modeling**")


if __name__ == '__main__':
    main()
