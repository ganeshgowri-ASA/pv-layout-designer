# 🌞 PV Layout Designer

**Advanced Solar PV Plant Layout Designer** with Interactive Mapping, Real-time Analysis & Automated Reporting

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)

---

## 🚀 Overview

A comprehensive web-based tool for designing solar PV plant layouts with:
- 🗺️ **Interactive Map Selection** - Draw site boundaries using Folium
- 📐 **Automated Layout Generation** - Optimized module placement with GCR calculations
- 🌓 **Shading Analysis** - Inter-row shading prediction with hourly profiles
- 🧹 **Soiling Loss Modeling** - Regional soiling rates with seasonal variations
- 📷 **Camera-Based Detection** - YOLOv8 AI for real-time soiling assessment
- 📊 **3D Visualization** - Interactive isometric views with PyDeck
- 📄 **Automated Reporting** - Excel BoQ, PDF layouts, DXF exports

---

## ✨ Key Features

### 1. Map-Based Site Selection
- **Interactive Drawing Tools**: Rectangle, Polygon, Freehand boundary selection
- **Coordinate Capture**: Latitude/Longitude with UTM conversion
- **Area Calculation**: Real-time site area computation
- **Satellite Base Maps**: OpenStreetMap, Google Satellite views

### 2. Intelligent Layout Engine
- **Automated Module Placement**: Optimized row arrangements
- **GCR Optimization**: Ground Coverage Ratio calculations (20-60%)
- **Inter-Row Spacing**: No-shading distance calculations using solar angles
- **Walkway Integration**: Maintenance access paths between arrays
- **Margin Management**: Configurable perimeter setbacks

### 3. Advanced Analytics
- **Shading Analysis**:
  - Solar elevation angle calculations
  - Winter solstice worst-case scenarios
  - Hourly shadow profiles (6 AM - 6 PM)
  - Electrical bypass diode loss modeling

- **Soiling Loss Predictions**:
  - Regional soiling rates (Gujarat: 12-15% annual)
  - Seasonal variation modeling (pre-monsoon: 0.55%/day)
  - Tilt angle correction factors
  - Cleaning schedule optimization

### 4. Camera-Based Soiling Detection (Phase 2)
- **YOLOv8 Integration**: Multi-class defect detection
- **Severity Classification**: Clean/Light/Moderate/Heavy soiling
- **Power Loss Prediction**: Real-time performance impact
- **Image Preprocessing**: Automated analysis pipeline

### 5. Visualization Suite
- **2D Views**:
  - Top view with color-coded modules
  - Side profile showing tilt angles
  - Equipment placement overlay

- **3D Isometric View**:
  - Interactive PyDeck rendering
  - Adjustable pitch/bearing
  - Module height extrusion

### 6. Export & Reporting
- **Excel BoQ**: Module counts, structure specs, cable lengths
- **PDF Reports**: Layout images, specifications, coordinates
- **DXF Exports**: CAD-ready drawings (optional)

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.28+ |
| **Mapping** | Folium, Leaflet.js |
| **3D Visualization** | PyDeck, deck.gl |
| **AI/ML** | YOLOv8 (Ultralytics) |
| **Database** | PostgreSQL |
| **Exports** | Pandas, ReportLab, ezdxf |
| **Deployment** | Railway (Cloud) |
| **Version Control** | Git, GitHub |

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Git

### Local Setup

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/pv-layout-designer.git
cd pv-layout-designer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/pvlayout"
export SOILING_MODEL_PATH="models/yolov8_soiling.pt"

