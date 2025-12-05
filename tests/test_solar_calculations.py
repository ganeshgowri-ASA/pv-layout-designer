"""
Unit tests for solar position calculation functions.

Tests validate the accuracy of solar position calculations against known values
and expected behaviors for different scenarios (winter/summer, day/night, etc.).
"""

import pytest
from datetime import datetime
from src.models.solar_calculations import (
    calculate_solar_elevation,
    calculate_solar_azimuth,
    get_winter_solstice_angle,
    calculate_sun_path,
    calculate_critical_hours_elevation,
)
from src.utils.constants import (
    GUJARAT_LATITUDE,
    GUJARAT_LONGITUDE,
    WINTER_SOLSTICE_DAY,
)


class TestWinterSolsticeAngle:
    """Test suite for winter solstice angle calculations."""
    
    def test_gujarat_winter_solstice(self):
        """Test that Gujarat winter solstice angle is approximately 43.5°."""
        angle = get_winter_solstice_angle(GUJARAT_LATITUDE)
        # Formula: 90 - 23.5 - 23.0225 = 43.4775°
        assert 43.0 <= angle <= 44.0, f"Expected angle ~43.5°, got {angle}°"
        
    def test_winter_solstice_precision(self):
        """Test exact calculation using the formula."""
        angle = get_winter_solstice_angle(GUJARAT_LATITUDE)
        expected = 90.0 - 23.5 - abs(GUJARAT_LATITUDE)
        assert abs(angle - expected) < 0.01, f"Expected {expected}°, got {angle}°"
    
    def test_equator_winter_solstice(self):
        """Test winter solstice angle at equator (0° latitude)."""
        angle = get_winter_solstice_angle(0.0)
        # At equator: 90 - 23.5 - 0 = 66.5°
        assert abs(angle - 66.5) < 0.1
    
    def test_northern_hemisphere(self):
        """Test winter solstice angle in northern hemisphere."""
        # New York: ~40.7° N
        angle = get_winter_solstice_angle(40.7)
        expected = 90.0 - 23.5 - 40.7
        assert abs(angle - expected) < 0.01
    
    def test_southern_hemisphere(self):
        """Test winter solstice angle in southern hemisphere."""
        # Sydney: ~33.9° S (negative latitude)
        angle = get_winter_solstice_angle(-33.9)
        # Should use absolute value: 90 - 23.5 - 33.9
        expected = 90.0 - 23.5 - 33.9
        assert abs(angle - expected) < 0.01


class TestSolarElevation:
    """Test suite for solar elevation calculations."""
    
    def test_elevation_bounds(self):
        """Test that all elevations are within valid range (-90° to 90°)."""
        # Test all hours on summer solstice (day 172)
        elevations = [
            calculate_solar_elevation(GUJARAT_LATITUDE, GUJARAT_LONGITUDE, 172, h)
            for h in range(24)
        ]
        assert all(-90 <= e <= 90 for e in elevations), "Elevation out of bounds"
    
    def test_night_hours(self):
        """Test that elevation is negative or zero during night hours."""
        # Test midnight (0:00) on winter solstice - should be night
        elevation_midnight = calculate_solar_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, 0.0
        )
        assert elevation_midnight <= 0, f"Midnight should be night, got {elevation_midnight}°"
        
        # Test 4 AM - should be night
        elevation_4am = calculate_solar_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, 4.0
        )
        assert elevation_4am <= 0, f"4 AM should be night, got {elevation_4am}°"
    
    def test_solar_noon_elevation(self):
        """Test that solar noon has highest elevation of the day."""
        # Test winter solstice
        elevations = {
            h: calculate_solar_elevation(
                GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h
            )
            for h in range(6, 18)  # 6 AM to 6 PM
        }
        max_elevation_hour = max(elevations, key=elevations.get)
        # Solar noon should be around 12:00 (may vary slightly due to equation of time)
        assert 11 <= max_elevation_hour <= 13, f"Solar noon at hour {max_elevation_hour}"
    
    def test_summer_vs_winter_elevation(self):
        """Test that summer elevation is greater than winter elevation at solar noon."""
        # Solar noon on summer solstice (day 172)
        summer_elevation = calculate_solar_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, 172, 12.0
        )
        
        # Solar noon on winter solstice (day 355)
        winter_elevation = calculate_solar_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, 12.0
        )
        
        assert summer_elevation > winter_elevation, (
            f"Summer ({summer_elevation}°) should be > winter ({winter_elevation}°)"
        )
        
        # The difference should be approximately 2 * 23.5° = 47°
        # In practice, it's slightly less due to latitude effects (~37-40°)
        difference = summer_elevation - winter_elevation
        assert 35 <= difference <= 50, f"Difference {difference}° not in expected range"


