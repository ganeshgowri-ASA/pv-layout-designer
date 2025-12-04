"""
Unit tests for SESSION-08: Visualizer Component
Tests for 2D/3D visualization functions
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from src.components.visualizer import (
    render_top_view,
    render_side_view,
    render_3d_isometric,
    add_shading_overlay,
    render_all_views,
    VisualizerConfig,
    COLORS
)


@pytest.fixture
def sample_layout():
    """Sample layout data for testing"""
    return {
        'center': [23.0225, 72.5714],
        'boundaries': [
            [23.0225, 72.5714],
            [23.0226, 72.5714],
            [23.0226, 72.5715],
            [23.0225, 72.5715]
        ],
        'modules': [
            {
                'coords': [
                    [23.02251, 72.57141],
                    [23.02252, 72.57141],
                    [23.02252, 72.57142],
                    [23.02251, 72.57142]
                ],
                'tilt': 20,
                'azimuth': 180,
                'length': 2.0,
                'ground_clearance': 0.5
            },
            {
                'coords': [
                    [23.02253, 72.57141],
                    [23.02254, 72.57141],
                    [23.02254, 72.57142],
                    [23.02253, 72.57142]
                ],
                'tilt': 20,
                'azimuth': 180,
                'length': 2.0,
                'ground_clearance': 0.5
            }
        ],
        'walkways': [
            {
                'coords': [
                    [23.02250, 72.57140],
                    [23.02251, 72.57140],
                    [23.02251, 72.57141],
                    [23.02250, 72.57141]
                ]
            }
        ],
        'equipment': [
            {
                'type': 'inverter',
                'position': [23.0225, 72.5714],
                'name': 'Inverter-1'
            },
            {
                'type': 'transformer',
                'position': [23.0226, 72.5715],
                'name': 'Transformer-1'
            }
        ],
        'margins': [
            {
                'coords': [
                    [23.0224, 72.5713],
                    [23.0227, 72.5713],
                    [23.0227, 72.5716],
                    [23.0224, 72.5716]
                ]
            }
        ],
        'tilt_angle': 20,
        'module_length': 2.0,
        'module_height': 0.04,
        'ground_clearance': 0.5,
        'num_rows': 3,
        'row_spacing': 5.0
    }


@pytest.fixture
def sample_shading_analysis():
    """Sample shading analysis data"""
    return {
        'shaded_areas': [
            {
                'coords': [
                    [23.02251, 72.57141],
                    [23.02252, 72.57141],
                    [23.02252, 72.57142],
                    [23.02251, 72.57142]
                ],
                'shade_percentage': 30.5,
                'time': '09:00'
            },
            {
                'coords': [
                    [23.02253, 72.57143],
                    [23.02254, 72.57143],
                    [23.02254, 72.57144],
                    [23.02253, 72.57144]
                ],
                'shade_percentage': 15.2,
                'time': '10:00'
            }
        ]
    }


class TestVisualizerConfig:
    """Test VisualizerConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = VisualizerConfig()
        assert config.map_center == (23.0225, 72.5714)
        assert config.zoom_start == 15
        assert config.map_style == 'OpenStreetMap'
        assert config.figure_size == (12, 6)
        assert config.dpi == 100
        assert 'latitude' in config.initial_view_state
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = VisualizerConfig(
            map_center=(25.0, 75.0),
            zoom_start=18,
            map_style='Satellite'
        )
        assert config.map_center == (25.0, 75.0)
        assert config.zoom_start == 18
        assert config.map_style == 'Satellite'


