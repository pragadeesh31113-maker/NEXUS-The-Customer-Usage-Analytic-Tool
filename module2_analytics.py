
"""
Module 2: Usage Analytics
- Aggregates detailed usage data from the unified UsageLog table.
- Computes advanced metrics for individual customers and the overall network.
- Prepares data for machine learning analysis and dashboard visualizations.
"""
from sqlalchemy import func, extract
import pandas as pd
from datetime import datetime, timedelta
from module1_data_db import Customer, UsageLog, mask_phone_number
def get_hourly_usage_distribution(session):
    """Calculates the total number of network events for each hour of the day."""
    query = session.query(
        extract('hour', UsageLog.timestamp).label('hour'),
        func.count(UsageLog.id).label('event_count')
    ).group_by('hour').order_by('hour')
    return pd.read_sql(query.statement, session.bind)

def get_customer_hourly_distribution(session, customer_id):
    """Calculates the total number of network events for each hour for a single customer."""
    query = session.query(
        extract('hour', UsageLog.timestamp).label('hour'),
        func.count(UsageLog.id).label('event_count')
    ).filter(UsageLog.customer_id == customer_id).group_by('hour').order_by('hour')
    return pd.read_sql(query.statement, session.bind)

def get_features_for_ml(session):
    """
    Performs in-depth Exploratory Data Analysis (EDA) and feature engineering
    to prepare a rich dataset for ML modeling.
    """
    customers_df = pd.read_sql(session.query(Customer.id, Customer.name).statement, session.bind)
    logs_df = pd.read_sql(session.query(UsageLog).statement, session.bind)

    if logs_df.empty or customers_df.empty:
        return pd.DataFrame()

    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
    
    # Calculate Recency, Frequency, and Monetary Value (RFM)
    snapshot_date = logs_df['timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = logs_df.groupby('customer_id').agg(
        Recency=('timestamp', lambda date: (snapshot_date - date.max()).days),
        Frequency=('timestamp', 'count'),
        MonetaryValue=('duration_seconds', 'sum')
    ).reset_index()

    # Add other valuable features
    usage_features = logs_df.groupby('customer_id').agg(
        TotalDataMB=('data_mb_used', 'sum'),
        TotalCalls=('record_type', lambda x: (x == 'call').sum()),
        TotalSMS=('record_type', lambda x: (x == 'sms').sum())
    ).reset_index()

    # Combine all features
    features_df = pd.merge(customers_df, rfm, left_on='id', right_on='customer_id', how='left')
    features_df = pd.merge(features_df, usage_features, on='customer_id', how='left')
    
    # Clean up and fill missing values
    features_df.drop('customer_id', axis=1, inplace=True)
    features_df.fillna(0, inplace=True)
    
    return features_df

def get_calendar_heatmap_data(session):
    """Prepares data for a calendar heatmap of network-wide activity."""
    query = session.query(
        func.date(UsageLog.timestamp).label('date'),
        func.count(UsageLog.id).label('total_events')
    ).group_by(func.date(UsageLog.timestamp))
    df = pd.read_sql(query.statement, session.bind)
    if df.empty: return pd.DataFrame()
    df['date'] = pd.to_datetime(df['date'])
    start_date, end_date = df['date'].min(), df['date'].max()
    all_days_index = pd.date_range(start=start_date, end=end_date, freq='D')
    df = df.set_index('date').reindex(all_days_index, fill_value=0)
    return df.reset_index().rename(columns={'index': 'date'})

