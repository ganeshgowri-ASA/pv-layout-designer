# Database Module - PostgreSQL Integration

## Overview

This module provides PostgreSQL database integration for the PV Layout Designer application using SQLAlchemy ORM.

## Database Schema

### Tables

1. **projects** - Main project information
   - `id` (UUID, Primary Key)
   - `name` (VARCHAR)
   - `location_coords` (JSON)
   - `total_area_sqm` (FLOAT)
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

2. **layouts** - Generated layout configurations
   - `id` (UUID, Primary Key)
   - `project_id` (UUID, Foreign Key → projects)
   - `config_json` (TEXT)
   - `layout_json` (TEXT)
   - `total_modules` (INT)
   - `capacity_kwp` (FLOAT)
   - `gcr_ratio` (FLOAT)
   - `created_at` (TIMESTAMP)

3. **boq_items** - Bill of Quantities items
   - `id` (UUID, Primary Key)
   - `layout_id` (UUID, Foreign Key → layouts)
   - `category` (VARCHAR)
   - `item_name` (VARCHAR)
   - `quantity` (INT)
   - `unit` (VARCHAR)
   - `rate` (FLOAT)
   - `amount` (FLOAT)

## Setup

### Environment Variables

Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

For Railway deployment, this is automatically configured.

### Initialize Database

```python
from src.components.database import initialize_database

# Create all tables
initialize_database()
```

## Usage

### Save a Project

```python
from src.components.database import save_project

project_data = {
    'name': 'My Solar Plant',
    'location_coords': {'lat': 23.0225, 'lng': 72.5714},
    'total_area_sqm': 10000.0,
    'layouts': [
        {
            'config_json': {'module_width': 1.0, 'module_height': 2.0},
            'layout_json': {'rows': 10, 'modules_per_row': 20},
            'total_modules': 200,
            'capacity_kwp': 100.0,
            'gcr_ratio': 0.35,
            'boq_items': [
                {
                    'category': 'Modules',
                    'item_name': 'Solar Module 500W',
                    'quantity': 200,
                    'unit': 'Nos',
                    'rate': 15000.0,
                    'amount': 3000000.0,
                }
            ]
        }
    ]
}

project_id = save_project(project_data)
print(f"Project saved with ID: {project_id}")
```

### Load a Project

```python
from src.components.database import load_project

project_data = load_project(project_id)
print(f"Project name: {project_data['name']}")
print(f"Number of layouts: {len(project_data['layouts'])}")
```

### List All Projects

```python
from src.components.database import list_projects

projects = list_projects()
for project in projects:
    print(f"{project['name']} - {project['layout_count']} layouts")
```

### Delete a Project

```python
from src.components.database import delete_project

success = delete_project(project_id)
if success:
    print("Project deleted successfully")
```

## Testing

Run the test suite:

```bash
# Set test database URL
export DATABASE_URL="postgresql://test:test@localhost:5432/test_pvlayout"

# Run tests
pytest tests/test_database.py -v

# Run with coverage
pytest tests/test_database.py -v --cov=src.components.database --cov-report=html
```

## Features

- **SQLAlchemy ORM** - Type-safe database operations
- **Connection Pooling** - Production-ready connection management
- **Cascading Deletes** - Automatic cleanup of related data
- **Transaction Management** - Automatic rollback on errors
- **JSON Support** - Native PostgreSQL JSON storage
- **UUID Primary Keys** - Globally unique identifiers
- **Timestamps** - Automatic creation and update tracking
- **Error Handling** - Comprehensive logging and error management

## Security

- No SQL injection vulnerabilities (parameterized queries via ORM)
- Connection pooling with pre-ping for stale connection detection
- Session management with automatic cleanup
- Environment-based configuration (no hardcoded credentials)

## Railway Deployment

The database module is designed to work seamlessly with Railway PostgreSQL:

1. Add PostgreSQL plugin to your Railway project
2. Railway automatically sets the `DATABASE_URL` environment variable
3. The application will use this connection string automatically
4. Run migrations or initialize tables on first deployment

## Migration Support

For production deployments with Alembic:

```bash
# Initialize Alembic (one-time)
alembic init alembic

# Create a migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

## Dependencies

- `sqlalchemy>=2.0.0` - ORM framework
- `psycopg2-binary>=2.9.0` - PostgreSQL adapter
- `alembic>=1.11.0` - Database migrations
- `python-dotenv>=1.0.0` - Environment variable management
