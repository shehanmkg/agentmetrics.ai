Here's what each agent should do. Query interpreter Agent should be able to understand the query and it should be able to get all the relevant data based on the query from the db.
Then those retrieved data should pass to the Data Analysis agent. It will analyse those data using those given tools. Then those analysed data will pass to the insight generator agent, it should be able to interpret those results to a meaningful and understandable way to the user and the final agent, the Visualization agent, it should be able to visualize those results if needed (This agent only uses when needed to illustrate the results in a graph or chart like that). So this is the flow I have planned to fulfil using this system.

Sample Admin Prompt
    "Predict Q3 2024 sales conversion rates for the ecommerce team, compare them to Q2 performance, and flag potential risks. Include a breakdown by region and visualize anomalies."

Example Output
    The admin receives this report in Next.js and a mobile alert:

Prediction:
    Q3 2024 sales conversion rate: 18.5% (±2.1% confidence interval).

Comparison:
    +3.2% improvement vs. Q2 2024.

Risks:
    North America region shows a 12% drop in weeks 3–4 of August (low inventory flagged).
    APAC region exceeds forecast by 8% (overly optimistic model adjustment needed).

Visualization:
    Line chart comparing Q2 vs. Q3.
    Heatmap of regional anomalies.

Edge Case Handling
    Ambiguous Prompt:
        If the admin writes "Check sales trends," the agent responds:
        "Which team, timeframe, and KPI would you like to analyze? Example: 'ecommerce sales_conversion_rate for Q3 2024.'"

Missing Data:
    If Database lacks historical data, the agent replies:
        "Insufficient data for Q3 predictions"

Context-Aware Predictions:
    Example: When an admin asks, “Why did sales drop last quarter?”, the AI uses your Postgre KPI data (not just generic knowledge) to explain.
    Example: If you add new KPIs (e.g., "social media engagement"), RAG lets the AI immediately use this data in predictions.

Handling Complex Queries:
    Example: “Compare North America’s Q3 sales to APAC’s Q2 and flag risks.”
        RAG retrieves region-specific data and generates a comparison.