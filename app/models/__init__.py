# in app/models/__init__.py
from .tables import Team, Region, KpiDefinition, KpiData
# Import other models as they are created

__all__ = [
    "Team",
    "Region",
    "KpiDefinition",
    "KpiData",
]