def get_customer_analytics(session, customer_id):
    """Fetches comprehensive analytics for a single customer."""
    customer = session.query(Customer).filter_by(id=customer_id).first()
    if not customer:
        return None

    logs_df = pd.read_sql(
        session.query(UsageLog).filter(UsageLog.customer_id == customer_id).statement,
        session.bind
    )

    if logs_df.empty:
        return { "id": customer.id, "name": customer.name, "phone": mask_phone_number(customer.phone_number), "has_data": False }
        
    logs_df['duration_seconds'] = pd.to_numeric(logs_df['duration_seconds'], errors='coerce')

    total_calls = logs_df[logs_df['record_type'] == 'call'].shape[0]
    total_sms = logs_df[logs_df['record_type'] == 'sms'].shape[0]
    total_data_mb = logs_df['data_mb_used'].sum()
    total_call_duration_mins = logs_df['duration_seconds'].sum() / 60

    logs_df['hour'] = pd.to_datetime(logs_df['timestamp']).dt.hour
    peak_hour = logs_df['hour'].mode()[0] if not logs_df.empty else None

    return {
        "id": customer.id,
        "name": customer.name,
        "phone": mask_phone_number(customer.phone_number),
        "has_data": True,
        "total_calls": total_calls,
        "total_sms": total_sms,
        "total_data_mb": total_data_mb,
        "total_call_duration_mins": total_call_duration_mins,
        "peak_usage_hour": f"{int(peak_hour)}:00 - {int(peak_hour)+1}:00" if peak_hour is not None else "N/A",
    }

def get_network_analytics(session):
    """Fetches analytics for the entire network."""
    logs_df = pd.read_sql(session.query(UsageLog).statement, session.bind)
    if logs_df.empty:
        return { "total_customers": 0, "total_calls": 0, "total_sms": 0, "total_data_gb": 0 }

    total_customers = session.query(func.count(Customer.id)).scalar()
    total_calls = logs_df[logs_df['record_type'] == 'call'].shape[0]
    total_sms = logs_df[logs_df['record_type'] == 'sms'].shape[0]
    total_data_gb = logs_df['data_mb_used'].sum() / 1024

    return {
        "total_customers": total_customers,
        "total_calls": total_calls,
        "total_sms": total_sms,
        "total_data_gb": total_data_gb,
    }

def get_data_for_ml(session):
    """Prepares a feature-rich DataFrame for machine learning."""
    customers_df = pd.read_sql(session.query(Customer.id, Customer.name).statement, session.bind)
    logs_df = pd.read_sql(session.query(UsageLog).statement, session.bind)

    if logs_df.empty or customers_df.empty:
        return pd.DataFrame()

    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
    latest_date = logs_df['timestamp'].max()
    
    features = logs_df.groupby('customer_id').agg(
        total_calls=('record_type', lambda x: (x == 'call').sum()),
        total_sms=('record_type', lambda x: (x == 'sms').sum()),
        total_data_mb=('data_mb_used', 'sum'),
        avg_call_duration=('duration_seconds', 'mean'),
        recency_days=('timestamp', lambda x: (latest_date - x.max()).days)
    ).reset_index()

    df = pd.merge(customers_df, features, left_on='id', right_on='customer_id', how='left').fillna(0)
    return df

def get_customer_daily_trends(session, customer_id):
    """Aggregates a single customer's usage data by day for trend analysis."""
    query = session.query(UsageLog.timestamp, UsageLog.record_type, UsageLog.data_mb_used)\
                   .filter(UsageLog.customer_id == customer_id)

    logs_df = pd.read_sql(query.statement, session.bind)
    if logs_df.empty: return pd.DataFrame()

    logs_df['date'] = pd.to_datetime(logs_df['timestamp']).dt.date

    daily_summary = logs_df.groupby('date').agg(
        Calls=('record_type', lambda x: (x == 'call').sum()),
        SMS=('record_type', lambda x: (x == 'sms').sum()),
        Data_Usage_MB=('data_mb_used', 'sum')
    ).reset_index()

    daily_summary['Total_Events'] = daily_summary['Calls'] + daily_summary['SMS'] + (daily_summary['Data_Usage_MB'] > 0).astype(int)

    if not daily_summary.empty:
        min_date = daily_summary['date'].min()
        max_date = daily_summary['date'].max()
        all_days = pd.date_range(start=min_date, end=max_date, freq='D').date
        daily_summary = daily_summary.set_index('date').reindex(all_days, fill_value=0).reset_index()
        daily_summary = daily_summary.rename(columns={'index': 'date'})
    return daily_summary

