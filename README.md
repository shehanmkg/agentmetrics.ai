# KPI Analytics System

A multi-agent system for analyzing KPI data and generating insights using natural language queries.

## Features

- Query KPI data using natural language
- Analyze trends and patterns in KPI performance
- Generate insights and identify risks
- Visualize data when needed

## Tech Stack

- FastAPI for the API framework
- PydanticAI for agent implementation
- PostgreSQL for data storage
- SQLAlchemy for ORM

## Project Structure

```
kpi-analytics/
├── app/
│   ├── agents/          # PydanticAI agent implementations
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic models
│   ├── config.py        # Configuration
│   └── database.py      # Database connection
├── docs/                # Documentation
├── .env                 # Environment variables
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` file:
   ```
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=kpi_analytics
   OPENAI_API_KEY=your_openai_api_key
   API_KEY=your_development_api_key
   ```
5. Create the database:
   ```
   createdb kpi_analytics  # Using PostgreSQL command line
   ```

### Running the Application

```
uvicorn main:app --reload
```

The API will be available at http://localhost:8000. API documentation is available at http://localhost:8000/docs.

## Usage

Send natural language queries to the API:

```bash
curl -X POST "http://localhost:8000/api/v1/queries/" \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_development_api_key" \
  -d '{"query": "Predict Q3 2024 sales conversion rates for the ecommerce team"}'
``` 