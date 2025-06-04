# In app/agents/__init__.py
from .query_interpreter import QueryInterpreterAgent, InterpreterOutput, StructuredQuery
from .data_analysis_agent import DataAnalysisAgent, AnalysisResult # DataAnalysisInput is internal
from .insight_generator_agent import InsightGeneratorAgent, GeneratedInsight # GeneratedInsight has changed

__all__ = [
    "QueryInterpreterAgent",
    "InterpreterOutput",
    "StructuredQuery", # Export if QueryInterpreterAgent output includes it and it's used externally
    "DataAnalysisAgent",
    "AnalysisResult",
    "InsightGeneratorAgent",
    "GeneratedInsight"
]