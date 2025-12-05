"""
Test Suite for Database Manager
Session 09: PostgreSQL Integration

Tests CRUD operations, connection handling, and data persistence
"""

import os
import pytest
import json
from datetime import datetime
from uuid import uuid4

# Set test database URL before importing database module
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'postgresql://test:test@localhost:5432/test_pvlayout')

from src.components.database import (
    DatabaseManager,
    Project,
    Layout,
    BoQItem,
    initialize_database,
    save_project,
    load_project,
    list_projects,
    delete_project,
    Base,
)


@pytest.fixture(scope='session')
def db_manager():
    """Create database manager for testing"""
    manager = DatabaseManager()
    # Create tables
    Base.metadata.create_all(manager.engine)
    yield manager
    # Cleanup after all tests
    Base.metadata.drop_all(manager.engine)


@pytest.fixture(scope='function')
def clean_db(db_manager):
    """Clean database before each test"""
    with db_manager.get_session() as session:
        session.query(BoQItem).delete()
        session.query(Layout).delete()
        session.query(Project).delete()
    yield db_manager


class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_initialize_database(self, db_manager):
        """Test database table creation"""
        result = db_manager.initialize_database()
        assert result is True
    
    def test_database_url_required(self):
        """Test that DATABASE_URL is required"""
        original_url = os.environ.get('DATABASE_URL')
        if original_url:
            del os.environ['DATABASE_URL']
        
        with pytest.raises(ValueError, match="DATABASE_URL"):
            DatabaseManager()
        
        # Restore original URL
        if original_url:
            os.environ['DATABASE_URL'] = original_url


