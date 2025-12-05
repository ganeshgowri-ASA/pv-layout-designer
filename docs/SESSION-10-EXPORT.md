# SESSION-10: Export & Reporting Module

## Overview
This module provides comprehensive export and reporting capabilities for the PV Layout Designer, generating professional Excel BoQ, PDF reports, and DXF CAD files.

## Features

### 1. Excel Bill of Quantities (BoQ)
Generates a multi-sheet Excel workbook with:
- **Sheet 1: Project Summary** - Key metrics, site specifications, technical parameters
- **Sheet 2: Module List** - Detailed module inventory with coordinates
- **Sheet 3: Bill of Quantities** - Complete equipment and materials list

### 2. PDF Layout Report
Creates a professional multi-page PDF report with:
- Cover page with project details
- Layout specifications table
- Equipment summary
- Supports embedded layout visualization images

### 3. DXF CAD Export
Exports layout to DXF format for CAD software with:
- Layered organization (modules, structures, boundaries)
- Module positions with IDs
- Compatible with AutoCAD 2010+

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API
```python
from src.components.exporter import generate_excel_boq, generate_pdf_report, generate_dxf_export

# Generate exports
excel_file = generate_excel_boq(layout, config)
pdf_file = generate_pdf_report(layout, config, images=None)
dxf_file = generate_dxf_export(layout)
```

### Streamlit UI
```bash
streamlit run src/app.py
```

### Demo Script
```bash
python demo_export.py
```

## Testing
```bash
pytest tests/test_exporter.py -v
```

## Dependencies
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- reportlab >= 4.0.0
- ezdxf >= 1.1.0

## Author
**Ganesh Gowri** - [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)
