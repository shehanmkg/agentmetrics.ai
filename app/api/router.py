from fastapi import APIRouter
from app.api.v1.endpoints import kpi_queries

api_router = APIRouter()

# Include all API v1 endpoints
api_router.include_router(
    kpi_queries.router, 
    prefix="/v1/queries", 
    tags=["queries"]
) 