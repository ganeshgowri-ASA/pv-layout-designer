"""
Test suite for Regional Soiling Loss Model
Tests Gujarat-specific soiling rates, seasonal variations, and tilt corrections.
"""

import pytest
from src.models.soiling_model import (
    load_regional_soiling_rates,
    calculate_seasonal_soiling,
    calculate_annual_soiling_loss,
    optimize_cleaning_schedule,
    calculate_daily_soiling_rate,
    get_gujarat_seasonal_rates,
    _get_season_from_day,
    _get_tilt_correction_factor
)


class TestRegionalSoilingRates:
    """Test loading and validation of regional soiling rates."""
    
    def test_load_gujarat_rates(self):
        """Test loading Gujarat-specific soiling rates."""
        rates = load_regional_soiling_rates('gujarat')
        
        assert 'pre_monsoon' in rates
        assert 'monsoon' in rates
        assert 'post_monsoon' in rates
        
        # Verify exact rates as per specification
        assert rates['pre_monsoon'] == 0.55
        assert rates['monsoon'] == 0.10
        assert rates['post_monsoon'] == 0.35
    
    def test_get_gujarat_seasonal_rates(self):
        """Test convenience function for Gujarat rates."""
        rates = get_gujarat_seasonal_rates()
        
        assert rates['pre_monsoon'] == 0.55
        assert rates['monsoon'] == 0.10
        assert rates['post_monsoon'] == 0.35
    
    def test_unsupported_climate_zone(self):
        """Test that unsupported climate zones raise ValueError."""
        with pytest.raises(ValueError, match="not supported"):
            load_regional_soiling_rates('mumbai')


class TestSeasonalCalculations:
    """Test seasonal soiling calculations."""
    
    def test_season_from_day(self):
        """Test season determination from day of year."""
        # Pre-monsoon: March-May (day 60-151)
        assert _get_season_from_day(90) == 'pre_monsoon'   # March
        assert _get_season_from_day(120) == 'pre_monsoon'  # April
        assert _get_season_from_day(150) == 'pre_monsoon'  # May
        
        # Monsoon: June-Sept (day 152-273)
        assert _get_season_from_day(152) == 'monsoon'  # June
        assert _get_season_from_day(200) == 'monsoon'  # July
        assert _get_season_from_day(273) == 'monsoon'  # September
        
        # Post-monsoon: Oct-Feb (day 274-365 and 1-59)
        assert _get_season_from_day(300) == 'post_monsoon'  # October
        assert _get_season_from_day(1) == 'post_monsoon'    # January
        assert _get_season_from_day(59) == 'post_monsoon'   # February
    
    def test_seasonal_soiling_pre_monsoon(self):
        """Test soiling calculation for pre-monsoon season."""
        # Day 90 is in March (pre-monsoon)
        # With 20-degree tilt (1.0x factor)
        rate = calculate_seasonal_soiling(90, 20.0)
        assert rate == 0.55  # Pre-monsoon rate with no tilt correction
    
    def test_seasonal_soiling_monsoon(self):
        """Test soiling calculation for monsoon season."""
        # Day 200 is in July (monsoon)
        # With 20-degree tilt (1.0x factor)
        rate = calculate_seasonal_soiling(200, 20.0)
        assert rate == 0.10  # Monsoon rate (natural cleaning)
    
    def test_seasonal_soiling_post_monsoon(self):
        """Test soiling calculation for post-monsoon season."""
        # Day 300 is in October (post-monsoon)
        # With 20-degree tilt (1.0x factor)
        rate = calculate_seasonal_soiling(300, 20.0)
        assert rate == 0.35  # Post-monsoon rate


class TestTiltCorrection:
    """Test tilt angle correction factors."""
    
    def test_tilt_correction_factors(self):
        """Test tilt correction factors for different angles."""
        # 0-10 degrees: 1.8x baseline
        assert _get_tilt_correction_factor(5.0) == 1.8
        assert _get_tilt_correction_factor(0.0) == 1.8
        
        # 10-20 degrees: 1.3x baseline
        assert _get_tilt_correction_factor(15.0) == 1.3
        assert _get_tilt_correction_factor(10.0) == 1.3
        
        # 20-30 degrees: 1.0x baseline
        assert _get_tilt_correction_factor(25.0) == 1.0
        assert _get_tilt_correction_factor(20.0) == 1.0
        
        # >30 degrees: 0.7x baseline
        assert _get_tilt_correction_factor(35.0) == 0.7
        assert _get_tilt_correction_factor(45.0) == 0.7
    
    def test_tilt_correction_in_seasonal_calculation(self):
        """Test tilt correction applied in seasonal soiling calculation."""
        # Pre-monsoon (0.55%/day) with different tilts
        day = 90  # March (pre-monsoon)
        
        # Low tilt (5 degrees): 1.8x
        rate_low = calculate_seasonal_soiling(day, 5.0)
        assert rate_low == pytest.approx(0.55 * 1.8, rel=0.01)
        
        # Medium tilt (15 degrees): 1.3x
        rate_med = calculate_seasonal_soiling(day, 15.0)
        assert rate_med == pytest.approx(0.55 * 1.3, rel=0.01)
        
        # Optimal tilt (25 degrees): 1.0x
        rate_opt = calculate_seasonal_soiling(day, 25.0)
        assert rate_opt == pytest.approx(0.55 * 1.0, rel=0.01)
        
        # High tilt (35 degrees): 0.7x
        rate_high = calculate_seasonal_soiling(day, 35.0)
        assert rate_high == pytest.approx(0.55 * 0.7, rel=0.01)


