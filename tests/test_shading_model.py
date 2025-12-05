"""
Test suite for SESSION-06: Inter-Row Shading Analysis
Tests geometric shading calculations and bypass diode electrical modeling
"""

import pytest
import numpy as np
from datetime import datetime

from src.models.shading_model import (
    calculate_inter_row_shading,
    calculate_electrical_loss,
    calculate_hourly_shading,
    generate_shading_profile,
    calculate_shadow_length,
    analyze_inter_row_shading,
    model_bypass_diode_losses,
    generate_winter_solstice_report
)


class TestCalculateInterRowShading:
    """Test geometric shading calculations"""
    
    def test_no_shading_high_sun(self):
        """Test that high sun angle produces no shading"""
        shading = calculate_inter_row_shading(
            row_pitch=5.0,
            module_length=2.0,
            tilt_angle=20.0,
            sun_altitude=60.0
        )
        assert shading == 0.0, "High sun should produce no shading"
    
    def test_full_shading_low_sun(self):
        """Test that low sun angle with close spacing produces shading"""
        shading = calculate_inter_row_shading(
            row_pitch=2.5,
            module_length=2.0,
            tilt_angle=25.0,
            sun_altitude=15.0
        )
        assert 0.0 < shading <= 1.0, "Low sun should produce shading"
    
    def test_shading_fraction_range(self):
        """Test that shading fraction is always between 0 and 1"""
        for sun_alt in range(5, 90, 5):
            shading = calculate_inter_row_shading(
                row_pitch=4.0,
                module_length=2.0,
                tilt_angle=20.0,
                sun_altitude=float(sun_alt)
            )
            assert 0.0 <= shading <= 1.0, f"Shading fraction out of range at {sun_alt}°"
    
    def test_sun_below_horizon(self):
        """Test that sun below horizon gives full shading"""
        shading = calculate_inter_row_shading(
            row_pitch=5.0,
            module_length=2.0,
            tilt_angle=20.0,
            sun_altitude=0.0
        )
        assert shading == 1.0, "Sun at/below horizon should give full shading"
    
    def test_sun_overhead(self):
        """Test that sun directly overhead gives no shading"""
        shading = calculate_inter_row_shading(
            row_pitch=5.0,
            module_length=2.0,
            tilt_angle=20.0,
            sun_altitude=90.0
        )
        assert shading == 0.0, "Sun overhead should give no shading"
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise ValueError"""
        with pytest.raises(ValueError):
            calculate_inter_row_shading(-1.0, 2.0, 20.0, 45.0)  # Negative pitch
        
        with pytest.raises(ValueError):
            calculate_inter_row_shading(5.0, -2.0, 20.0, 45.0)  # Negative module length
        
        with pytest.raises(ValueError):
            calculate_inter_row_shading(5.0, 2.0, -10.0, 45.0)  # Negative tilt
        
        with pytest.raises(ValueError):
            calculate_inter_row_shading(5.0, 2.0, 100.0, 45.0)  # Tilt > 90
    
    def test_winter_solstice_scenario(self):
        """Test with realistic winter solstice parameters for Gujarat"""
        # Gujarat: ~22°N, Dec 21 solar noon elevation ~43.5°
        shading = calculate_inter_row_shading(
            row_pitch=5.0,
            module_length=2.0,
            tilt_angle=22.0,
            sun_altitude=43.5
        )
        assert 0.0 <= shading <= 1.0, "Winter solstice shading should be valid"


class TestCalculateElectricalLoss:
    """Test bypass diode electrical loss modeling"""
    
    def test_linear_loss_minor_shading(self):
        """Test that minor shading (<5%) results in linear loss"""
        loss = calculate_electrical_loss(0.03)
        assert loss <= 0.05, "Minor shading should have small loss"
    
    def test_bypass_diode_threshold(self):
        """Test bypass diode activation at 33% threshold"""
        # Just above threshold - should trigger first diode
        loss = calculate_electrical_loss(0.35)
        assert loss >= 0.33, "Shading >33% should trigger at least one bypass diode"
    
    def test_multiple_diode_bypass(self):
        """Test that high shading bypasses multiple diodes"""
        loss = calculate_electrical_loss(0.7)
        assert loss >= 0.66, "High shading should bypass multiple diodes"
    
    def test_full_module_loss(self):
        """Test that extreme shading results in complete module loss"""
        loss = calculate_electrical_loss(1.0)
        assert loss == 1.0, "Full shading should result in 100% loss"
    
    def test_nonlinear_behavior(self):
        """Test that electrical loss is non-linear"""
        loss_10 = calculate_electrical_loss(0.10)
        loss_20 = calculate_electrical_loss(0.20)
        loss_30 = calculate_electrical_loss(0.30)
        
        # Non-linearity: 20% shading should not be exactly 2x 10% loss
        assert not np.isclose(loss_20, 2 * loss_10, rtol=0.1), \
            "Electrical loss should be non-linear"
    
    def test_invalid_shading_fraction(self):
        """Test that invalid shading fractions raise ValueError"""
        with pytest.raises(ValueError):
            calculate_electrical_loss(-0.1)
        
        with pytest.raises(ValueError):
            calculate_electrical_loss(1.5)
    
    def test_custom_bypass_diodes(self):
        """Test with different numbers of bypass diodes"""
        # 2 diodes
        loss_2 = calculate_electrical_loss(0.6, bypass_diodes=2)
        assert 0.0 <= loss_2 <= 1.0
        
        # 4 diodes
        loss_4 = calculate_electrical_loss(0.6, bypass_diodes=4)
        assert 0.0 <= loss_4 <= 1.0


class TestCalculateHourlyShading:
    """Test hourly shading analysis"""
    
    def test_hourly_shading_returns_list(self):
        """Test that hourly shading returns a list"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        results = calculate_hourly_shading(
            layout=layout,
            date='2024-12-21',
            lat=22.0,
            lon=72.0
        )
        
        assert isinstance(results, list), "Should return a list"
        assert len(results) > 0, "Should have at least some daylight hours"
    
    def test_hourly_data_structure(self):
        """Test that hourly data has correct structure"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        results = calculate_hourly_shading(
            layout=layout,
            date='2024-06-21',
            lat=22.0,
            lon=72.0
        )
        
        for hour_data in results:
            assert 'hour' in hour_data
            assert 'sun_elevation' in hour_data
            assert 'shading_fraction' in hour_data
            assert 'electrical_loss' in hour_data
            assert 'power_loss' in hour_data
            
            # Validate ranges
            assert 0 <= hour_data['hour'] <= 23
            assert hour_data['sun_elevation'] > 0
            assert 0.0 <= hour_data['shading_fraction'] <= 1.0
            assert 0.0 <= hour_data['electrical_loss'] <= 1.0
    
    def test_winter_vs_summer_shading(self):
        """Test that winter has more shading than summer"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        winter = calculate_hourly_shading(layout, '2024-12-21', 22.0, 72.0)
        summer = calculate_hourly_shading(layout, '2024-06-21', 22.0, 72.0)
        
        winter_avg = sum(d['electrical_loss'] for d in winter) / len(winter)
        summer_avg = sum(d['electrical_loss'] for d in summer) / len(summer)
        
        assert winter_avg >= summer_avg, "Winter should have more shading than summer"