class TestSolarAzimuth:
    """Test suite for solar azimuth calculations."""
    
    def test_azimuth_range(self):
        """Test that all azimuth values are within valid range (0° to 360°)."""
        # Test all hours on winter solstice
        azimuths = [
            calculate_solar_azimuth(GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h)
            for h in range(24)
        ]
        # Filter out night hours (when elevation is negative)
        daytime_azimuths = []
        for h in range(24):
            elevation = calculate_solar_elevation(
                GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h
            )
            if elevation > 0:
                azimuth = calculate_solar_azimuth(
                    GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h
                )
                daytime_azimuths.append(azimuth)
        
        assert all(0 <= a <= 360 for a in daytime_azimuths), "Azimuth out of bounds"
    
    def test_sunrise_east(self):
        """Test that sun rises in the eastern direction."""
        # Find sunrise time (first hour with positive elevation)
        for h in range(24):
            elevation = calculate_solar_elevation(
                GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h
            )
            if elevation > 0:
                azimuth = calculate_solar_azimuth(
                    GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, h
                )
                # Sunrise should be in eastern quadrant (45° to 135°)
                assert 45 <= azimuth <= 135, f"Sunrise azimuth {azimuth}° not in eastern quadrant"
                break
    
    def test_solar_noon_south(self):
        """Test that sun is in southern direction at solar noon (Northern Hemisphere)."""
        # Solar noon on winter solstice
        azimuth_noon = calculate_solar_azimuth(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, 12.0
        )
        # In Northern Hemisphere, sun should be in southern quadrant at noon (135° to 225°)
        assert 135 <= azimuth_noon <= 225, f"Noon azimuth {azimuth_noon}° not in southern quadrant"


class TestSunPath:
    """Test suite for sun path calculations."""
    
    def test_sun_path_returns_24_hours(self):
        """Test that sun path calculation returns 24 hourly values."""
        sun_path = calculate_sun_path(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-12-21"
        )
        assert len(sun_path) == 24, f"Expected 24 hours, got {len(sun_path)}"
    
    def test_sun_path_structure(self):
        """Test that each sun path entry has correct structure."""
        sun_path = calculate_sun_path(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-12-21"
        )
        
        for entry in sun_path:
            assert 'hour' in entry, "Missing 'hour' key"
            assert 'elevation' in entry, "Missing 'elevation' key"
            assert 'azimuth' in entry, "Missing 'azimuth' key"
            assert 0 <= entry['hour'] <= 23, f"Invalid hour: {entry['hour']}"
    
    def test_sun_path_sequential_hours(self):
        """Test that hours are sequential from 0 to 23."""
        sun_path = calculate_sun_path(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-06-21"
        )
        
        for i, entry in enumerate(sun_path):
            assert entry['hour'] == i, f"Expected hour {i}, got {entry['hour']}"
    
    def test_sun_path_daytime_hours(self):
        """Test that there are positive elevations during daytime."""
        sun_path = calculate_sun_path(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-06-21"
        )
        
        # Count hours with positive elevation (daytime)
        daytime_hours = sum(1 for entry in sun_path if entry['elevation'] > 0)
        
        # Should have at least 10 hours of daylight in summer
        assert daytime_hours >= 10, f"Expected at least 10 daylight hours, got {daytime_hours}"


class TestCriticalHoursElevation:
    """Test suite for critical hours elevation calculations."""
    
    def test_critical_hours_count(self):
        """Test that critical hours returns 7 data points (9 AM to 3 PM inclusive)."""
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE
        )
        # 9, 10, 11, 12, 13, 14, 15 = 7 hours
        assert len(critical) == 7, f"Expected 7 hours, got {len(critical)}"
    
    def test_critical_hours_range(self):
        """Test that critical hours include 9 AM to 3 PM."""
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE
        )
        
        expected_hours = [9, 10, 11, 12, 13, 14, 15]
        assert list(critical.keys()) == expected_hours, (
            f"Expected hours {expected_hours}, got {list(critical.keys())}"
        )
    
    def test_critical_hours_structure(self):
        """Test that each critical hour entry has correct structure."""
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE
        )
        
        for hour, data in critical.items():
            assert 'elevation' in data, f"Missing 'elevation' for hour {hour}"
            assert 'azimuth' in data, f"Missing 'azimuth' for hour {hour}"
    
    def test_critical_hours_positive_elevation(self):
        """Test that all critical hours have positive elevation (sun is up)."""
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-12-21"
        )
        
        for hour, data in critical.items():
            assert data['elevation'] > 0, (
                f"Hour {hour} should have positive elevation, got {data['elevation']}°"
            )
    
    def test_critical_hours_custom_date(self):
        """Test critical hours with a custom date (summer solstice)."""
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-06-21"
        )
        
        assert len(critical) == 7, "Should still return 7 hours"
        
        # Summer elevations should be higher than winter
        winter_critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-12-21"
        )
        
        # Compare noon elevations
        assert critical[12]['elevation'] > winter_critical[12]['elevation'], (
            "Summer noon elevation should be higher than winter"
        )


class TestIntegrationWithConstants:
    """Test suite for integration with constants module."""
    
    def test_constants_import(self):
        """Test that constants are properly imported and used."""
        # This test verifies that the module can import and use constants
        angle = get_winter_solstice_angle(GUJARAT_LATITUDE)
        assert angle is not None
        
        elevation = calculate_solar_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, WINTER_SOLSTICE_DAY, 12.0
        )
        assert elevation is not None
    
    def test_gujarat_defaults(self):
        """Test using Gujarat default coordinates."""
        # Using constants for Gujarat location
        sun_path = calculate_sun_path(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE, "2024-12-21"
        )
        assert len(sun_path) == 24
        
        critical = calculate_critical_hours_elevation(
            GUJARAT_LATITUDE, GUJARAT_LONGITUDE
        )
        assert len(critical) == 7


# Run tests with: pytest tests/test_solar_calculations.py -v
