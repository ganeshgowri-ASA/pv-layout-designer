#!/usr/bin/env python
"""
Quick validation script for visualizer component
Tests basic functionality without Streamlit UI
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.components.visualizer import (
    render_top_view,
    render_side_view,
    render_3d_isometric,
    render_all_views,
    VisualizerConfig,
    COLORS
)

def main():
    print("=" * 60)
    print("SESSION-08: Visualizer Validation")
    print("=" * 60)
    
    # Sample layout
    layout = {
        'center': [23.0225, 72.5714],
        'boundaries': [
            [23.0220, 72.5710],
            [23.0230, 72.5710],
            [23.0230, 72.5720],
            [23.0220, 72.5720]
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
            }
        ],
        'tilt_angle': 20,
        'module_length': 2.0,
        'module_height': 0.04,
        'ground_clearance': 0.5,
        'num_rows': 3,
        'row_spacing': 5.0
    }
    
    print("\n1. Testing VisualizerConfig...")
    config = VisualizerConfig()
    print(f"   ✓ Default config created: center={config.map_center}")
    
    print("\n2. Testing render_top_view...")
    top_view = render_top_view(layout, config=config)
    print(f"   ✓ Top view created: {type(top_view).__name__}")
    
    print("\n3. Testing render_side_view...")
    side_view = render_side_view(layout, config=config)
    print(f"   ✓ Side view created: {type(side_view).__name__}")
    print(f"   ✓ Figure has {len(side_view.axes)} axes")
    
    print("\n4. Testing render_3d_isometric...")
    isometric_3d = render_3d_isometric(layout, config=config)
    print(f"   ✓ 3D view created: {type(isometric_3d).__name__}")
    
    print("\n5. Testing render_all_views...")
    views = render_all_views(layout, config=config)
    print(f"   ✓ All views rendered: {list(views.keys())}")
    
    print("\n6. Testing color constants...")
    required_colors = ['modules', 'walkways', 'equipment_inverter', 
                      'equipment_transformer', 'margins', 'shading']
    for color in required_colors:
        assert color in COLORS, f"Missing color: {color}"
    print(f"   ✓ All {len(required_colors)} color constants defined")
    
    print("\n7. Testing shading overlay...")
    shading_analysis = {
        'shaded_areas': [
            {
                'coords': layout['modules'][0]['coords'],
                'shade_percentage': 30.0,
                'time': '09:00'
            }
        ]
    }
    views_with_shading = render_all_views(layout, shading_analysis=shading_analysis)
    print(f"   ✓ Views with shading overlay created")
    
    print("\n" + "=" * 60)
    print("✅ ALL VALIDATION CHECKS PASSED")
    print("=" * 60)
    
    print("\nVisualization Summary:")
    print(f"  • Modules rendered: {len(layout.get('modules', []))}")
    print(f"  • Walkways rendered: {len(layout.get('walkways', []))}")
    print(f"  • Equipment markers: {len(layout.get('equipment', []))}")
    print(f"  • Tilt angle: {layout.get('tilt_angle', 0)}°")
    print(f"  • Row spacing: {layout.get('row_spacing', 0)}m")
    
    print("\nReady for Streamlit integration!")
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
