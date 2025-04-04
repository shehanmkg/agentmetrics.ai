"""Base database model for the KPI Analytics System."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative

@as_declarative()
class Base:
    """Base class for all database models."""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Helper methods will be added as needed 