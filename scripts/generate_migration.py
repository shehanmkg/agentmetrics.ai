#!/usr/bin/env python3
"""
Generate an initial migration for the KPI Analytics System database.

This script runs Alembic to generate an initial migration.
"""
import sys
import os
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    """Generate the initial migration."""
    print("Generating initial migration...")
    
    try:
        # Run alembic revision command
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            check=True
        )
        print("✅ Migration generated successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate migration: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 