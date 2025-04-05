#!/usr/bin/env python3
"""
Apply migrations to the KPI Analytics System database.

This script runs Alembic to apply all pending migrations.
"""
import sys
import os
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    """Apply all pending migrations."""
    print("Applying database migrations...")
    
    try:
        # Run alembic upgrade command
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True
        )
        print("✅ Migrations applied successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to apply migrations: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 