class TestAnnualSoilingLoss:
    """Test annual soiling loss calculations."""
    
    def test_annual_loss_no_cleaning(self):
        """Test annual soiling loss without any cleaning."""
        # Gujarat with typical tilt (20-25 degrees)
        annual_loss = calculate_annual_soiling_loss('gujarat', 25.0, 0)
        
        # Should be in the range of 12-15% as per specification
        assert 12.0 <= annual_loss <= 15.0
    
    def test_annual_loss_with_cleaning(self):
        """Test annual loss with periodic cleaning reduces overall loss."""
        tilt = 25.0
        
        # No cleaning
        loss_no_clean = calculate_annual_soiling_loss('gujarat', tilt, 0)
        
        # Monthly cleaning (12 times per year)
        loss_monthly = calculate_annual_soiling_loss('gujarat', tilt, 12)
        
        # Weekly cleaning (52 times per year)
        loss_weekly = calculate_annual_soiling_loss('gujarat', tilt, 52)
        
        # More frequent cleaning should result in lower loss
        assert loss_monthly < loss_no_clean
        assert loss_weekly < loss_monthly
    
    def test_annual_loss_tilt_comparison(self):
        """Test that higher tilt angles result in lower annual loss."""
        # Compare 15-degree vs 30-degree tilt (no cleaning)
        loss_15_deg = calculate_annual_soiling_loss('gujarat', 15.0, 0)
        loss_30_deg = calculate_annual_soiling_loss('gujarat', 30.0, 0)
        
        # Higher tilt should have lower soiling
        assert loss_30_deg < loss_15_deg


class TestCleaningOptimization:
    """Test cleaning schedule optimization."""
    
    def test_optimize_cleaning_schedule(self):
        """Test optimization of cleaning schedule."""
        result = optimize_cleaning_schedule(0.35, 25.0, 'gujarat')
        
        # Check structure
        assert 'optimal_frequency' in result
        assert 'optimal_description' in result
        assert 'expected_annual_loss' in result
        assert 'all_options' in result
        
        # Verify all options are present
        assert len(result['all_options']) > 0
        
        # Optimal frequency should be reasonable (not too extreme)
        assert result['optimal_frequency'] >= 0
    
    def test_optimization_results_format(self):
        """Test that optimization results have correct format."""
        result = optimize_cleaning_schedule(0.35, 25.0, 'gujarat')
        
        for option in result['all_options']:
            assert 'frequency' in option
            assert 'cleanings_per_year' in option
            assert 'annual_loss_percent' in option
            assert 'description' in option
            
            # Verify types
            assert isinstance(option['frequency'], int)
            assert isinstance(option['annual_loss_percent'], (int, float))
            assert isinstance(option['description'], str)


class TestCompatibilityFunctions:
    """Test compatibility functions for agent requirements."""
    
    def test_calculate_daily_soiling_rate(self):
        """Test daily soiling rate calculation by season."""
        # Pre-monsoon with 25-degree tilt
        rate = calculate_daily_soiling_rate('gujarat', 'pre_monsoon', 25.0)
        assert rate == pytest.approx(0.55 * 1.0, rel=0.01)
        
        # Monsoon with 15-degree tilt
        rate = calculate_daily_soiling_rate('gujarat', 'monsoon', 15.0)
        assert rate == pytest.approx(0.10 * 1.3, rel=0.01)
        
        # Post-monsoon with 35-degree tilt
        rate = calculate_daily_soiling_rate('gujarat', 'post_monsoon', 35.0)
        assert rate == pytest.approx(0.35 * 0.7, rel=0.01)


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow_gujarat(self):
        """Test complete workflow for Gujarat installation."""
        # Load rates
        rates = get_gujarat_seasonal_rates()
        assert rates['pre_monsoon'] == 0.55
        
        # Calculate daily rate for a specific day
        day_march = 80  # March
        tilt = 25.0
        daily_rate = calculate_seasonal_soiling(day_march, tilt)
        assert daily_rate == 0.55  # Pre-monsoon with 1.0x tilt factor
        
        # Calculate annual loss
        annual_loss = calculate_annual_soiling_loss('gujarat', tilt, 0)
        assert 12.0 <= annual_loss <= 15.0
        
        # Optimize cleaning
        optimization = optimize_cleaning_schedule(0.35, tilt)
        assert optimization['optimal_frequency'] >= 0
    
    def test_seasonal_variation_impact(self):
        """Test that seasonal variation significantly impacts calculations."""
        tilt = 25.0
        
        # Get rates for different seasons
        pre_monsoon = calculate_seasonal_soiling(90, tilt)   # March
        monsoon = calculate_seasonal_soiling(200, tilt)      # July
        post_monsoon = calculate_seasonal_soiling(300, tilt) # October
        
        # Monsoon should be significantly lower
        assert monsoon < pre_monsoon
        assert monsoon < post_monsoon
        
        # Pre-monsoon should be highest
        assert pre_monsoon > post_monsoon
        assert pre_monsoon > monsoon


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
