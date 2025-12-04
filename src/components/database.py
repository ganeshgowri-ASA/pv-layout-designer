"""
Database Manager for PV Layout Designer
Session 09: PostgreSQL Integration with SQLAlchemy ORM

Provides CRUD operations for project persistence with connection pooling
and error handling for production deployment.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from contextlib import contextmanager
from uuid import UUID, uuid4

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import NullPool, QueuePool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()


# ================== ORM Models ==================

class Project(Base):
    """Project model representing a PV plant project"""
    __tablename__ = 'projects'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    location_coords = Column(JSON)
    total_area_sqm = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    layouts = relationship("Layout", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert project to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'location_coords': self.location_coords,
            'total_area_sqm': self.total_area_sqm,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Layout(Base):
    """Layout model representing a generated PV layout"""
    __tablename__ = 'layouts'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    config_json = Column(Text)
    layout_json = Column(Text)
    total_modules = Column(Integer)
    capacity_kwp = Column(Float)
    gcr_ratio = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="layouts")
    boq_items = relationship("BoQItem", back_populates="layout", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert layout to dictionary"""
        return {
            'id': str(self.id),
            'project_id': str(self.project_id),
            'config_json': json.loads(self.config_json) if self.config_json else None,
            'layout_json': json.loads(self.layout_json) if self.layout_json else None,
            'total_modules': self.total_modules,
            'capacity_kwp': self.capacity_kwp,
            'gcr_ratio': self.gcr_ratio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BoQItem(Base):
    """Bill of Quantities item model"""
    __tablename__ = 'boq_items'
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    layout_id = Column(PG_UUID(as_uuid=True), ForeignKey('layouts.id', ondelete='CASCADE'), nullable=False)
    category = Column(String(50))
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit = Column(String(20))
    rate = Column(Float)
    amount = Column(Float)
    
    # Relationships
    layout = relationship("Layout", back_populates="boq_items")
    
    def to_dict(self) -> Dict:
        """Convert BoQ item to dictionary"""
        return {
            'id': str(self.id),
            'layout_id': str(self.layout_id),
            'category': self.category,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'rate': self.rate,
            'amount': self.amount,
        }


# ================== Database Manager ==================

class DatabaseManager:
    """
    Database manager with connection pooling and session management
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: PostgreSQL connection URL (defaults to DATABASE_URL env var)
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create engine with connection pooling for production
        # Use QueuePool for production, NullPool for testing
        poolclass = QueuePool if 'localhost' not in self.database_url else NullPool
        
        self.engine = create_engine(
            self.database_url,
            poolclass=poolclass,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL debugging
        )
        
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("Database manager initialized successfully")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        
        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def initialize_database(self) -> bool:
        """
        Create all database tables
        
        Returns:
            True if successful, False otherwise
        """
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False
    
    def save_project(self, project_data: Dict) -> str:
        """
        Save or update a project with its layouts and BoQ items
        
        Args:
            project_data: Dictionary containing project information
                {
                    'name': str,
                    'location_coords': dict,
                    'total_area_sqm': float,
                    'layouts': [
                        {
                            'config_json': dict,
                            'layout_json': dict,
                            'total_modules': int,
                            'capacity_kwp': float,
                            'gcr_ratio': float,
                            'boq_items': [
                                {
                                    'category': str,
                                    'item_name': str,
                                    'quantity': int,
                                    'unit': str,
                                    'rate': float,
                                    'amount': float
                                }
                            ]
                        }
                    ]
                }
        
        Returns:
            Project UUID as string
        """
        try:
            with self.get_session() as session:
                # Check if project already exists (by id if provided)
                project_id = project_data.get('id')
                if project_id:
                    project = session.query(Project).filter_by(id=project_id).first()
                    if project:
                        # Update existing project
                        project.name = project_data.get('name', project.name)
                        project.location_coords = project_data.get('location_coords', project.location_coords)
                        project.total_area_sqm = project_data.get('total_area_sqm', project.total_area_sqm)
                        project.updated_at = datetime.now(timezone.utc)
                        
                        # If layouts are provided in update, clear existing layouts
                        # This ensures clean state when updating with new layout data
                        if 'layouts' in project_data:
                            # Delete existing layouts (cascades to BoQ items)
                            session.query(Layout).filter_by(project_id=project.id).delete()
                            session.flush()
                    else:
                        # Create new project with specified ID
                        project = Project(
                            id=project_id,
                            name=project_data['name'],
                            location_coords=project_data.get('location_coords'),
                            total_area_sqm=project_data.get('total_area_sqm'),
                        )
                        session.add(project)
                else:
                    # Create new project
                    project = Project(
                        name=project_data['name'],
                        location_coords=project_data.get('location_coords'),
                        total_area_sqm=project_data.get('total_area_sqm'),
                    )
                    session.add(project)
                
                # Add layouts if provided
                if 'layouts' in project_data:
                    for layout_data in project_data['layouts']:
                        layout = Layout(
                            project_id=project.id,
                            config_json=json.dumps(layout_data.get('config_json')) if layout_data.get('config_json') else None,
                            layout_json=json.dumps(layout_data.get('layout_json')) if layout_data.get('layout_json') else None,
                            total_modules=layout_data.get('total_modules'),
                            capacity_kwp=layout_data.get('capacity_kwp'),
                            gcr_ratio=layout_data.get('gcr_ratio'),
                        )
                        session.add(layout)
                        session.flush()  # Get layout.id for BoQ items
                        
                        # Add BoQ items if provided
                        if 'boq_items' in layout_data:
                            for boq_data in layout_data['boq_items']:
                                boq_item = BoQItem(
                                    layout_id=layout.id,
                                    category=boq_data.get('category'),
                                    item_name=boq_data['item_name'],
                                    quantity=boq_data['quantity'],
                                    unit=boq_data.get('unit'),
                                    rate=boq_data.get('rate'),
                                    amount=boq_data.get('amount'),
                                )
                                session.add(boq_item)
                
                session.flush()
                project_id = str(project.id)
                logger.info(f"Project saved successfully: {project_id}")
                return project_id
                
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            raise
    
    def load_project(self, project_id: str) -> Optional[Dict]:
        """
        Load a project with all its layouts and BoQ items
        
        Args:
            project_id: Project UUID as string
        
        Returns:
            Dictionary containing complete project data or None if not found
        """
        try:
            with self.get_session() as session:
                project = session.query(Project).filter_by(id=UUID(project_id)).first()
                
                if not project:
                    logger.warning(f"Project not found: {project_id}")
                    return None
                
                # Build complete project data
                project_dict = project.to_dict()
                project_dict['layouts'] = []
                
                for layout in project.layouts:
                    layout_dict = layout.to_dict()
                    layout_dict['boq_items'] = [item.to_dict() for item in layout.boq_items]
                    project_dict['layouts'].append(layout_dict)
                
                logger.info(f"Project loaded successfully: {project_id}")
                return project_dict
                
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            raise
    
    def list_projects(self) -> List[Dict]:
        """
        List all projects (without full layout data)
        
        Returns:
            List of project dictionaries
        """
        try:
            with self.get_session() as session:
                projects = session.query(Project).order_by(Project.created_at.desc()).all()
                project_list = []
                
                for project in projects:
                    project_dict = project.to_dict()
                    # Add layout count
                    project_dict['layout_count'] = len(project.layouts)
                    project_list.append(project_dict)
                
                logger.info(f"Listed {len(project_list)} projects")
                return project_list
                
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all associated data (cascading delete)
        
        Args:
            project_id: Project UUID as string
        
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            with self.get_session() as session:
                project = session.query(Project).filter_by(id=UUID(project_id)).first()
                
                if not project:
                    logger.warning(f"Project not found for deletion: {project_id}")
                    return False
                
                session.delete(project)
                logger.info(f"Project deleted successfully: {project_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            raise


# ================== Module-level Functions ==================

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get or create the global database manager instance
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def initialize_database() -> bool:
    """
    Initialize database tables
    
    Returns:
        True if successful
    """
    db_manager = get_db_manager()
    return db_manager.initialize_database()


def save_project(project_data: Dict) -> str:
    """
    Save a project
    
    Args:
        project_data: Project data dictionary
    
    Returns:
        Project UUID
    """
    db_manager = get_db_manager()
    return db_manager.save_project(project_data)


def load_project(project_id: str) -> Optional[Dict]:
    """
    Load a project by ID
    
    Args:
        project_id: Project UUID
    
    Returns:
        Project data dictionary or None
    """
    db_manager = get_db_manager()
    return db_manager.load_project(project_id)


def list_projects() -> List[Dict]:
    """
    List all projects
    
    Returns:
        List of project dictionaries
    """
    db_manager = get_db_manager()
    return db_manager.list_projects()


def delete_project(project_id: str) -> bool:
    """
    Delete a project
    
    Args:
        project_id: Project UUID
    
    Returns:
        True if deleted successfully
    """
    db_manager = get_db_manager()
    return db_manager.delete_project(project_id)
