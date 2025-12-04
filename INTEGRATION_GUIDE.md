# PostgreSQL Database Integration Guide

## Session 09: Database Implementation Complete ✅

This guide provides step-by-step instructions for integrating and testing the PostgreSQL database module.

## 📦 What's Included

### Files Created

1. **database/schema.sql** - PostgreSQL schema with tables, indexes, and triggers
2. **src/components/database.py** - SQLAlchemy ORM with full CRUD operations
3. **tests/test_database.py** - Comprehensive test suite (17 test cases)
4. **tests/demo_database.py** - Interactive demo script
5. **database/README.md** - Detailed module documentation
6. **requirements.txt** - Python dependencies
7. **.env.example** - Environment variable template
8. **.gitignore** - Git ignore patterns

### Database Schema

```
projects (id, name, location_coords, total_area_sqm, created_at, updated_at)
    ↓ (1-to-many)
layouts (id, project_id, config_json, layout_json, total_modules, capacity_kwp, gcr_ratio, created_at)
    ↓ (1-to-many)
boq_items (id, layout_id, category, item_name, quantity, unit, rate, amount)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `sqlalchemy>=2.0.0` - ORM framework
- `psycopg2-binary>=2.9.0` - PostgreSQL adapter
- `alembic>=1.11.0` - Database migrations
- `python-dotenv>=1.0.0` - Environment management
- `pytest>=7.4.0` - Testing framework

### 2. Configure Database

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql # macOS

# Create database and user
sudo -u postgres psql
postgres=# CREATE DATABASE pvlayout;
postgres=# CREATE USER pvuser WITH PASSWORD 'pvpass';
postgres=# GRANT ALL PRIVILEGES ON DATABASE pvlayout TO pvuser;
postgres=# \q

# Set environment variable
export DATABASE_URL="postgresql://pvuser:pvpass@localhost:5432/pvlayout"
```

#### Option B: Railway PostgreSQL

Railway automatically provides a PostgreSQL database:

1. Add PostgreSQL plugin to your Railway project
2. Railway sets `DATABASE_URL` automatically
3. No additional configuration needed

### 3. Initialize Database

```bash
# Run the demo script to initialize tables
python tests/demo_database.py
```

Or in Python:

```python
from src.components.database import initialize_database
initialize_database()
```

## 🧪 Testing

### Run All Tests

```bash
# Set test database URL
export DATABASE_URL="postgresql://pvuser:pvpass@localhost:5432/pvlayout"

# Run test suite
pytest tests/test_database.py -v

# Run with coverage
pytest tests/test_database.py -v --cov=src.components.database --cov-report=html
```

### Test Coverage

The test suite includes:
- ✅ Database initialization (2 tests)
- ✅ Project CRUD operations (9 tests)
- ✅ Cascading deletes (2 tests)
- ✅ Module-level functions (4 tests)
- ✅ Data integrity (3 tests)

**Total: 20 test cases**

### Run Demo Script

```bash
python tests/demo_database.py
```

This will:
1. Initialize database tables
2. Create a test project with layouts and BoQ items
3. Load the project
4. List all projects
5. Delete the test project
6. Verify all operations succeeded

## 💻 Usage Examples

### Save a Complete Project

```python
from src.components.database import save_project

project_data = {
    'name': 'Gujarat Solar Plant - 5MW',
    'location_coords': {
        'lat': 23.0225,
        'lng': 72.5714,
        'address': 'Ahmedabad, Gujarat'
    },
    'total_area_sqm': 50000.0,
    'layouts': [
        {
            'config_json': {
                'module_width': 1.0,
                'module_height': 2.0,
                'tilt_angle': 20,
                'azimuth': 180,
                'row_spacing': 5.0
            },
            'layout_json': {
                'rows': 25,
                'modules_per_row': 20,
                'total_strings': 100,
                'inverters': 5
            },
            'total_modules': 10000,
            'capacity_kwp': 5000.0,
            'gcr_ratio': 0.35,
            'boq_items': [
                {
                    'category': 'Modules',
                    'item_name': 'Bifacial Solar Module 500W',
                    'quantity': 10000,
                    'unit': 'Nos',
                    'rate': 15000.0,
                    'amount': 150000000.0
                },
                {
                    'category': 'Structure',
                    'item_name': 'Galvanized Mounting Structure',
                    'quantity': 500,
                    'unit': 'Sets',
                    'rate': 50000.0,
                    'amount': 25000000.0
                },
                {
                    'category': 'Inverters',
                    'item_name': 'String Inverter 1000kW',
                    'quantity': 5,
                    'unit': 'Nos',
                    'rate': 5000000.0,
                    'amount': 25000000.0
                }
            ]
        }
    ]
}

project_id = save_project(project_data)
print(f"Project saved: {project_id}")
```

### Load and Analyze Project

```python
from src.components.database import load_project

project = load_project(project_id)

print(f"Project: {project['name']}")
print(f"Location: {project['location_coords']}")
print(f"Site Area: {project['total_area_sqm']} sqm")
print(f"\nLayouts: {len(project['layouts'])}")

for i, layout in enumerate(project['layouts'], 1):
    print(f"\nLayout {i}:")
    print(f"  Modules: {layout['total_modules']}")
    print(f"  Capacity: {layout['capacity_kwp']} kWp")
    print(f"  GCR: {layout['gcr_ratio']}")
    print(f"  BoQ Items: {len(layout['boq_items'])}")
    
    total_cost = sum(item['amount'] for item in layout['boq_items'] if item['amount'])
    print(f"  Total Cost: ₹{total_cost:,.2f}")
```

