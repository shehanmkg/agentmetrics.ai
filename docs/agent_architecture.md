# KPI Analytics System Agent Architecture

## Overview
The system uses a multi-agent architecture powered by PydanticAI to process natural language queries about KPIs, retrieve and analyze the relevant data, generate insights, and produce visualizations when needed.

## Agent Pipeline

```
User Query → Query Interpreter → Data Analysis → Insight Generator → [Visualization] → Response
```

## Agent Definitions

### Query Interpreter Agent

**Purpose**: Understand natural language queries and translate them into structured data retrievals.

**Inputs**:
- Raw query text from user

**Outputs**:
- Structured query parameters:
  - KPI type(s)
  - Time period(s)
  - Team/region filters
  - Comparison requests
  - Visualization needs

**Tools**:
- NLP parsing
- Entity extraction
- PostgreSQL querying

### Data Analysis Agent

**Purpose**: Analyze the retrieved data using statistical methods to identify trends, forecast values, and detect anomalies.

**Inputs**:
- Raw KPI data from database
- Analysis parameters from Query Interpreter

**Outputs**:
- Statistical analysis results
- Forecast predictions
- Trend indicators
- Detected anomalies

**Tools**:
- Time series analysis
- Statistical comparisons
- Forecasting models
- Anomaly detection

### Insight Generator Agent

**Purpose**: Convert analysis results into human-readable insights and recommendations.

**Inputs**:
- Analysis results from Data Analysis Agent
- Original query context

**Outputs**:
- Textual insights
- Prioritized findings
- Risk assessments
- Actionable recommendations

**Tools**:
- Natural language generation
- Context-aware templating
- Risk evaluation

### Visualization Agent (Optional)

**Purpose**: Create visual representations of the analysis when requested or beneficial.

**Inputs**:
- Analysis results
- Insight highlights
- Visualization parameters

**Outputs**:
- Chart/graph data
- Visualization type recommendations
- Visual anomaly highlighting

**Tools**:
- Chart generation
- Visualization type selection

## PydanticAI Implementation

Each agent will be implemented using PydanticAI models:

```python
from pydanticai import Agent, Tool

class QueryInterpreterAgent(Agent):
    """Agent for interpreting user queries"""
    
    class Config:
        tools = [
            Tool(name="parse_query"),
            Tool(name="extract_entities"),
            Tool(name="retrieve_data")
        ]

class DataAnalysisAgent(Agent):
    """Agent for analyzing KPI data"""
    
    class Config:
        tools = [
            Tool(name="analyze_time_series"),
            Tool(name="compare_periods"),
            Tool(name="detect_anomalies"),
            Tool(name="forecast_values")
        ]

class InsightGeneratorAgent(Agent):
    """Agent for generating insights from analysis"""
    
    class Config:
        tools = [
            Tool(name="generate_narrative"),
            Tool(name="prioritize_findings"),
            Tool(name="identify_risks")
        ]

class VisualizationAgent(Agent):
    """Agent for creating visualizations"""
    
    class Config:
        tools = [
            Tool(name="create_chart"),
            Tool(name="select_visualization_type")
        ]
```

## Agent Communication

Agents will communicate through structured Pydantic models passed between them, ensuring type safety and consistency throughout the pipeline. 