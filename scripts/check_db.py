#!/usr/bin/env python3
"""
Database connection check script.

This script tests the connection to the PostgreSQL database
and provides information about the existing tables.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.connector import db_connector
from app.config import settings

def main():
    """Main function."""
    print(f"Testing connection to PostgreSQL database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}, Port: {settings.DB_PORT}")
    
    # Test the connection
    if db_connector.test_connection():
        print("✅ Connection successful!")
        
        # Check if important tables exist
        tables = ["teams", "regions", "kpi_definitions", "kpi_data", "anomalies", "query_history"]
        for table in tables:
            try:
                count = db_connector.count_records(table)
                print(f"✅ Table '{table}' exists with {count} records")
            except Exception:
                print(f"❌ Table '{table}' does not exist or cannot be accessed")
        
        return 0
    else:
        print("❌ Connection failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 