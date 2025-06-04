# In app/models/tables.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, NUMERIC, TIMESTAMP, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server-side default timestamps
from app.db.connector import Base # Import Base from your connector

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    kpi_data = relationship("KpiData", back_populates="team")

class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    kpi_data = relationship("KpiData", back_populates="region")

class KpiDefinition(Base):
    __tablename__ = "kpi_definitions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    unit = Column(String(50))
    category = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    kpi_data = relationship("KpiData", back_populates="kpi_definition")

class KpiData(Base):
    __tablename__ = "kpi_data"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kpi_id = Column(Integer, ForeignKey("kpi_definitions.id"))
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True) # Assuming team can be optional
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True) # Assuming region can be optional
    value = Column(NUMERIC, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    week = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    kpi_definition = relationship("KpiDefinition", back_populates="kpi_data")
    team = relationship("Team", back_populates="kpi_data")
    region = relationship("Region", back_populates="kpi_data")

    __table_args__ = (
        Index("idx_kpi_data_kpi_id", "kpi_id"),
        Index("idx_kpi_data_team_id", "team_id"),
        Index("idx_kpi_data_region_id", "region_id"),
        Index("idx_kpi_data_time", "year", "quarter", "month"),
    )

# Other models like Anomalies, QueryHistory can be added if needed by agents
# For now, focusing on the core KPI-related tables.