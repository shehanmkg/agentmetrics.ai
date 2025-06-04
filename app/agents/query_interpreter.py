# In app/agents/query_interpreter.py
from pydanticai import Agent, Tool # Assuming PydanticAI is still the base
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Optional # Added Optional
from sentence_transformers import SentenceTransformer, util
import torch # sentence_transformers often requires torch

# SQLAlchemy imports for DB interaction
from sqlalchemy.orm import Session
from app.db.connector import get_db # To get a DB session, though agent tools are not typically designed for direct dependency injection like FastAPI endpoints
# For agent tool usage, we might need to pass a session or have the agent create one if it's a long-lived process.
# For simplicity in this subtask, we'll assume the agent's tool method can obtain a session.
# A better pattern would be to pass the session to the agent's run method if possible.

from app.models.tables import KpiData, KpiDefinition, Team, Region # Import models

# Define a schema representation for semantic search
# This is a simplified version. A more robust solution would generate this from SQLAlchemy metadata or a config file.
SCHEMA_DESCRIPTIONS = {
    "kpi_data.value": "The numerical value of the Key Performance Indicator.",
    "kpi_data.timestamp": "The date and time when the KPI was recorded.",
    "kpi_data.year": "The year of the KPI data.",
    "kpi_data.quarter": "The quarter of the KPI data (1 to 4).",
    "kpi_data.month": "The month of the KPI data (1 to 12).",
    "kpi_definitions.name": "The name or title of the Key Performance Indicator (e.g., 'sales_conversion_rate', 'customer_acquisition_cost').",
    "kpi_definitions.category": "The category of the KPI (e.g., 'sales', 'marketing', 'operations').",
    "teams.name": "The name of the team associated with the KPI data (e.g., 'Ecommerce team', 'Social Media team').",
    "regions.name": "The name of the region associated with the KPI data (e.g., 'North America', 'APAC')."
    # Add more descriptions for other relevant fields/tables
}

# Load a sentence transformer model
# Using a smaller, faster model for demonstration.
# Consider more powerful models for production.
MODEL_NAME = 'all-MiniLM-L6-v2'
try:
    EMBEDDING_MODEL = SentenceTransformer(MODEL_NAME)
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}. Make sure you have internet to download it the first time.")
    EMBEDDING_MODEL = None


class StructuredQuery(BaseModel): # Re-defining or ensuring it's available
    table: str = "kpi_data" # Default to kpi_data
    select_fields: List[Any] = Field(default_factory=list) # Changed to List[Any] for SQLAlchemy column objects
    join_on: List[Tuple[Any, Any]] = Field(default_factory=list) # e.g., (KpiData.kpi_id, KpiDefinition.id)
    filters: List[Tuple[Any, str, Any]] = Field(default_factory=list) # e.g., (KpiDefinition.name, '==', 'sales_conversion_rate')

    # A field to store the raw generated SQL for inspection if needed
    raw_sql_debug: Optional[str] = None


class InterpreterOutput(BaseModel): # From previous step, ensure it's consistent
    raw_query: str
    interpretation_summary: str
    structured_query_representation: Optional[StructuredQuery] = None # To store our new query model
    fetched_data: List[Dict[str, Any]]
    # error_message: Optional[str] = None # If something goes wrong


