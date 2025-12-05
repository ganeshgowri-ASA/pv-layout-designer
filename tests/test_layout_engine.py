"""
Comprehensive test suite for the layout engine module.
Tests row pitch calculation, module placement, and layout optimization.
"""
import pytest
import math
from src.components.layout_engine import (
    calculate_usable_area,
    calculate_module_count,
    place_modules,
    optimize_layout
)
from src.utils.geometry import (
    calculate_row_pitch,
    calculate_gcr,
    calculate_polygon_area
)
from src.models.solar_calculations import get_winter_solstice_angle


class TestRowPitchCalculation:
    """Test row pitch calculation with various parameters."""
    
    def test_row_pitch_basic(self):
        """Test row pitch with standard 2m module at 15° tilt."""
        # 2m module, 15° tilt, 43.5° sun angle (typical winter in Gujarat)
        pitch = calculate_row_pitch(2.0, 15, 43.5)
        # Expected: ~2.0*cos(15°) + 2.0*sin(15°)/tan(43.5°) ≈ 1.932 + 0.542 ≈ 2.47m
        assert 2.3 <= pitch <= 2.6, f"Row pitch {pitch}m outside expected range"
    
    def test_row_pitch_high_tilt(self):
        """Test row pitch with higher tilt angle."""
        pitch = calculate_row_pitch(2.278, 25, 40)
        # Higher tilt creates longer shadows
        assert 3.0 <= pitch <= 4.0, f"Row pitch {pitch}m outside expected range"
    
    def test_row_pitch_low_sun_angle(self):
        """Test row pitch with low solar elevation (higher latitude)."""
        pitch = calculate_row_pitch(2.0, 15, 30)
        # Lower sun angle needs more spacing
        assert 2.8 <= pitch <= 3.5, f"Row pitch {pitch}m outside expected range"
    
    def test_row_pitch_zero_tilt(self):
        """Test row pitch with zero tilt (flat modules)."""
        pitch = calculate_row_pitch(2.0, 0, 45)
        # Flat modules: pitch = length (no shadow)
        assert 1.9 <= pitch <= 2.1, f"Row pitch {pitch}m should be ≈ module length"
    
    def test_row_pitch_invalid_solar_angle(self):
        """Test that invalid solar angles raise errors."""
        with pytest.raises(ValueError):
            calculate_row_pitch(2.0, 15, 0)  # Zero solar angle
        
        with pytest.raises(ValueError):
            calculate_row_pitch(2.0, 15, -10)  # Negative solar angle


class TestGCRCalculation:
    """Test Ground Coverage Ratio calculations."""
    
    def test_gcr_standard(self):
        """Test GCR calculation with standard values."""
        gcr = calculate_gcr(module_length=2.0, row_pitch=5.0)
        assert gcr == 0.4, f"GCR should be 0.4, got {gcr}"
    
    def test_gcr_range(self):
        """Test that calculated GCR falls within acceptable range."""
        gcr = calculate_gcr(module_length=2.278, row_pitch=5.0)
        assert 0.2 <= gcr <= 0.7, f"GCR {gcr} outside typical range"
    
    def test_gcr_invalid_pitch(self):
        """Test that zero/negative pitch raises error."""
        with pytest.raises(ValueError):
            calculate_gcr(2.0, 0)
        
        with pytest.raises(ValueError):
            calculate_gcr(2.0, -1.0)


class TestUsableArea:
    """Test usable area calculation with margins."""
    
    def test_usable_area_rectangular(self):
        """Test margin application on rectangular site."""
        site = [(0, 0), (100, 0), (100, 100), (0, 100)]
        usable = calculate_usable_area(site, margin=5.0)
        
        # Should reduce area by margin on all sides
        assert not usable.is_empty, "Usable area should not be empty"
        assert usable.area < 10000, "Usable area should be less than original"
        # Approximate area: (100-10) * (100-10) = 8100
        assert 7900 <= usable.area <= 8200, f"Usable area {usable.area} outside expected range"
    
    def test_usable_area_small_margin(self):
        """Test with small margin."""
        site = [(0, 0), (50, 0), (50, 50), (0, 50)]
        usable = calculate_usable_area(site, margin=1.0)
        
        assert not usable.is_empty, "Usable area should not be empty"
        # Original: 2500, Expected: ~(48)*(48) = 2304
        assert 2200 <= usable.area <= 2400, f"Usable area {usable.area} outside expected range"
    
    def test_usable_area_excessive_margin(self):
        """Test that excessive margin results in empty polygon."""
        site = [(0, 0), (10, 0), (10, 10), (0, 10)]
        usable = calculate_usable_area(site, margin=10.0)
        
        assert usable.is_empty or usable.area <= 0.01, "Excessive margin should result in empty area"
    
    def test_usable_area_zero_margin(self):
        """Test with zero margin (no change)."""
        site = [(0, 0), (100, 0), (100, 100), (0, 100)]
        usable = calculate_usable_area(site, margin=0.0)
        
        assert abs(usable.area - 10000) < 1, "Zero margin should preserve area"