# Run application
streamlit run src/app.py
```

---

## 📂 Project Structure

```
pv-layout-designer/
├── src/
│   ├── app.py                    # Main Streamlit application
│   ├── components/               # Modular UI components
│   │   ├── map_selector.py       # Interactive map with drawing
│   │   ├── input_panel.py        # Configuration inputs
│   │   ├── layout_engine.py      # Core layout algorithms
│   │   ├── visualizer.py         # 2D/3D visualization
│   │   └── exporter.py           # Report generation
│   ├── models/                   # Analysis models
│   │   ├── soiling_model.py      # Soiling calculations
│   │   ├── shading_model.py      # Inter-row shading
│   │   ├── camera_detection.py   # YOLOv8 integration
│   │   └── solar_calculations.py # Sun position algorithms
│   ├── database/
│   │   ├── schema.sql            # PostgreSQL schema
│   │   └── db_manager.py         # Database operations
│   └── utils/
│       ├── geometry.py           # Spatial calculations
│       ├── validators.py         # Input validation
│       └── constants.py          # Physical constants
├── config/
│   ├── settings.yaml             # Application settings
│   └── soiling_params.json       # Regional soiling data
├── data/
│   └── soiling_rates/
│       └── india_regions.json    # Gujarat-specific rates
├── tests/                        # Comprehensive test suite
├── docs/
│   ├── PRD.md                    # Product requirements
│   └── API.md                    # API documentation
├── deployment/
│   ├── railway.toml              # Railway config
│   └── Dockerfile                # Container setup
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🎯 Usage

### Step 1: Select Site Location
1. Use interactive map to draw site boundary
2. Choose drawing tool: Rectangle, Polygon, or Freehand
3. App automatically calculates site area

### Step 2: Configure Module Specifications
- Module dimensions (length × width × thickness)
- Orientation: Portrait/Landscape
- Tilt angle: 0-90°
- Height from ground
- Modules per structure

### Step 3: Set Layout Parameters
- GCR (Ground Coverage Ratio): 20-60%
- Row orientation: North-South recommended
- Walkway width: 3-5m
- Perimeter margins

### Step 4: Generate Layout
- Click **"Generate Layout"** button
- View optimized module placement
- Analyze shading and soiling impacts

### Step 5: Visualize & Analyze
- Toggle 2D/3D views
- Review shading analysis charts
- Check soiling loss predictions

### Step 6: Export Reports
- Download Excel BoQ
- Generate PDF layout report
- Export DXF for CAD software

---

## 🔧 Development Workflow

### Branch Strategy

Each feature is developed in **isolated branches** for modular testing:

1. `feature/map-selection` - Interactive map with drawing tools
2. `feature/input-configuration` - Configuration panel
3. `feature/layout-engine` - Core calculation algorithms
4. `feature/shading-analysis` - Shading predictions
5. `feature/soiling-model` - Soiling loss modeling
6. `feature/visualization-2d` - Top/side view rendering
7. `feature/visualization-3d` - PyDeck 3D views
8. `feature/camera-detection` - YOLOv8 integration
9. `feature/export-boq` - Report generation
10. `feature/database-integration` - PostgreSQL integration

### Development Principles

✅ **LOCAL FIRST**: All coding in Claude Code IDE, never GitHub web editor  
✅ **SYNTAX VALIDATION**: Validate locally before every push  
✅ **ONE FIX = ONE COMMIT**: Surgical, traceable changes only  
✅ **COMPREHENSIVE QA**: Test every workflow after each commit  
✅ **BRANCH ISOLATION**: No cross-contamination between features  
✅ **VERIFY EVERY LAYER**: Code → Syntax → Deploy → Frontend → Database  

---

## 📊 Roadmap

### Phase 1: Core Features (Current)
- [x] GitHub repository setup
- [ ] Interactive map selection
- [ ] Layout generation engine
- [ ] Shading analysis
- [ ] Soiling modeling
- [ ] 2D/3D visualization
- [ ] Excel/PDF exports

### Phase 2: AI Integration
- [ ] YOLOv8 soiling detection
- [ ] Image preprocessing pipeline
- [ ] Real-time camera feed analysis
- [ ] Power loss predictions

### Phase 3: Advanced Features
- [ ] Multi-site project management
- [ ] Weather integration (API)
- [ ] Financial modeling (LCOE, IRR)
- [ ] Collaborative editing
- [ ] Mobile app version

---

## 🤝 Contributing

This is a private project. For collaboration inquiries, contact the repository owner.

---

## 📄 License

Proprietary - All Rights Reserved

---

## 📧 Contact

**Developer**: Ganesh Gowri  
**GitHub**: [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)  
**Repository**: [pv-layout-designer](https://github.com/ganeshgowri-ASA/pv-layout-designer)  

---

**Built with ❤️ for the Solar PV Industry**