class TestGenerateShadingProfile:
    """Test annual shading profile generation"""
    
    def test_profile_structure(self):
        """Test that shading profile has correct structure"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        location = {
            'latitude': 22.0,
            'longitude': 72.0
        }
        
        profile = generate_shading_profile(layout, location)
        
        assert 'winter_solstice' in profile
        assert 'summer_solstice' in profile
        assert 'equinox' in profile
        assert 'annual_average_loss' in profile
        assert 'worst_case_loss' in profile
    
    def test_worst_case_is_winter(self):
        """Test that worst case typically occurs in winter"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        location = {
            'latitude': 22.0,
            'longitude': 72.0
        }
        
        profile = generate_shading_profile(layout, location)
        
        winter_loss = profile['winter_solstice']['average_loss']
        summer_loss = profile['summer_solstice']['average_loss']
        
        assert winter_loss >= summer_loss, "Winter should have higher average loss"


class TestCalculateShadowLength:
    """Test shadow length calculations"""
    
    def test_shadow_length_calculation(self):
        """Test basic shadow length calculation"""
        shadow = calculate_shadow_length(
            module_height=1.0,
            sun_elevation=45.0
        )
        assert np.isclose(shadow, 1.0, rtol=0.01), "45° should give shadow equal to height"
    
    def test_high_sun_short_shadow(self):
        """Test that high sun produces short shadow"""
        shadow = calculate_shadow_length(1.0, 60.0)
        assert shadow < 1.0, "High sun should produce short shadow"
    
    def test_low_sun_long_shadow(self):
        """Test that low sun produces long shadow"""
        shadow = calculate_shadow_length(1.0, 15.0)
        assert shadow > 1.0, "Low sun should produce long shadow"
    
    def test_overhead_sun_no_shadow(self):
        """Test that overhead sun produces no shadow"""
        shadow = calculate_shadow_length(1.0, 90.0)
        assert shadow == 0.0, "Overhead sun should produce no shadow"
    
    def test_invalid_module_height(self):
        """Test that negative module height raises error"""
        with pytest.raises(ValueError):
            calculate_shadow_length(-1.0, 45.0)