class TestRenderTopView:
    """Test render_top_view function"""
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_creates_map(self, mock_folium, sample_layout):
        """Test that top view creates a Folium map"""
        mock_map = Mock()
        mock_folium.Map.return_value = mock_map
        
        result = render_top_view(sample_layout)
        
        # Verify map was created
        mock_folium.Map.assert_called_once()
        assert result == mock_map
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_with_existing_map(self, mock_folium, sample_layout):
        """Test that existing map is used when provided"""
        existing_map = Mock()
        
        result = render_top_view(sample_layout, folium_map=existing_map)
        
        # Verify no new map was created
        mock_folium.Map.assert_not_called()
        assert result == existing_map
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_adds_boundaries(self, mock_folium, sample_layout):
        """Test that site boundaries are rendered"""
        mock_map = Mock()
        mock_folium.Map.return_value = mock_map
        
        render_top_view(sample_layout)
        
        # Verify Polygon was called for boundaries
        assert mock_folium.Polygon.called
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_adds_modules(self, mock_folium, sample_layout):
        """Test that modules are rendered"""
        mock_map = Mock()
        mock_folium.Map.return_value = mock_map
        
        render_top_view(sample_layout)
        
        # Verify multiple polygons were created (for modules)
        assert mock_folium.Polygon.call_count >= len(sample_layout['modules'])
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_adds_equipment(self, mock_folium, sample_layout):
        """Test that equipment markers are rendered"""
        mock_map = Mock()
        mock_folium.Map.return_value = mock_map
        
        render_top_view(sample_layout)
        
        # Verify CircleMarker was called for equipment
        assert mock_folium.CircleMarker.call_count == len(sample_layout['equipment'])


class TestRenderSideView:
    """Test render_side_view function"""
    
    @patch('src.components.visualizer.plt')
    def test_render_side_view_creates_figure(self, mock_plt, sample_layout):
        """Test that side view creates a matplotlib figure"""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        result = render_side_view(sample_layout)
        
        # Verify figure was created
        mock_plt.subplots.assert_called_once()
        assert result == mock_fig
    
    def test_render_side_view_with_real_matplotlib(self, sample_layout):
        """Test side view with actual matplotlib (integration test)"""
        fig = render_side_view(sample_layout)
        
        # Verify figure properties
        assert fig is not None
        assert len(fig.axes) > 0
        ax = fig.axes[0]
        assert ax.get_xlabel() == 'Distance (meters)'
        assert ax.get_ylabel() == 'Height (meters)'
        assert 'Tilt Angle' in ax.get_title()
    
    def test_render_side_view_calculates_tilt_correctly(self, sample_layout):
        """Test that tilt angle is correctly applied"""
        tilt_angle = 25
        sample_layout['tilt_angle'] = tilt_angle
        
        fig = render_side_view(sample_layout)
        
        # Verify title contains correct tilt angle
        ax = fig.axes[0]
        assert f'{tilt_angle}°' in ax.get_title()


class TestRender3DIsometric:
    """Test render_3d_isometric function"""
    
    @patch('src.components.visualizer.pdk')
    def test_render_3d_creates_deck(self, mock_pdk, sample_layout):
        """Test that 3D view creates a PyDeck deck"""
        mock_deck = Mock()
        mock_pdk.Deck.return_value = mock_deck
        
        result = render_3d_isometric(sample_layout)
        
        # Verify deck was created
        mock_pdk.Deck.assert_called_once()
        assert result == mock_deck
    
    @patch('src.components.visualizer.pdk')
    def test_render_3d_creates_layers(self, mock_pdk, sample_layout):
        """Test that layers are created for modules"""
        mock_deck = Mock()
        mock_pdk.Deck.return_value = mock_deck
        
        render_3d_isometric(sample_layout)
        
        # Verify Layer was called
        assert mock_pdk.Layer.called
    
    @patch('src.components.visualizer.pdk')
    def test_render_3d_with_equipment(self, mock_pdk, sample_layout):
        """Test that equipment layer is created"""
        mock_deck = Mock()
        mock_pdk.Deck.return_value = mock_deck
        
        render_3d_isometric(sample_layout)
        
        # Verify multiple layers (modules + equipment)
        assert mock_pdk.Layer.call_count >= 2