### List All Projects

```python
from src.components.database import list_projects

projects = list_projects()

print(f"Total Projects: {len(projects)}\n")

for project in projects:
    print(f"{project['name']}")
    print(f"  ID: {project['id']}")
    print(f"  Area: {project['total_area_sqm']} sqm")
    print(f"  Layouts: {project['layout_count']}")
    print(f"  Created: {project['created_at']}")
    print(f"  Updated: {project['updated_at']}")
    print()
```

### Update Existing Project

```python
from src.components.database import save_project, load_project

# Load existing project
project = load_project(project_id)

# Update fields
project['name'] = 'Gujarat Solar Plant - 5MW (Updated)'
project['total_area_sqm'] = 55000.0

# Save changes
save_project(project)
```

### Delete Project

```python
from src.components.database import delete_project

success = delete_project(project_id)
if success:
    print("Project deleted successfully")
else:
    print("Project not found")
```

## 🔒 Security Features

### SQL Injection Prevention

✅ **All queries use parameterized statements via SQLAlchemy ORM**
- No raw SQL strings with user input
- Type-safe model definitions
- Automatic escaping of special characters

### Connection Security

✅ **Production-ready connection pooling**
- QueuePool with configurable pool size
- Pre-ping to detect stale connections
- Automatic connection recycling
- Timeout handling

### Session Management

✅ **Automatic session cleanup**
- Context managers ensure proper closure
- Rollback on errors
- No connection leaks

### Environment-based Configuration

✅ **No hardcoded credentials**
- DATABASE_URL from environment variables
- Support for .env files with python-dotenv
- Railway automatic configuration

## 🔧 Integration with Other Sessions

### SESSION-05 Integration (Layout Engine)

When the layout engine generates a layout, save it to the database:

```python
from src.components.database import save_project

def save_generated_layout(layout_data, project_info):
    """Save layout generated by SESSION-05"""
    project_data = {
        'name': project_info['project_name'],
        'location_coords': project_info['coordinates'],
        'total_area_sqm': project_info['site_area'],
        'layouts': [
            {
                'config_json': layout_data['configuration'],
                'layout_json': layout_data['geometry'],
                'total_modules': layout_data['module_count'],
                'capacity_kwp': layout_data['capacity'],
                'gcr_ratio': layout_data['gcr'],
            }
        ]
    }
    
    return save_project(project_data)
```

### SESSION-10 Integration (Export/Reporting)

Load saved projects for export:

```python
from src.components.database import load_project, list_projects

def export_project_to_excel(project_id):
    """Export project loaded from database"""
    project = load_project(project_id)
    
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    # Use project data for Excel/PDF export
    # ... export logic ...
    
    return export_path
```

## 🚢 Railway Deployment

### Automatic Setup

Railway automatically:
1. Provisions PostgreSQL database
2. Sets `DATABASE_URL` environment variable
3. Manages backups and scaling

### First Deployment

On first deployment, initialize tables:

```python
# In your main app startup (e.g., src/app.py)
from src.components.database import initialize_database

# Initialize tables on startup
initialize_database()
```

### Monitoring

Check Railway dashboard for:
- Connection count
- Query performance
- Storage usage
- Backup status

## 📊 Database Migrations (Optional)

For production deployments with schema changes:

```bash
# Initialize Alembic (one-time)
alembic init alembic

# Configure alembic.ini with DATABASE_URL
# Edit alembic/env.py to import your models

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# For future schema changes
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

## 🐛 Troubleshooting

### Connection Refused

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
- Verify PostgreSQL is running: `sudo service postgresql status`
- Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Verify firewall allows port 5432

### Authentication Failed

```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solution:**
- Verify username and password in DATABASE_URL
- Check PostgreSQL pg_hba.conf for authentication method
- Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE pvlayout TO pvuser`

### Module Import Error

```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### SSL Required (Railway)

If Railway requires SSL:

```python
# Update DATABASE_URL
DATABASE_URL += "?sslmode=require"
```

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] Database and user created
- [ ] DATABASE_URL environment variable set
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`initialize_database()`)
- [ ] Tests passing (`pytest tests/test_database.py -v`)
- [ ] Demo script working (`python tests/demo_database.py`)
- [ ] Can create, read, update, delete projects
- [ ] Cascading deletes working
- [ ] JSON fields storing/loading correctly
- [ ] Timestamps being set automatically

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Railway PostgreSQL Guide](https://docs.railway.app/databases/postgresql)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

## 🎯 Next Steps

1. **SESSION-05 Integration**: Use database to save generated layouts
2. **SESSION-10 Integration**: Load projects for export/reporting
3. **Production Deployment**: Deploy to Railway with PostgreSQL
4. **Schema Migrations**: Set up Alembic for future schema changes
5. **Performance Optimization**: Add indexes for common queries
6. **Backup Strategy**: Configure automated backups in Railway

---

**Implementation Status: ✅ COMPLETE**

All sacred principles followed:
- ✅ Syntax validation before commit (`python -m py_compile`)
- ✅ Comprehensive test suite (20 test cases)
- ✅ Production-ready code with error handling
- ✅ Security best practices (no SQL injection)
- ✅ Documentation and examples
- ✅ Railway-ready configuration
