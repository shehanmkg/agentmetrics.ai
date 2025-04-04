# KPI Analytics System Database Schema

## Overview
The database schema is designed to store KPI metrics, organizational structure, and historical data for analysis. We're using PostgreSQL as the database engine.

## Tables

### teams
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### regions
```sql
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### kpi_definitions
```sql
CREATE TABLE kpi_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(50),
    category VARCHAR(100), -- e.g., 'sales', 'marketing', 'operations'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### kpi_data
```sql
CREATE TABLE kpi_data (
    id SERIAL PRIMARY KEY,
    kpi_id INTEGER REFERENCES kpi_definitions(id),
    team_id INTEGER REFERENCES teams(id),
    region_id INTEGER REFERENCES regions(id),
    value NUMERIC NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL, -- 1, 2, 3, 4
    month INTEGER NOT NULL, -- 1-12
    week INTEGER, -- 1-52
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Indexes for fast querying
    INDEX idx_kpi_data_kpi_id (kpi_id),
    INDEX idx_kpi_data_team_id (team_id),
    INDEX idx_kpi_data_region_id (region_id),
    INDEX idx_kpi_data_time (year, quarter, month)
);
```

### anomalies
```sql
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    kpi_data_id INTEGER REFERENCES kpi_data(id),
    description TEXT,
    severity VARCHAR(20), -- 'low', 'medium', 'high'
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### query_history
```sql
CREATE TABLE query_history (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    successful BOOLEAN DEFAULT TRUE
);
```

## Sample Data Insertion

### Sample Teams
```sql
INSERT INTO teams (name, department) VALUES
('Ecommerce', 'Sales'),
('Social Media', 'Marketing'),
('Customer Support', 'Operations');
```

### Sample Regions
```sql
INSERT INTO regions (name, country) VALUES
('North America', 'USA'),
('APAC', 'Singapore'),
('EMEA', 'Germany');
```

### Sample KPI Definitions
```sql
INSERT INTO kpi_definitions (name, description, unit, category) VALUES
('sales_conversion_rate', 'Percentage of visitors who complete a purchase', '%', 'sales'),
('customer_acquisition_cost', 'Average cost to acquire a new customer', 'USD', 'marketing'),
('support_response_time', 'Average time to first response for support tickets', 'minutes', 'operations');
``` 