def get_daily_network_trends(session, last_n_days=30):
    """Aggregates network-wide usage data by day for trend analysis."""
    start_date = datetime.now() - timedelta(days=last_n_days)
    
    query = session.query(UsageLog.timestamp, UsageLog.record_type, UsageLog.data_mb_used)\
                   .filter(UsageLog.timestamp >= start_date)
    
    logs_df = pd.read_sql(query.statement, session.bind)
    if logs_df.empty:
        return pd.DataFrame()

    logs_df['date'] = pd.to_datetime(logs_df['timestamp']).dt.date
    
    daily_summary = logs_df.groupby('date').agg(
        Calls=('record_type', lambda x: (x == 'call').sum()),
        SMS=('record_type', lambda x: (x == 'sms').sum()),
        Data_Usage_MB=('data_mb_used', 'sum')
    ).reset_index()

    return daily_summary

def get_top_customers(session, top_n=10):
    """Identifies the top N customers by data usage."""
    query = session.query(
        Customer.name,
        func.sum(UsageLog.data_mb_used).label('total_data_usage')
    ).join(UsageLog, Customer.id == UsageLog.customer_id)\
     .group_by(Customer.name)\
     .order_by(func.sum(UsageLog.data_mb_used).desc())\
     .limit(top_n)

    top_customers_df = pd.read_sql(query.statement, session.bind)
    return top_customers_df

def get_hourly_usage_distribution(session):
    """Calculates the total number of network events for each hour of the day."""
    query = session.query(
        extract('hour', UsageLog.timestamp).label('hour'),
        func.count(UsageLog.id).label('event_count')
    ).group_by('hour').order_by('hour')

    hourly_df = pd.read_sql(query.statement, session.bind)
    return hourly_df

def get_customer_daily_trends(session, customer_id):
    """Aggregates a single customer's usage data by day for trend analysis."""
    query = session.query(UsageLog.timestamp, UsageLog.record_type, UsageLog.data_mb_used)\
                   .filter(UsageLog.customer_id == customer_id)
    
    logs_df = pd.read_sql(query.statement, session.bind)
    if logs_df.empty:
        return pd.DataFrame()

    logs_df['date'] = pd.to_datetime(logs_df['timestamp']).dt.date
    
    daily_summary = logs_df.groupby('date').agg(
        Calls=('record_type', lambda x: (x == 'call').sum()),
        SMS=('record_type', lambda x: (x == 'sms').sum()),
        Data_Usage_MB=('data_mb_used', 'sum')
    ).reset_index()

    daily_summary['Total_Events'] = daily_summary['Calls'] + daily_summary['SMS'] + (daily_summary['Data_Usage_MB'] > 0).astype(int)

    # --- NEW ---: Ensure all days are present for the heatmap
    if not daily_summary.empty:
        min_date = daily_summary['date'].min()
        max_date = daily_summary['date'].max()
        all_days = pd.date_range(start=min_date, end=max_date, freq='D').date
        daily_summary = daily_summary.set_index('date').reindex(all_days, fill_value=0).reset_index()
        daily_summary = daily_summary.rename(columns={'index': 'date'})


    return daily_summary

def get_customer_hourly_distribution(session, customer_id):
    """Calculates the total number of network events for each hour for a single customer."""
    query = session.query(
        extract('hour', UsageLog.timestamp).label('hour'),
        func.count(UsageLog.id).label('event_count')
    ).filter(UsageLog.customer_id == customer_id).group_by('hour').order_by('hour')

    hourly_df = pd.read_sql(query.statement, session.bind)
    return hourly_df
# Add this new function to the end of module2_analytics.py

def get_customer_monthly_trends(session, customer_id):
    """Aggregates a single customer's usage data by month."""
    query = session.query(
        func.strftime('%Y-%m', UsageLog.timestamp).label('month'),
        func.count(UsageLog.id).label('total_events')
    ).filter(UsageLog.customer_id == customer_id).group_by('month').order_by('month')
    
    monthly_df = pd.read_sql(query.statement, session.bind)
    return monthly_df