class TestModuleCount:
    """Test module count estimation."""
    
    def test_module_count_basic(self):
        """Test basic module count calculation."""
        area = 10000  # 10,000 m²
        module_area = 2.278 * 1.134  # ~2.58 m²
        gcr = 0.40
        
        count = calculate_module_count(area, module_area, gcr)
        # Expected: 10000 * 0.40 / 2.58 ≈ 1550 modules
        assert 1400 <= count <= 1700, f"Module count {count} outside expected range"
    
    def test_module_count_high_gcr(self):
        """Test with high GCR."""
        count = calculate_module_count(5000, 2.5, 0.6)
        # Expected: 5000 * 0.6 / 2.5 = 1200
        assert count == 1200, f"Expected 1200 modules, got {count}"
    
    def test_module_count_low_gcr(self):
        """Test with low GCR."""
        count = calculate_module_count(10000, 2.5, 0.25)
        # Expected: 10000 * 0.25 / 2.5 = 1000
        assert count == 1000, f"Expected 1000 modules, got {count}"
    
    def test_module_count_zero_area(self):
        """Test with zero area."""
        count = calculate_module_count(0, 2.5, 0.4)
        assert count == 0, "Zero area should result in zero modules"
    
    def test_module_count_invalid_gcr(self):
        """Test that invalid GCR raises error."""
        with pytest.raises(ValueError):
            calculate_module_count(1000, 2.5, 0)
        
        with pytest.raises(ValueError):
            calculate_module_count(1000, 2.5, 1.5)


class TestModulePlacement:
    """Test the main module placement algorithm."""
    
    def test_placement_rectangular_site(self):
        """Test module placement on simple rectangular site."""
        config = {
            'latitude': 23.0225,  # Ahmedabad, Gujarat
            'module_length': 2.278,  # meters
            'module_width': 1.134,  # meters
            'module_power': 545,  # watts
            'tilt_angle': 15,
            'orientation': 'portrait',
            'walkway_width': 3.0,
            'margin': 5.0
        }
        # 100m x 100m site = 10,000 m²
        site_coords = [(0, 0), (100, 0), (100, 100), (0, 100)]
        
        result = place_modules(site_coords, config)
        
        # Validate results
        assert result['total_modules'] > 0, "Should place at least some modules"
        assert result['rows'] > 0, "Should have at least one row"
        assert result['capacity_kwp'] > 0, "Should have positive capacity"
        # GCR can be higher at low latitudes with high solar angles
        assert 0.2 <= result['actual_gcr'] <= 0.9, f"GCR {result['actual_gcr']} outside acceptable range"
        
        # Check module count is reasonable
        # With GCR ~0.8, module area ~2.58 m², usable area ~8100 m²
        # Expected: ~2500 modules
        assert 800 <= result['total_modules'] <= 3000, f"Module count {result['total_modules']} outside expected range"
    
    def test_placement_small_site(self):
        """Test placement on small site."""
        config = {
            'latitude': 23.0,
            'module_length': 2.278,
            'module_width': 1.134,
            'module_power': 545,
            'tilt_angle': 15,
            'margin': 2.0
        }
        # 20m x 20m site = 400 m²
        site_coords = [(0, 0), (20, 0), (20, 20), (0, 20)]
        
        result = place_modules(site_coords, config)
        
        assert result['total_modules'] > 0, "Should place modules even on small site"
        assert result['total_modules'] < 100, "Small site should have limited modules"
    
    def test_placement_irregular_polygon(self):
        """Test placement on irregular polygon."""
        config = {
            'latitude': 23.0,
            'module_length': 2.0,
            'module_width': 1.0,
            'module_power': 400,
            'tilt_angle': 15,
            'margin': 2.0
        }
        # L-shaped polygon
        site_coords = [(0, 0), (50, 0), (50, 30), (30, 30), (30, 50), (0, 50)]
        
        result = place_modules(site_coords, config)
        
        assert result['total_modules'] > 0, "Should handle irregular shapes"
        assert result['usable_area'] > 0, "Should have usable area"
    
    def test_placement_capacity_calculation(self):
        """Test that capacity is calculated correctly."""
        config = {
            'latitude': 23.0,
            'module_length': 2.0,
            'module_width': 1.0,
            'module_power': 500,  # 500W modules
            'tilt_angle': 15,
            'margin': 5.0
        }
        site_coords = [(0, 0), (100, 0), (100, 100), (0, 100)]
        
        result = place_modules(site_coords, config)
        
        # Verify capacity = modules × power / 1000
        expected_capacity = result['total_modules'] * 500 / 1000
        assert abs(result['capacity_kwp'] - expected_capacity) < 0.1, \
            f"Capacity calculation mismatch: {result['capacity_kwp']} vs {expected_capacity}"
    
    def test_placement_no_overlap(self):
        """Verify that modules don't overlap."""
        config = {
            'latitude': 23.0,
            'module_length': 2.0,
            'module_width': 1.0,
            'module_power': 400,
            'tilt_angle': 15,
            'margin': 2.0
        }
        site_coords = [(0, 0), (50, 0), (50, 50), (0, 50)]
        
        result = place_modules(site_coords, config)
        
        # Check that no two modules have the same position
        positions = [tuple(m['position']) for m in result['modules']]
        assert len(positions) == len(set(positions)), "Modules should have unique positions"
    
    def test_placement_within_bounds(self):
        """Verify all modules are within site boundaries."""
        config = {
            'latitude': 23.0,
            'module_length': 2.0,
            'module_width': 1.0,
            'module_power': 400,
            'tilt_angle': 15,
            'margin': 2.0
        }
        site_coords = [(0, 0), (50, 0), (50, 50), (0, 50)]
        
        result = place_modules(site_coords, config)
        
        # All module centers should be within original site bounds
        for module in result['modules']:
            cx, cy = module['center']
            assert 0 <= cx <= 50, f"Module X-center {cx} outside bounds"
            assert 0 <= cy <= 50, f"Module Y-center {cy} outside bounds"
    
    def test_placement_excessive_margin(self):
        """Test that excessive margin returns zero modules."""
        config = {
            'latitude': 23.0,
            'module_length': 2.0,
            'module_width': 1.0,
            'module_power': 400,
            'tilt_angle': 15,
            'margin': 50.0  # Excessive margin
        }
        site_coords = [(0, 0), (50, 0), (50, 50), (0, 50)]
        
        result = place_modules(site_coords, config)
        
        assert result['total_modules'] == 0, "Excessive margin should result in zero modules"
        assert 'error' in result, "Should return error message"


