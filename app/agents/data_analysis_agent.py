# In app/agents/data_analysis_agent.py
from pydanticai import Agent, Tool # Assuming PydanticAI is still the base
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pandas as pd # Import pandas for easier data manipulation

# Input will be InterpreterOutput.fetched_data and potentially structured_query.table for context
# For simplicity, we'll primarily use the fetched_data.
# The actual structure of fetched_data items will be dictionaries matching the SELECT query.
# e.g., {"KpiData_value": 123, "KpiDefinition_name": "sales_conversion_rate", ...}
# The keys might be prefixed by table names by SQLAlchemy's _asdict() if multiple tables have same column names.
# We need to be mindful of actual key names. Let's assume simple key names for now,
# or that the QueryInterpreterAgent standardizes them.
# For this subtask, we'll assume keys like 'value', 'name', 'category', 'team_name', 'region_name'.

class DataAnalysisInput(BaseModel): # Kept for clarity, though not strictly enforced on dict list
    # table_name: str # We might not get table_name directly if data is already joined
    # For now, let's assume the agent infers or works generally on the provided data.
    # If table_name is needed for specific logic, it should be passed from the orchestration.
    # Let's assume the orchestrator (API endpoint) will pass the original table name if needed.
    query_context: str # e.g. "sales_data" or "marketing_campaigns" from interpreter.structured_query.table
    data: List[Dict[str, Any]] = Field(..., description="Data fetched from the database")

class AnalysisResult(BaseModel): # From previous step, ensure it's consistent
    analyzed_context: str # Replaces analyzed_table to be more generic
    record_count: int
    summary_statistics: Dict[str, Any] = Field(default_factory=dict, description="Basic statistics like sum, mean, median, mode if applicable")
    trends_identified: List[str] = Field(default_factory=list, description="Identified trends in the data (still mock/simple)")
    anomalies_detected: List[str] = Field(default_factory=list, description="Detected anomalies or outliers (still mock/simple)")
    # forecast: Optional[str] = Field(None, description="A simple forecast if applicable (still mock/simple)") # Removing forecast for now to simplify

class DataAnalysisAgent(Agent): # Assuming PydanticAI structure
    class Config:
        tools = [Tool(name="analyze_data_real")]
        enable_default_tools = False
        arbitrary_types_allowed = True # If pandas Series/DataFrames are used internally and parts returned

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tools["analyze_data_real"] = self._analyze_real_data

    def _analyze_real_data(self, analysis_input: DataAnalysisInput) -> AnalysisResult:
        """
        Performs basic real data analysis (sum, average, count) on the fetched data.
        Trends and anomalies are still placeholder/simple.
        """
        stats = {}
        trends = []
        anomalies = []

        record_count = len(analysis_input.data)

        if not analysis_input.data:
            return AnalysisResult(
                analyzed_context=analysis_input.query_context,
                record_count=0,
                summary_statistics={"message": "No data provided for analysis."},
                trends_identified=["No data to identify trends."],
                anomalies_detected=[]
            )

        # Use pandas DataFrame for easier computation
        df = pd.DataFrame(analysis_input.data)

        # Attempt to find a primary numeric 'value' column.
        # Common key for KPI values from KpiData table is 'value'.
        # The actual key from joined query might be 'KpiData_value' or similar if not aliased.
        # For this example, let's search for common patterns or assume a primary value column.

        # Try to identify the main value column (e.g., KpiData.value)
        # The actual column names will depend on the SELECT statement in QueryInterpreter
        # For now, let's assume the QueryInterpreter aliases KpiData.value to 'kpi_value'
        # or that we can find it.

        # Let's assume the primary numeric column is named 'value' as in KpiData.value
        # This needs to be robust if column names vary (e.g. KpiData_value)
        value_col_name = None
        if 'value' in df.columns and pd.api.types.is_numeric_dtype(df['value']):
            value_col_name = 'value'
        elif 'KpiData_value' in df.columns and pd.api.types.is_numeric_dtype(df['KpiData_value']): # A common pattern from joined queries
            value_col_name = 'KpiData_value'
        # Add more checks or expect a specific alias from QueryInterpreterAgent

        if value_col_name:
            numeric_values = pd.to_numeric(df[value_col_name], errors='coerce').dropna()
            if not numeric_values.empty:
                stats[f'sum_of_{value_col_name}'] = round(numeric_values.sum(), 2)
                stats[f'mean_of_{value_col_name}'] = round(numeric_values.mean(), 2)
                stats[f'median_of_{value_col_name}'] = round(numeric_values.median(), 2)
                stats[f'min_of_{value_col_name}'] = round(numeric_values.min(), 2)
                stats[f'max_of_{value_col_name}'] = round(numeric_values.max(), 2)
                stats[f'std_dev_of_{value_col_name}'] = round(numeric_values.std(), 2)

                # Simple trend/anomaly placeholders based on real data
                if numeric_values.mean() > 1000: # Arbitrary threshold for example
                    trends.append(f"Average {value_col_name.replace('_', ' ')} is high, indicating strong performance.")
                if numeric_values.max() > numeric_values.mean() * 3 and numeric_values.std() > numeric_values.mean() : # Arbitrary check for anomaly
                    anomalies.append(f"Potential anomaly: Max {value_col_name.replace('_', ' ')} is significantly higher than average.")
            else:
                stats['numeric_column_info'] = f"Column '{value_col_name}' found but contained no valid numeric data."
        else:
            stats['numeric_column_info'] = "No primary numeric 'value' column identified for detailed statistics."
            trends.append("Could not perform detailed trend analysis without a clear numeric KPI value column.")


        # Generic count if 'name' or 'KpiDefinition_name' column exists (e.g. for distinct KPIs)
        name_col = None
        if 'KpiDefinition_name' in df.columns:
            name_col = 'KpiDefinition_name'
        elif 'name' in df.columns: # Generic name
            name_col = 'name'

        if name_col:
            stats[f'distinct_{name_col}_count'] = df[name_col].nunique()


        if not trends: trends.append("Basic analysis performed; further context needed for detailed trends.")
        if not anomalies and value_col_name and not numeric_values.empty: # only if we had data to check
            anomalies.append("No obvious anomalies detected with simple checks.")


        return AnalysisResult(
            analyzed_context=analysis_input.query_context,
            record_count=record_count,
            summary_statistics=stats,
            trends_identified=trends,
            anomalies_detected=anomalies
        )

    async def run(self, query_context: str, data: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Runs the data analysis agent with real data.
        'query_context' could be the primary table name or a description of the query.
        """
        input_data = DataAnalysisInput(query_context=query_context, data=data)
        return self._analyze_real_data(input_data)

# Update app/agents/__init__.py if AnalysisResult or DataAnalysisInput changed significantly.
# from .data_analysis_agent import DataAnalysisAgent, AnalysisResult, DataAnalysisInput # (DataAnalysisInput might be internal)
