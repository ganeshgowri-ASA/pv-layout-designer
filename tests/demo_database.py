#!/usr/bin/env python3
"""
Database Integration Example
Demonstrates usage of the PostgreSQL database module

Note: Requires DATABASE_URL environment variable to be set
Example: export DATABASE_URL="postgresql://user:pass@localhost:5432/pvlayout"
"""

import os
import sys
from datetime import datetime

# Check if DATABASE_URL is set
if not os.getenv('DATABASE_URL'):
    print("⚠️  DATABASE_URL environment variable not set")
    print("   Set it with: export DATABASE_URL='postgresql://user:pass@host:port/database'")
    print("\n   For this demo, we'll show the API usage without connecting to a database\n")
    DEMO_MODE = True
else:
    DEMO_MODE = False

def demo_api_usage():
    """Demonstrate the database API"""
    
    print("=" * 70)
    print("PV Layout Designer - Database Module Demo")
    print("=" * 70)
    
    if DEMO_MODE:
        print("\n📚 API Usage Examples:\n")
        
        print("1. Initialize Database:")
        print("   >>> from src.components.database import initialize_database")
        print("   >>> initialize_database()")
        print("   >>> # Creates all tables in PostgreSQL\n")
        
        print("2. Save a Project:")
        print("   >>> from src.components.database import save_project")
        print("   >>> project_data = {")
        print("   ...     'name': 'Gujarat Solar Plant',")
        print("   ...     'location_coords': {'lat': 23.0225, 'lng': 72.5714},")
        print("   ...     'total_area_sqm': 50000.0,")
        print("   ...     'layouts': [{")
        print("   ...         'config_json': {'module_width': 1.0, 'module_height': 2.0},")
        print("   ...         'total_modules': 200,")
        print("   ...         'capacity_kwp': 100.0,")
        print("   ...         'gcr_ratio': 0.35,")
        print("   ...     }]")
        print("   ... }")
        print("   >>> project_id = save_project(project_data)")
        print("   >>> print(f'Saved project: {project_id}')\n")
        
        print("3. Load a Project:")
        print("   >>> from src.components.database import load_project")
        print("   >>> project = load_project(project_id)")
        print("   >>> print(project['name'])")
        print("   >>> 'Gujarat Solar Plant'\n")
        
        print("4. List All Projects:")
        print("   >>> from src.components.database import list_projects")
        print("   >>> projects = list_projects()")
        print("   >>> for p in projects:")
        print("   ...     print(f\"{p['name']} - {p['layout_count']} layouts\")\n")
        
        print("5. Delete a Project:")
        print("   >>> from src.components.database import delete_project")
        print("   >>> success = delete_project(project_id)")
        print("   >>> if success:")
        print("   ...     print('Project deleted successfully')\n")
        
        print("=" * 70)
        print("Database Module Features:")
        print("=" * 70)
        print("✓ SQLAlchemy ORM with declarative models")
        print("✓ Connection pooling for production")
        print("✓ Automatic session management")
        print("✓ Cascading deletes for data integrity")
        print("✓ JSON field support for flexible storage")
        print("✓ UUID primary keys")
        print("✓ Automatic timestamp tracking")
        print("✓ Comprehensive error handling")
        print("✓ Module-level convenience functions")
        print("=" * 70)
    
    else:
        print("\n✓ DATABASE_URL is set, attempting to connect...\n")
        
        try:
            from src.components.database import (
                initialize_database,
                save_project,
                load_project,
                list_projects,
                delete_project,
            )
            
            # Initialize database
            print("1. Initializing database...")
            success = initialize_database()
            if success:
                print("   ✓ Database initialized successfully\n")
            else:
                print("   ✗ Failed to initialize database\n")
                return
            
            # Create a test project
            print("2. Creating a test project...")
            project_data = {
                'name': f'Test Project {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'location_coords': {'lat': 23.0225, 'lng': 72.5714},
                'total_area_sqm': 50000.0,
                'layouts': [
                    {
                        'config_json': {
                            'module_width': 1.0,
                            'module_height': 2.0,
                            'tilt_angle': 20,
                        },
                        'layout_json': {
                            'rows': 10,
                            'modules_per_row': 20,
                        },
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
            print(f"   ✓ Project created with ID: {project_id}\n")
            
            # Load the project
            print("3. Loading the project...")
            loaded_project = load_project(project_id)
            if loaded_project:
                print(f"   ✓ Project loaded: {loaded_project['name']}")
                print(f"   ✓ Layouts: {len(loaded_project['layouts'])}")
                if loaded_project['layouts']:
                    print(f"   ✓ Modules: {loaded_project['layouts'][0]['total_modules']}")
                    print(f"   ✓ BoQ Items: {len(loaded_project['layouts'][0]['boq_items'])}\n")
            
            # List all projects
            print("4. Listing all projects...")
            projects = list_projects()
            print(f"   ✓ Found {len(projects)} project(s)")
            for p in projects[:5]:  # Show first 5
                print(f"     - {p['name']} ({p['layout_count']} layouts)")
            print()
            
            # Delete the test project
            print("5. Deleting test project...")
            success = delete_project(project_id)
            if success:
                print(f"   ✓ Project {project_id} deleted successfully\n")
            
            print("=" * 70)
            print("✓ All database operations completed successfully!")
            print("=" * 70)
            
        except ImportError as e:
            print(f"✗ Failed to import database module: {e}")
            print("  Make sure requirements are installed: pip install -r requirements.txt")
        except Exception as e:
            print(f"✗ Database error: {e}")
            print(f"  Error type: {type(e).__name__}")


if __name__ == '__main__':
    demo_api_usage()
