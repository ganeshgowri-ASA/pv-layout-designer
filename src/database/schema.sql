-- PV Layout Designer Database Schema
-- This schema will be implemented in Session 8

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    site_coordinates TEXT,  -- JSON string of polygon coordinates
    site_area_sqm REAL,
    center_lat REAL,
    center_lon REAL
);

-- Layouts table
CREATE TABLE IF NOT EXISTS layouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config TEXT,  -- JSON string of configuration
    panel_count INTEGER,
    total_capacity_kw REAL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Panels table
CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    layout_id INTEGER NOT NULL,
    position_x REAL,
    position_y REAL,
    rotation REAL,
    module_type TEXT,
    FOREIGN KEY (layout_id) REFERENCES layouts(id)
);