class TestLayoutOptimization:
    """Test layout optimization function."""
    
    def test_optimize_basic(self):
        """Test basic layout optimization."""
        module_dims = {
            'length': 2.278,
            'width': 1.134,
            'power': 545
        }
        
        result = optimize_layout(
            site_area=10000,
            module_dims=module_dims,
            target_gcr=0.40,
            latitude=23.0,
            tilt_angle=15
        )
        
        assert result['recommended_modules'] > 0, "Should recommend modules"
        assert result['row_pitch'] > 0, "Should calculate row pitch"
        assert 0.3 <= result['gcr'] <= 0.5, f"GCR {result['gcr']} outside expected range"
        assert result['capacity_kwp'] > 0, "Should calculate capacity"
    
    def test_optimize_different_gcr(self):
        """Test optimization with different GCR targets."""
        module_dims = {
            'length': 2.0,
            'width': 1.0,
            'power': 400
        }
        
        # Low GCR
        result_low = optimize_layout(5000, module_dims, 0.3, 23.0, 15)
        
        # High GCR
        result_high = optimize_layout(5000, module_dims, 0.5, 23.0, 15)
        
        # Higher GCR should recommend more modules
        assert result_high['recommended_modules'] > result_low['recommended_modules'], \
            "Higher GCR should result in more modules"
        
        # Higher GCR should have smaller row pitch
        assert result_high['row_pitch'] < result_low['row_pitch'], \
            "Higher GCR should have smaller row pitch"
    
    def test_optimize_invalid_gcr(self):
        """Test that invalid GCR raises error."""
        module_dims = {'length': 2.0, 'width': 1.0, 'power': 400}
        
        with pytest.raises(ValueError):
            optimize_layout(5000, module_dims, 0.1, 23.0, 15)  # Too low
        
        with pytest.raises(ValueError):
            optimize_layout(5000, module_dims, 0.8, 23.0, 15)  # Too high


class TestSolarCalculations:
    """Test solar angle calculations."""
    
    def test_winter_solstice_angle_gujarat(self):
        """Test winter solstice angle for Gujarat."""
        angle = get_winter_solstice_angle(23.0225)  # Ahmedabad
        # Expected: 90 - 23.0225 - 23.5 = 43.4775°
        assert 42 <= angle <= 45, f"Solar angle {angle}° outside expected range for Gujarat"
    
    def test_winter_solstice_angle_equator(self):
        """Test angle at equator."""
        angle = get_winter_solstice_angle(0)
        # Expected: 90 - 0 - 23.5 = 66.5°
        assert 65 <= angle <= 68, f"Solar angle {angle}° incorrect for equator"
    
    def test_winter_solstice_angle_high_latitude(self):
        """Test angle at high latitude."""
        angle = get_winter_solstice_angle(50)
        # Expected: 90 - 50 - 23.5 = 16.5°
        assert 15 <= angle <= 18, f"Solar angle {angle}° incorrect for high latitude"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
