#!/usr/bin/env python3
"""
Seed the KPI Analytics System database with initial data.

This script inserts sample data into the database for testing.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.db.connector import db_connector
from app.models import Team, Region, KPIDefinition, KPIData, Anomaly

def seed_teams(session: Session) -> None:
    """Seed the teams table with initial data."""
    teams = [
        {"name": "Ecommerce", "department": "Sales"},
        {"name": "Social Media", "department": "Marketing"},
        {"name": "Customer Support", "department": "Operations"}
    ]
    
    for team_data in teams:
        team = Team(**team_data)
        session.add(team)
    
    session.commit()
    print(f"✅ Added {len(teams)} teams")


def seed_regions(session: Session) -> None:
    """Seed the regions table with initial data."""
    regions = [
        {"name": "North America", "country": "USA"},
        {"name": "APAC", "country": "Singapore"},
        {"name": "EMEA", "country": "Germany"}
    ]
    
    for region_data in regions:
        region = Region(**region_data)
        session.add(region)
    
    session.commit()
    print(f"✅ Added {len(regions)} regions")


def seed_kpi_definitions(session: Session) -> None:
    """Seed the KPI definitions table with initial data."""
    kpis = [
        {
            "name": "sales_conversion_rate",
            "description": "Percentage of visitors who complete a purchase",
            "unit": "%",
            "category": "sales"
        },
        {
            "name": "customer_acquisition_cost",
            "description": "Average cost to acquire a new customer",
            "unit": "USD",
            "category": "marketing"
        },
        {
            "name": "support_response_time",
            "description": "Average time to first response for support tickets",
            "unit": "minutes",
            "category": "operations"
        }
    ]
    
    for kpi_data in kpis:
        kpi = KPIDefinition(**kpi_data)
        session.add(kpi)
    
    session.commit()
    print(f"✅ Added {len(kpis)} KPI definitions")


def seed_sample_kpi_data(session: Session) -> None:
    """Seed a small amount of sample KPI data."""
    # Get reference IDs
    teams = {team.name: team.id for team in session.query(Team).all()}
    regions = {region.name: region.id for region in session.query(Region).all()}
    kpis = {kpi.name: kpi.id for kpi in session.query(KPIDefinition).all()}
    
    # Create some sample data points
    today = datetime.now()
    
    # Just add a few data points as examples
    data_points = [
        # Sales conversion rate
        {
            "kpi_id": kpis["sales_conversion_rate"],
            "team_id": teams["Ecommerce"],
            "region_id": regions["North America"],
            "value": 0.15,  # 15%
            "timestamp": today - timedelta(days=1),
            "year": today.year,
            "quarter": (today.month - 1) // 3 + 1,
            "month": today.month,
            "week": today.isocalendar()[1]
        },
        {
            "kpi_id": kpis["sales_conversion_rate"],
            "team_id": teams["Ecommerce"],
            "region_id": regions["APAC"],
            "value": 0.12,  # 12%
            "timestamp": today - timedelta(days=1),
            "year": today.year,
            "quarter": (today.month - 1) // 3 + 1,
            "month": today.month,
            "week": today.isocalendar()[1]
        },
        # Customer acquisition cost
        {
            "kpi_id": kpis["customer_acquisition_cost"],
            "team_id": teams["Social Media"],
            "region_id": regions["North America"],
            "value": 75.50,  # $75.50
            "timestamp": today - timedelta(days=1),
            "year": today.year,
            "quarter": (today.month - 1) // 3 + 1,
            "month": today.month,
            "week": today.isocalendar()[1]
        },
        # Support response time
        {
            "kpi_id": kpis["support_response_time"],
            "team_id": teams["Customer Support"],
            "region_id": regions["EMEA"],
            "value": 12.3,  # 12.3 minutes
            "timestamp": today - timedelta(days=1),
            "year": today.year,
            "quarter": (today.month - 1) // 3 + 1,
            "month": today.month,
            "week": today.isocalendar()[1]
        }
    ]
    
    for data in data_points:
        kpi_data = KPIData(**data)
        session.add(kpi_data)
    
    session.commit()
    print(f"✅ Added {len(data_points)} sample KPI data points")


def main():
    """Seed the database with initial data."""
    print("Seeding database with initial data...")
    
    try:
        with db_connector.get_session() as session:
            # Check if database is empty
            team_count = session.query(Team).count()
            if team_count > 0:
                print("Database already contains data. Skipping seed operation.")
                return 0
            
            seed_teams(session)
            seed_regions(session)
            seed_kpi_definitions(session)
            seed_sample_kpi_data(session)
            
            print("✅ Database seeded successfully!")
            return 0
    except Exception as e:
        print(f"❌ Failed to seed database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 