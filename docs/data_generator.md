# KPI Test Data Generator

## Overview
This document outlines the approach for generating realistic test data for the KPI Analytics System. The test data will simulate various business KPIs across different teams, regions, and time periods.

## Data Requirements

- **Time Range**: At least 2 years of historical data with quarterly, monthly, and weekly granularity
- **KPIs**: Multiple KPI types across different business functions
- **Patterns**: Realistic trends, seasonality, and occasional anomalies
- **Volume**: Sufficient volume to test system performance without being excessive

## Generation Approach

### 1. Base Pattern Generation

For each KPI, we'll generate base patterns that follow realistic business trends:

```python
def generate_base_pattern(kpi_type, start_date, end_date, frequency='D'):
    """Generate a base pattern for a specific KPI"""
    date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)
    data = []
    
    if kpi_type == 'sales_conversion_rate':
        # Generate with seasonal patterns and slight upward trend
        base = np.linspace(0.12, 0.16, len(date_range))  # Slight improvement over time
        seasonal = 0.03 * np.sin(np.linspace(0, 12*np.pi, len(date_range)))  # Seasonal pattern
        noise = np.random.normal(0, 0.01, len(date_range))  # Random variations
        values = base + seasonal + noise
        values = np.clip(values, 0.05, 0.30)  # Keep within realistic bounds
    
    elif kpi_type == 'customer_acquisition_cost':
        # Generate with quarterly budget cycles and gradual efficiency
        base = np.linspace(80, 65, len(date_range))  # Improving efficiency
        seasonal = 15 * np.sin(np.linspace(0, 8*np.pi, len(date_range)))  # Budget cycles
        noise = np.random.normal(0, 5, len(date_range))  # Random variations
        values = base + seasonal + noise
        values = np.clip(values, 40, 120)  # Keep within realistic bounds
    
    # Add more KPI types as needed
    
    for i, date in enumerate(date_range):
        data.append({
            'date': date,
            'value': float(values[i])
        })
    
    return pd.DataFrame(data)
```

### 2. Region and Team Variations

Apply multipliers and pattern shifts for different regions and teams:

```python
def apply_regional_variation(base_df, region):
    """Apply regional variations to the base pattern"""
    df = base_df.copy()
    
    if region == 'North America':
        df['value'] = df['value'] * 1.2  # Higher values
    elif region == 'APAC':
        df['value'] = df['value'] * 0.9  # Lower values with higher growth
        # Add growth trend
        growth = np.linspace(1.0, 1.15, len(df))
        df['value'] = df['value'] * growth
    elif region == 'EMEA':
        df['value'] = df['value'] * 1.1  # Moderate values
        # Add different seasonality
        df['value'] = df['value'] + 0.02 * np.cos(np.linspace(0, 12*np.pi, len(df)))
    
    return df
```

### 3. Anomaly Injection

Add occasional anomalies to make the data more realistic:

```python
def inject_anomalies(df, anomaly_rate=0.05):
    """Inject random anomalies into the data"""
    anomaly_count = int(len(df) * anomaly_rate)
    anomaly_indices = np.random.choice(len(df), anomaly_count, replace=False)
    
    for idx in anomaly_indices:
        # 50% chance of positive anomaly, 50% chance of negative
        if np.random.random() > 0.5:
            df.loc[idx, 'value'] = df.loc[idx, 'value'] * np.random.uniform(1.3, 2.0)
        else:
            df.loc[idx, 'value'] = df.loc[idx, 'value'] * np.random.uniform(0.4, 0.7)
    
    return df
```

### 4. Data Transformation and Loading

Transform the generated dataframes into database records:

```python
def transform_to_db_records(df, kpi_id, team_id, region_id):
    """Transform dataframe to database records"""
    records = []
    
    for _, row in df.iterrows():
        date = row['date']
        records.append({
            'kpi_id': kpi_id,
            'team_id': team_id,
            'region_id': region_id,
            'value': row['value'],
            'timestamp': date,
            'year': date.year,
            'quarter': (date.month - 1) // 3 + 1,
            'month': date.month,
            'week': date.isocalendar()[1]
        })
    
    return records
```

## Sample Data Generation Script

A simplified version of the complete data generation process:

```python
def generate_all_test_data(db_connection):
    """Generate all test data and load into database"""
    # Date range for 2 years of history
    start_date = '2022-01-01'
    end_date = '2024-03-31'
    
    # Get reference IDs
    kpi_ids = {'sales_conversion_rate': 1, 'customer_acquisition_cost': 2, 'support_response_time': 3}
    team_ids = {'Ecommerce': 1, 'Social Media': 2, 'Customer Support': 3}
    region_ids = {'North America': 1, 'APAC': 2, 'EMEA': 3}
    
    # Generate and load data for each combination
    for kpi_name, kpi_id in kpi_ids.items():
        base_df = generate_base_pattern(kpi_name, start_date, end_date)
        
        for team_name, team_id in team_ids.items():
            if not is_valid_kpi_for_team(kpi_name, team_name):
                continue
                
            for region_name, region_id in region_ids.items():
                # Apply variations
                region_df = apply_regional_variation(base_df, region_name)
                team_df = apply_team_variation(region_df, team_name)
                final_df = inject_anomalies(team_df)
                
                # Transform to records
                records = transform_to_db_records(final_df, kpi_id, team_id, region_id)
                
                # Insert into database
                insert_records(db_connection, 'kpi_data', records)
                
    print(f"Successfully generated test data from {start_date} to {end_date}")
```

## Generated Data Characteristics

The generated test data will have the following characteristics:

1. **Realistic Trends**: Overall patterns that mimic real business metrics
2. **Seasonality**: Cyclical patterns appropriate for each KPI type
3. **Regional Variations**: Different performance across regions
4. **Team-Specific Patterns**: Variations based on team function
5. **Anomalies**: Occasional outliers that the system should detect
6. **Time Granularity**: Daily data that can be aggregated to weekly, monthly, quarterly 