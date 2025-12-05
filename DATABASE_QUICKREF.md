# Database Quick Reference

## Environment Setup

```bash
export DATABASE_URL="postgresql://user:pass@host:port/database"
pip install -r requirements.txt
```

## Initialize Database

```python
from src.components.database import initialize_database
initialize_database()
```

## Basic Operations

### Create Project

```python
from src.components.database import save_project

project_id = save_project({
    'name': 'My Solar Plant',
    'location_coords': {'lat': 23.0, 'lng': 72.0},
    'total_area_sqm': 10000.0
})
```

### Load Project

```python
from src.components.database import load_project

project = load_project(project_id)
```

### List Projects

```python
from src.components.database import list_projects

projects = list_projects()
```

### Delete Project

```python
from src.components.database import delete_project

success = delete_project(project_id)
```

## Complete Project with Layout and BoQ

```python
project_data = {
    'name': 'Complete Plant',
    'location_coords': {'lat': 23.0, 'lng': 72.0},
    'total_area_sqm': 50000.0,
    'layouts': [{
        'config_json': {'module_width': 1.0, 'module_height': 2.0},
        'layout_json': {'rows': 10, 'modules_per_row': 20},
        'total_modules': 200,
        'capacity_kwp': 100.0,
        'gcr_ratio': 0.35,
        'boq_items': [{
            'category': 'Modules',
            'item_name': 'Solar Module 500W',
            'quantity': 200,
            'unit': 'Nos',
            'rate': 15000.0,
            'amount': 3000000.0
        }]
    }]
}

project_id = save_project(project_data)
```

## Testing

```bash
# Run tests
pytest tests/test_database.py -v

# Run demo
python tests/demo_database.py
```

## Database Schema

```
projects
├── id (UUID)
├── name (VARCHAR)
├── location_coords (JSON)
├── total_area_sqm (FLOAT)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

layouts
├── id (UUID)
├── project_id (UUID) → projects.id
├── config_json (TEXT)
├── layout_json (TEXT)
├── total_modules (INT)
├── capacity_kwp (FLOAT)
├── gcr_ratio (FLOAT)
└── created_at (TIMESTAMP)

boq_items
├── id (UUID)
├── layout_id (UUID) → layouts.id
├── category (VARCHAR)
├── item_name (VARCHAR)
├── quantity (INT)
├── unit (VARCHAR)
├── rate (FLOAT)
└── amount (FLOAT)
```

## Railway Deployment

Railway automatically sets `DATABASE_URL` when you add PostgreSQL plugin.

```python
# Auto-configured, no manual setup needed
from src.components.database import initialize_database
initialize_database()  # Run once on first deployment
```