class TestAnalyzeInterRowShading:
    """Test integrated shading analysis"""
    
    def test_analysis_structure(self):
        """Test that analysis returns correct structure"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        solar_position = {
            'elevation': 43.5,
            'azimuth': 180.0
        }
        
        dt = datetime(2024, 12, 21, 12, 0, 0)
        
        result = analyze_inter_row_shading(layout, solar_position, dt)
        
        assert 'timestamp' in result
        assert 'sun_elevation' in result
        assert 'shading_fraction' in result
        assert 'electrical_loss' in result
        assert 'power_loss_percent' in result
        assert 'shadow_length' in result


class TestModelBypassDiodeLosses:
    """Test bypass diode loss wrapper function"""
    
    def test_percentage_conversion(self):
        """Test that percentage input/output works correctly"""
        loss = model_bypass_diode_losses(33.0)
        assert 0.0 <= loss <= 100.0, "Loss should be in percentage range"
    
    def test_wrapper_consistency(self):
        """Test that wrapper gives same result as main function"""
        shading_pct = 50.0
        loss_pct = model_bypass_diode_losses(shading_pct)
        
        shading_frac = shading_pct / 100.0
        loss_frac = calculate_electrical_loss(shading_frac)
        
        assert np.isclose(loss_pct, loss_frac * 100.0)


class TestGenerateWinterSolsticeReport:
    """Test winter solstice worst-case analysis"""
    
    def test_winter_report_structure(self):
        """Test that winter report has correct structure"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        report = generate_winter_solstice_report(layout, lat=22.0, lon=72.0)
        
        assert 'date' in report
        assert 'latitude' in report
        assert 'hourly_data' in report
        assert 'critical_hours_loss' in report
        assert 'max_loss' in report
        assert 'daily_average_loss' in report
        assert 'total_daylight_hours' in report
    
    def test_winter_report_date(self):
        """Test that report uses correct winter solstice date"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        report = generate_winter_solstice_report(layout, lat=22.0)
        
        assert '12-21' in report['date'], "Should use December 21"
    
    def test_critical_hours_calculation(self):
        """Test that critical hours (9-3 PM) are calculated"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        report = generate_winter_solstice_report(layout, lat=22.0, lon=72.0)
        
        # Critical hours should be analyzed
        assert report['critical_hours_loss'] >= 0.0
        assert report['max_loss'] >= 0.0


class TestIntegrationWithSolarCalculations:
    """Test integration with SESSION-04 solar calculations"""
    
    def test_hourly_shading_uses_solar_path(self):
        """Test that hourly shading integrates with solar calculations"""
        layout = {
            'row_pitch': 5.0,
            'module_length': 2.0,
            'tilt_angle': 22.0
        }
        
        # This should not raise any errors
        results = calculate_hourly_shading(
            layout=layout,
            date='2024-12-21',
            lat=22.0,
            lon=72.0
        )
        
        assert len(results) > 0, "Should produce hourly results"
        
        # Verify sun elevations are reasonable
        for hour_data in results:
            assert 0 < hour_data['sun_elevation'] < 90, \
                "Sun elevation should be positive and less than 90°"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