class TestProjectCRUD:
    """Test Project CRUD operations"""
    
    def test_create_simple_project(self, clean_db):
        """Test creating a simple project"""
        project_data = {
            'name': 'Test Solar Plant',
            'location_coords': {'lat': 23.0225, 'lng': 72.5714},
            'total_area_sqm': 10000.0,
        }
        
        project_id = clean_db.save_project(project_data)
        assert project_id is not None
        assert len(project_id) == 36  # UUID format
    
    def test_create_project_with_layouts(self, clean_db):
        """Test creating a project with layouts"""
        project_data = {
            'name': 'Complex Solar Plant',
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
                }
            ]
        }
        
        project_id = clean_db.save_project(project_data)
        assert project_id is not None
        
        # Verify project was saved
        loaded_project = clean_db.load_project(project_id)
        assert loaded_project is not None
        assert loaded_project['name'] == 'Complex Solar Plant'
        assert len(loaded_project['layouts']) == 1
        assert loaded_project['layouts'][0]['total_modules'] == 200
    
    def test_create_project_with_boq_items(self, clean_db):
        """Test creating a project with BoQ items"""
        project_data = {
            'name': 'Plant with BoQ',
            'location_coords': {'lat': 23.0225, 'lng': 72.5714},
            'total_area_sqm': 25000.0,
            'layouts': [
                {
                    'config_json': {'module_type': 'bifacial'},
                    'layout_json': {'rows': 5},
                    'total_modules': 100,
                    'capacity_kwp': 50.0,
                    'gcr_ratio': 0.30,
                    'boq_items': [
                        {
                            'category': 'Modules',
                            'item_name': 'Solar Module 500W',
                            'quantity': 100,
                            'unit': 'Nos',
                            'rate': 15000.0,
                            'amount': 1500000.0,
                        },
                        {
                            'category': 'Structure',
                            'item_name': 'Mounting Structure',
                            'quantity': 10,
                            'unit': 'Sets',
                            'rate': 50000.0,
                            'amount': 500000.0,
                        }
                    ]
                }
            ]
        }
        
        project_id = clean_db.save_project(project_data)
        loaded_project = clean_db.load_project(project_id)
        
        assert loaded_project is not None
        assert len(loaded_project['layouts']) == 1
        assert len(loaded_project['layouts'][0]['boq_items']) == 2
        assert loaded_project['layouts'][0]['boq_items'][0]['item_name'] == 'Solar Module 500W'
    
    def test_load_project(self, clean_db):
        """Test loading a project by ID"""
        # Create project
        project_data = {
            'name': 'Load Test Project',
            'location_coords': {'lat': 20.0, 'lng': 75.0},
            'total_area_sqm': 15000.0,
        }
        project_id = clean_db.save_project(project_data)
        
        # Load project
        loaded = clean_db.load_project(project_id)
        assert loaded is not None
        assert loaded['name'] == 'Load Test Project'
        assert loaded['location_coords'] == {'lat': 20.0, 'lng': 75.0}
        assert loaded['total_area_sqm'] == 15000.0
    
    def test_load_nonexistent_project(self, clean_db):
        """Test loading a project that doesn't exist"""
        fake_id = str(uuid4())
        result = clean_db.load_project(fake_id)
        assert result is None
    
    def test_list_projects(self, clean_db):
        """Test listing all projects"""
        # Create multiple projects
        for i in range(3):
            project_data = {
                'name': f'Project {i+1}',
                'location_coords': {'lat': 23.0 + i, 'lng': 72.0 + i},
                'total_area_sqm': 10000.0 * (i + 1),
            }
            clean_db.save_project(project_data)
        
        # List projects
        projects = clean_db.list_projects()
        assert len(projects) == 3
        assert all('name' in p for p in projects)
        assert all('layout_count' in p for p in projects)
    
    def test_delete_project(self, clean_db):
        """Test deleting a project"""
        # Create project
        project_data = {
            'name': 'Delete Test Project',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        project_id = clean_db.save_project(project_data)
        
        # Verify it exists
        loaded = clean_db.load_project(project_id)
        assert loaded is not None
        
        # Delete project
        result = clean_db.delete_project(project_id)
        assert result is True
        
        # Verify it's gone
        loaded = clean_db.load_project(project_id)
        assert loaded is None
    
    def test_delete_nonexistent_project(self, clean_db):
        """Test deleting a project that doesn't exist"""
        fake_id = str(uuid4())
        result = clean_db.delete_project(fake_id)
        assert result is False
    
    def test_update_existing_project(self, clean_db):
        """Test updating an existing project"""
        # Create project
        project_data = {
            'name': 'Original Name',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        project_id = clean_db.save_project(project_data)
        
        # Update project
        update_data = {
            'id': project_id,
            'name': 'Updated Name',
            'location_coords': {'lat': 24.0, 'lng': 73.0},
            'total_area_sqm': 15000.0,
        }
        updated_id = clean_db.save_project(update_data)
        
        # Verify update
        assert updated_id == project_id
        loaded = clean_db.load_project(project_id)
        assert loaded['name'] == 'Updated Name'
        assert loaded['total_area_sqm'] == 15000.0
    
    def test_update_project_replaces_layouts(self, clean_db):
        """Test that updating a project with new layouts replaces old ones"""
        # Create project with layouts
        project_data = {
            'name': 'Layout Update Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
            'layouts': [
                {
                    'total_modules': 100,
                    'capacity_kwp': 50.0,
                    'gcr_ratio': 0.30,
                }
            ]
        }
        project_id = clean_db.save_project(project_data)
        
        # Verify initial layout
        loaded = clean_db.load_project(project_id)
        assert len(loaded['layouts']) == 1
        assert loaded['layouts'][0]['total_modules'] == 100
        
        # Update with new layouts
        update_data = {
            'id': project_id,
            'name': 'Layout Update Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
            'layouts': [
                {
                    'total_modules': 200,
                    'capacity_kwp': 100.0,
                    'gcr_ratio': 0.35,
                },
                {
                    'total_modules': 150,
                    'capacity_kwp': 75.0,
                    'gcr_ratio': 0.32,
                }
            ]
        }
        clean_db.save_project(update_data)
        
        # Verify layouts were replaced
        loaded = clean_db.load_project(project_id)
        assert len(loaded['layouts']) == 2
        assert loaded['layouts'][0]['total_modules'] == 200
        assert loaded['layouts'][1]['total_modules'] == 150


class TestCascadingDelete:
    """Test cascading delete behavior"""
    
    def test_delete_project_cascades_to_layouts(self, clean_db):
        """Test that deleting a project also deletes its layouts"""
        project_data = {
            'name': 'Cascade Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
            'layouts': [
                {
                    'total_modules': 100,
                    'capacity_kwp': 50.0,
                    'gcr_ratio': 0.30,
                }
            ]
        }
        
        project_id = clean_db.save_project(project_data)
        
        # Verify layout exists
        with clean_db.get_session() as session:
            layout_count = session.query(Layout).filter(Layout.project_id == project_id).count()
            assert layout_count == 1
        
        # Delete project
        clean_db.delete_project(project_id)
        
        # Verify layout is also deleted
        with clean_db.get_session() as session:
            layout_count = session.query(Layout).filter(Layout.project_id == project_id).count()
            assert layout_count == 0
    
    def test_delete_layout_cascades_to_boq(self, clean_db):
        """Test that deleting a layout also deletes its BoQ items"""
        project_data = {
            'name': 'BoQ Cascade Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
            'layouts': [
                {
                    'total_modules': 100,
                    'capacity_kwp': 50.0,
                    'gcr_ratio': 0.30,
                    'boq_items': [
                        {
                            'item_name': 'Test Item',
                            'quantity': 10,
                            'unit': 'Nos',
                        }
                    ]
                }
            ]
        }
        
        project_id = clean_db.save_project(project_data)
        
        # Get layout ID
        loaded = clean_db.load_project(project_id)
        layout_id = loaded['layouts'][0]['id']
        
        # Verify BoQ item exists
        with clean_db.get_session() as session:
            boq_count = session.query(BoQItem).filter(BoQItem.layout_id == layout_id).count()
            assert boq_count == 1
        
        # Delete project (which cascades to layouts and BoQ)
        clean_db.delete_project(project_id)
        
        # Verify BoQ item is deleted
        with clean_db.get_session() as session:
            boq_count = session.query(BoQItem).filter(BoQItem.layout_id == layout_id).count()
            assert boq_count == 0


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""
    
    def test_module_initialize_database(self):
        """Test module-level initialize_database()"""
        result = initialize_database()
        assert result is True
    
    def test_module_save_and_load_project(self, clean_db):
        """Test module-level save_project() and load_project()"""
        project_data = {
            'name': 'Module Test Project',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        
        project_id = save_project(project_data)
        assert project_id is not None
        
        loaded = load_project(project_id)
        assert loaded is not None
        assert loaded['name'] == 'Module Test Project'
    
    def test_module_list_projects(self, clean_db):
        """Test module-level list_projects()"""
        # Create a project
        project_data = {
            'name': 'List Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        save_project(project_data)
        
        projects = list_projects()
        assert len(projects) >= 1
    
    def test_module_delete_project(self, clean_db):
        """Test module-level delete_project()"""
        project_data = {
            'name': 'Delete Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        
        project_id = save_project(project_data)
        result = delete_project(project_id)
        assert result is True


class TestDataIntegrity:
    """Test data integrity and validation"""
    
    def test_json_serialization_deserialization(self, clean_db):
        """Test that JSON fields are properly serialized and deserialized"""
        config = {
            'module_width': 1.0,
            'module_height': 2.0,
            'tilt_angle': 20,
            'nested': {'key': 'value'}
        }
        
        project_data = {
            'name': 'JSON Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
            'layouts': [
                {
                    'config_json': config,
                    'total_modules': 100,
                    'capacity_kwp': 50.0,
                    'gcr_ratio': 0.30,
                }
            ]
        }
        
        project_id = clean_db.save_project(project_data)
        loaded = clean_db.load_project(project_id)
        
        assert loaded['layouts'][0]['config_json'] == config
    
    def test_timestamps_are_set(self, clean_db):
        """Test that timestamps are automatically set"""
        project_data = {
            'name': 'Timestamp Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        
        project_id = clean_db.save_project(project_data)
        loaded = clean_db.load_project(project_id)
        
        assert loaded['created_at'] is not None
        assert loaded['updated_at'] is not None
    
    def test_uuid_generation(self, clean_db):
        """Test that UUIDs are properly generated"""
        project_data = {
            'name': 'UUID Test',
            'location_coords': {'lat': 23.0, 'lng': 72.0},
            'total_area_sqm': 10000.0,
        }
        
        project_id = clean_db.save_project(project_data)
        
        # UUID should be 36 characters (including hyphens)
        assert len(project_id) == 36
        assert project_id.count('-') == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