class QueryInterpreterAgent(Agent): # Assuming PydanticAI structure
    class Config:
        tools = [Tool(name="interpret_query_and_fetch_data_real")]
        enable_default_tools = False # Keep this if you don't want PydanticAI's default tools
        arbitrary_types_allowed = True # Added to allow SQLAlchemy column objects in StructuredQuery

    def __init__(self, db_session_factory=None, **kwargs): # db_session_factory to create sessions
        super().__init__(**kwargs)
        self._tools["interpret_query_and_fetch_data_real"] = self._interpret_and_fetch_real
        # It's better to pass a session factory or have the agent manage sessions if it's long-lived.
        # For a single call, the session could be passed to 'run'.
        # Here, using a simplified approach where the tool method gets a session.
        self.db_session_factory = db_session_factory if db_session_factory else get_db


    def _get_semantic_matches(self, query_embedding, threshold=0.3) -> List[str]:
        matched_schema_keys = []
        if EMBEDDING_MODEL is None:
            # Fallback or error if model isn't loaded
            print("Warning: Embedding model not loaded. Semantic search will not work.")
            return []

        schema_keys = list(SCHEMA_DESCRIPTIONS.keys())
        schema_phrases = [SCHEMA_DESCRIPTIONS[key] for key in schema_keys]

        # Embed all schema descriptions
        schema_embeddings = EMBEDDING_MODEL.encode(schema_phrases, convert_to_tensor=True)

        # Compute cosine similarities
        similarities = util.pytorch_cos_sim(query_embedding, schema_embeddings)

        # Find matches above threshold
        for i, key_phrase in enumerate(schema_phrases):
            if similarities[0][i] > threshold:
                matched_schema_keys.append(schema_keys[i])
        return matched_schema_keys

    def _build_sql_query(self, matched_keys: List[str], original_user_query: str) -> StructuredQuery:
        sq = StructuredQuery()

        # Determine fields to select and tables to join
        select_targets = []
        joins_to_make = set() # Using a set to avoid duplicate join conditions

        # Default selection if no specific fields are matched strongly for select
        # Always select KPI value and name by default if kpi_data or kpi_definitions are involved
        select_targets.extend([KpiData.timestamp, KpiData.value, KpiDefinition.name])
        joins_to_make.add((KpiData.kpi_id, KpiDefinition.id)) # Default join

        # Basic entity extraction from original_user_query for filter values (very naive)
        # Example: "sales conversion rate for Q2" -> value: "sales_conversion_rate", quarter_filter: "Q2"
        # This part needs significant improvement with proper NER or regex for actual values.

        for key in matched_keys:
            table_name, column_name = key.split('.')

            # Add to select list
            if table_name == "kpi_data":
                select_targets.append(getattr(KpiData, column_name))
            elif table_name == "kpi_definitions":
                select_targets.append(getattr(KpiDefinition, column_name))
                joins_to_make.add((KpiData.kpi_id, KpiDefinition.id))
            elif table_name == "teams":
                select_targets.append(getattr(Team, column_name)) # e.g., Team.name
                joins_to_make.add((KpiData.team_id, Team.id))
            elif table_name == "regions":
                select_targets.append(getattr(Region, column_name)) # e.g., Region.name
                joins_to_make.add((KpiData.region_id, Region.id))

        # Naive filter addition (example, can be expanded)
        # This is highly simplified. Real implementation needs robust entity extraction and mapping.
        if "sales conversion rate" in original_user_query.lower():
             sq.filters.append((KpiDefinition.name, "==", "sales_conversion_rate"))
        if "q2" in original_user_query.lower():
             sq.filters.append((KpiData.quarter, "==", 2))
        if "north america" in original_user_query.lower():
            sq.filters.append((Region.name, "==", "North America"))


        # Remove duplicate select targets (e.g. if KpiDefinition.name was added twice)
        # Using a dict to preserve order while removing duplicates
        unique_select_targets = list(dict.fromkeys(select_targets))
        sq.select_fields = unique_select_targets
        sq.join_on = list(joins_to_make)

        return sq

    def _execute_query(self, db: Session, structured_query: StructuredQuery) -> List[Dict[str, Any]]:
        query = db.query(*structured_query.select_fields)

        # Apply joins
        # Keep track of tables already joined to avoid re-joining on the same path
        joined_tables = {KpiData} # Start with the base table for kpi_data related queries

        for left_on, right_on in structured_query.join_on:
            left_table = left_on.parent.entity # Get the SQLAlchemy model class (e.g., KpiData)
            right_table = right_on.parent.entity

            # Join if one of the tables is already in query and the other is not, or if it's the first join
            if left_table in joined_tables and right_table not in joined_tables:
                query = query.join(right_table, left_on == right_on)
                joined_tables.add(right_table)
            elif right_table in joined_tables and left_table not in joined_tables:
                 query = query.join(left_table, left_on == right_on)
                 joined_tables.add(left_table)
            # This simple logic might need enhancement for more complex join paths

        # Apply filters
        for field, operator, value in structured_query.filters:
            if operator == "==":
                query = query.filter(field == value)
            # Add more operators as needed (e.g., '>', '<', 'like')

        # For debugging: print the raw SQL
        try:
            raw_sql = str(query.statement.compile(bind=db.get_bind(), compile_kwargs={"literal_binds": True}))
            structured_query.raw_sql_debug = raw_sql
            print(f"Generated SQL: {raw_sql}")
        except Exception as e:
            print(f"Error compiling SQL for debug: {e}")


        results = query.limit(100).all() # Limit results for now
        # Convert SQLAlchemy Row objects to dictionaries
        # Need to handle cases where results might not have _asdict (if not KeyedTuple)
        return [row._asdict() if hasattr(row, '_asdict') else dict(row) for row in results]


    def _interpret_and_fetch_real(self, user_query: str) -> InterpreterOutput:
        """
        Interprets user query using semantic search, builds SQL, executes it, and returns data.
        """
        summary = "Interpreting query using semantic search."
        fetched_data_list = []
        error_msg = None # Not used in return yet
        s_query_representation = None

        if EMBEDDING_MODEL is None:
            return InterpreterOutput(
                raw_query=user_query,
                interpretation_summary="Error: Embedding model not loaded. Cannot process query.",
                fetched_data=[],
                # error_message="Embedding model not available." # Field not in model
            )

        query_embedding = EMBEDDING_MODEL.encode(user_query, convert_to_tensor=True)
        matched_keys = self._get_semantic_matches(query_embedding)

        if not matched_keys:
            summary = "Could not confidently match query to known KPI data fields using semantic search."
        else:
            summary = f"Semantic search matched query to: {', '.join(matched_keys)}. Building SQL query."

        s_query_representation = self._build_sql_query(matched_keys, user_query)

        # Get DB session - this is a simplified way for a tool method
        db_gen = self.db_session_factory() # Call the factory to get a session generator
        db_session = next(db_gen)
        try:
            fetched_data_list = self._execute_query(db_session, s_query_representation)
            if not fetched_data_list and matched_keys: # If we expected data but got none
                summary += " Query executed, but no data returned. Check filters or data availability."
            elif fetched_data_list:
                summary += f" Successfully fetched {len(fetched_data_list)} records."

        except Exception as e:
            print(f"Error executing SQL query: {e}")
            # error_msg = f"Database query execution failed: {str(e)}" # Field not in model
            summary += f" Error during query execution: {e}"
        finally:
            try:
                next(db_gen) # To execute the finally block in get_db
            except StopIteration:
                pass # Expected


        return InterpreterOutput(
            raw_query=user_query,
            interpretation_summary=summary,
            structured_query_representation=s_query_representation,
            fetched_data=fetched_data_list,
            # error_message=error_msg # This field needs to be added to InterpreterOutput if desired
        )

    async def run(self, user_query: str) -> InterpreterOutput: # Keep PydanticAI's async structure
        # This wrapper is if PydanticAI expects an async tool.
        # The actual work is synchronous due to sentence_transformers and typical DB I/O.
        # For a truly async DB operation, you'd need an async DB driver and SQLAlchemy setup.
        return self._interpret_and_fetch_real(user_query)

# Update app/agents/__init__.py if InterpreterOutput changed significantly (e.g. removed error_message)
# from .query_interpreter import QueryInterpreterAgent, InterpreterOutput, StructuredQuery (if needed by other modules)
