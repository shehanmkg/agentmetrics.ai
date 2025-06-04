# In app/db/mock_db_connector.py
from typing import List, Dict, Any
# Import StructuredQuery from the agent file to avoid circular dependency if it were defined in db
# For simplicity here, we assume direct use or it's defined in a shared schema location.
# To make this runnable, let's assume StructuredQuery is accessible.
# from app.agents.query_interpreter import StructuredQuery # This would be a circular import if not careful

# A better approach would be for StructuredQuery to be in a shared schemas directory.
# For now, let's redefine it or assume it's passed as a dict if QueryInterpreterAgent is the only user.
# For this subtask, we'll assume the agent passes the necessary components of StructuredQuery.

MOCK_SALES_DATA = [
    {"date": "2023-04-01", "product_id": "P101", "revenue": 1500, "units_sold": 10},
    {"date": "2023-04-05", "product_id": "P202", "revenue": 2500, "units_sold": 5},
    {"date": "2023-06-10", "product_id": "P101", "revenue": 1800, "units_sold": 12},
]

MOCK_MARKETING_DATA = [
    {"campaign_id": "C001", "spend": 5000, "roi": 2.5, "start_date": "2023-01-01"},
    {"campaign_id": "C002", "spend": 7500, "roi": 1.8, "start_date": "2023-04-15"},
]

# The agent will pass an object that has 'table' and 'filters' attributes.
def mock_fetch_data(query: Any) -> List[Dict[str, Any]]: # query is of type StructuredQuery
    """
    Mock function to fetch data based on a structured query object.
    The query object must have 'table' and 'filters' attributes.
    """
    if query.table == "sales_data":
        if query.filters and query.filters.get("quarter") == "Q2":
             # Simplified filter: assume MOCK_SALES_DATA is Q2 if filter is Q2
            return MOCK_SALES_DATA
        return MOCK_SALES_DATA # Return all if no Q2 filter
    elif query.table == "marketing_campaigns":
        return MOCK_MARKETING_DATA
    return []
