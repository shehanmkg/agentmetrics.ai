"""Database table models for the KPI Analytics System."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.models.base import Base

class Team(Base):
    """Team model for organizational structure."""
    __tablename__ = "teams"
    
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    
    # Relationships
    kpi_data = relationship("KPIData", back_populates="team")


class Region(Base):
    """Region model for geographical segmentation."""
    __tablename__ = "regions"
    
    name = Column(String(100), nullable=False)
    country = Column(String(100))
    
    # Relationships
    kpi_data = relationship("KPIData", back_populates="region")


class KPIDefinition(Base):
    """KPI definition model."""
    __tablename__ = "kpi_definitions"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=True)
    unit = Column(String(50))
    category = Column(String(100))
    
    # Relationships
    kpi_data = relationship("KPIData", back_populates="kpi_definition")


class KPIData(Base):
    """KPI data model for storing metric values."""
    __tablename__ = "kpi_data"
    
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    week = Column(Integer, nullable=True)
    
    # Relationships
    kpi_definition = relationship("KPIDefinition", back_populates="kpi_data")
    team = relationship("Team", back_populates="kpi_data")
    region = relationship("Region", back_populates="kpi_data")
    anomalies = relationship("Anomaly", back_populates="kpi_data")
    
    # Indexes for faster queries
    __table_args__ = (
        Index("idx_kpi_data_kpi_id", kpi_id),
        Index("idx_kpi_data_team_id", team_id),
        Index("idx_kpi_data_region_id", region_id),
        Index("idx_kpi_data_time", year, quarter, month),
    )


class Anomaly(Base):
    """Anomaly model for tracking detected data anomalies."""
    __tablename__ = "anomalies"
    
    kpi_data_id = Column(Integer, ForeignKey("kpi_data.id"), nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high'
    
    # Relationships
    kpi_data = relationship("KPIData", back_populates="anomalies")


class QueryHistory(Base):
    """Query history model for tracking API usage."""
    __tablename__ = "query_history"
    
    query_text = Column(String, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    successful = Column(Integer, default=1)  # 1 for true, 0 for false 