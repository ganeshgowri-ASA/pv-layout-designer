"""
Demo script to generate sample Excel, PDF, and DXF files
"""

from src.components.exporter import generate_excel_boq, generate_pdf_report, generate_dxf_export

# Sample layout data
sample_layout = {
    'site_area': 50000,
    'usable_area': 45000,
    'total_modules': 5000,
    'total_capacity_kwp': 2750,
    'num_rows': 178,
    'gcr': 0.35,
    'inter_row_spacing': 4.5,
    'module_length': 2.278,
    'module_width': 1.134,
    'modules': [
        {
            'module_id': i,
            'row': (i // 28) + 1,
            'position': (i % 28) + 1,
            'latitude': 23.0225 + (i * 0.0001),
            'longitude': 72.5714 + (i * 0.0001),
            'status': 'Active'
        }
        for i in range(100)
    ],
    'site_boundary': [
        {'lat': 23.0, 'lon': 72.5},
        {'lat': 23.0, 'lon': 72.6},
        {'lat': 23.1, 'lon': 72.6},
        {'lat': 23.1, 'lon': 72.5},
    ]
}

# Sample configuration
sample_config = {
    'project_name': 'Demo Solar Plant - 2.75 MWp',
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

if __name__ == '__main__':
    import os
    
    # Create output directory
    os.makedirs('/tmp/pv_exports', exist_ok=True)
    
    print("Generating Excel BoQ...")
    excel_file = generate_excel_boq(sample_layout, sample_config)
    with open('/tmp/pv_exports/PV_Layout_BoQ_Demo.xlsx', 'wb') as f:
        f.write(excel_file.read())
    print("✅ Excel BoQ generated: /tmp/pv_exports/PV_Layout_BoQ_Demo.xlsx")
    
    print("\nGenerating PDF Report...")
    pdf_file = generate_pdf_report(sample_layout, sample_config)
    with open('/tmp/pv_exports/PV_Layout_Report_Demo.pdf', 'wb') as f:
        f.write(pdf_file.read())
    print("✅ PDF Report generated: /tmp/pv_exports/PV_Layout_Report_Demo.pdf")
    
    print("\nGenerating DXF Export...")
    dxf_file = generate_dxf_export(sample_layout)
    with open('/tmp/pv_exports/PV_Layout_Demo.dxf', 'wb') as f:
        f.write(dxf_file.read())
    print("✅ DXF Export generated: /tmp/pv_exports/PV_Layout_Demo.dxf")
    
    print("\n" + "="*60)
    print("All files generated successfully!")
    print("="*60)
    
    # Show file sizes
    for filename in os.listdir('/tmp/pv_exports'):
        filepath = os.path.join('/tmp/pv_exports', filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes ({size/1024:.2f} KB)")