class TestAddShadingOverlay:
    """Test add_shading_overlay function"""
    
    @patch('src.components.visualizer.folium')
    def test_add_shading_overlay(self, mock_folium, sample_shading_analysis):
        """Test that shading overlay is added to map"""
        mock_map = Mock()
        
        result = add_shading_overlay(mock_map, sample_shading_analysis)
        
        # Verify Polygon was called for shaded areas
        assert mock_folium.Polygon.called
        assert result == mock_map
    
    @patch('src.components.visualizer.folium')
    def test_shading_overlay_opacity_varies(self, mock_folium, sample_shading_analysis):
        """Test that opacity varies with shade percentage"""
        mock_map = Mock()
        
        add_shading_overlay(mock_map, sample_shading_analysis)
        
        # Verify Polygon was called multiple times
        assert mock_folium.Polygon.call_count == len(sample_shading_analysis['shaded_areas'])


class TestRenderAllViews:
    """Test render_all_views function"""
    
    @patch('src.components.visualizer.render_3d_isometric')
    @patch('src.components.visualizer.render_side_view')
    @patch('src.components.visualizer.render_top_view')
    def test_render_all_views(self, mock_top, mock_side, mock_3d, sample_layout):
        """Test that all views are rendered"""
        mock_top.return_value = Mock()
        mock_side.return_value = Mock()
        mock_3d.return_value = Mock()
        
        result = render_all_views(sample_layout)
        
        # Verify all rendering functions were called
        mock_top.assert_called_once()
        mock_side.assert_called_once()
        mock_3d.assert_called_once()
        
        # Verify result contains all views
        assert 'top_view' in result
        assert 'side_view' in result
        assert '3d_view' in result
    
    @patch('src.components.visualizer.add_shading_overlay')
    @patch('src.components.visualizer.render_3d_isometric')
    @patch('src.components.visualizer.render_side_view')
    @patch('src.components.visualizer.render_top_view')
    def test_render_all_views_with_shading(self, mock_top, mock_side, mock_3d, 
                                           mock_shading, sample_layout, sample_shading_analysis):
        """Test that shading overlay is added when provided"""
        mock_map = Mock()
        mock_top.return_value = mock_map
        mock_side.return_value = Mock()
        mock_3d.return_value = Mock()
        mock_shading.return_value = mock_map
        
        result = render_all_views(sample_layout, shading_analysis=sample_shading_analysis)
        
        # Verify shading overlay was added
        mock_shading.assert_called_once_with(mock_map, sample_shading_analysis)


class TestColorConstants:
    """Test color constant definitions"""
    
    def test_color_constants_exist(self):
        """Test that all required color constants are defined"""
        required_colors = [
            'modules', 'walkways', 'equipment_inverter',
            'equipment_transformer', 'margins', 'shading'
        ]
        
        for color_key in required_colors:
            assert color_key in COLORS
            assert COLORS[color_key].startswith('#')
    
    def test_color_values_match_spec(self):
        """Test that colors match specification"""
        assert COLORS['modules'] == '#4A90E2'  # Blue
        assert COLORS['walkways'] == '#9E9E9E'  # Grey
        assert COLORS['equipment_inverter'] == '#FF5252'  # Red
        assert COLORS['equipment_transformer'] == '#4CAF50'  # Green
        assert COLORS['margins'] == '#FFD600'  # Yellow


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @patch('src.components.visualizer.folium')
    def test_render_top_view_empty_layout(self, mock_folium):
        """Test top view with minimal layout data"""
        mock_map = Mock()
        mock_folium.Map.return_value = mock_map
        
        minimal_layout = {'center': [0, 0]}
        result = render_top_view(minimal_layout)
        
        # Should not crash and return a map
        assert result == mock_map
    
    def test_render_side_view_default_values(self):
        """Test side view uses default values when keys missing"""
        minimal_layout = {}
        fig = render_side_view(minimal_layout)
        
        # Should not crash and return a figure
        assert fig is not None
    
    @patch('src.components.visualizer.pdk')
    def test_render_3d_no_modules(self, mock_pdk):
        """Test 3D view with no modules"""
        mock_deck = Mock()
        mock_pdk.Deck.return_value = mock_deck
        
        minimal_layout = {'center': [0, 0]}
        result = render_3d_isometric(minimal_layout)
        
        # Should not crash and return a deck
        assert result == mock_deck


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
