-- PostgreSQL Schema for PV Layout Designer
-- Session 09: Database Integration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location_coords JSON,
    total_area_sqm FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Layouts table
CREATE TABLE IF NOT EXISTS layouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    config_json TEXT,
    layout_json TEXT,
    total_modules INT,
    capacity_kwp FLOAT,
    gcr_ratio FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill of Quantities (BoQ) items table
CREATE TABLE IF NOT EXISTS boq_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    layout_id UUID NOT NULL REFERENCES layouts(id) ON DELETE CASCADE,
    category VARCHAR(50),
    item_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(20),
    rate FLOAT,
    amount FLOAT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_layouts_project_id ON layouts(project_id);
CREATE INDEX IF NOT EXISTS idx_boq_items_layout_id ON boq_items(layout_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
