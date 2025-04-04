#!/usr/bin/env python3
"""
Database setup script for KPI Analytics System.

This script:
1. Tests the connection to PostgreSQL
2. Creates the database if it doesn't exist
3. Creates all the tables
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, inspect

from app.config import settings
from app.models.base import Base
from app.models.tables import Team, Region, KPIDefinition, KPIData, Anomaly, QueryHistory

def test_connection():
    """Test the connection to PostgreSQL."""
    print(f"Testing connection to PostgreSQL at {settings.DB_HOST}:{settings.DB_PORT}...")
    
    try:
        # Connect using psycopg2 to test basic connectivity
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        conn.close()
        print("Connection successful!")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def setup_database():
    """Create the database if it doesn't exist."""
    # Create a URL for checking if the database exists
    db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    print(f"Checking if database '{settings.DB_NAME}' exists...")
    
    if not database_exists(db_url):
        print(f"Database '{settings.DB_NAME}' does not exist. Creating...")
        try:
            create_database(db_url)
            print(f"Database '{settings.DB_NAME}' created successfully!")
        except Exception as e:
            print(f"Failed to create database: {e}")
            return False
    else:
        print(f"Database '{settings.DB_NAME}' already exists.")
    
    return True

def create_tables():
    """Create all tables in the database."""
    from sqlalchemy import create_engine
    
    print("Creating tables...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully!")
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {', '.join(tables)}")
        
        return True
    except Exception as e:
        print(f"Failed to create tables: {e}")
        return False

def main():
    """Main function."""
    print("Setting up database for KPI Analytics System...\n")
    
    if not test_connection():
        print("Cannot proceed without a connection to PostgreSQL.")
        return 1
    
    if not setup_database():
        print("Database setup failed.")
        return 1
    
    if not create_tables():
        print("Table creation failed.")
        return 1
    
    print("\nDatabase setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 