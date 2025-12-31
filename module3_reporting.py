# """
# Module 3: Reporting
# - Generates formatted tabular reports using PrettyTable.
# - Supports customer-wise and overall network reports.
# - Masks phone numbers for privacy.
# """

# from prettytable import PrettyTable

# def mask_phone(phone):
#     return phone[-4:].rjust(len(phone), "*")

# def report_customer_summary(phone_number, summary):
#     table = PrettyTable()
#     table.field_names = ["Phone Number", "Total Calls", "Total SMS", "Total Data (MB)", "Peak Call Hour"]
#     peak_hr = f"{summary['peak_call_hour']}:00" if summary['peak_call_hour'] is not None else "N/A"
#     masked_phone = mask_phone(phone_number)
#     table.add_row([masked_phone, summary['total_calls'], summary['total_sms'], f"{summary['total_data']:.2f}", peak_hr])
#     print(table)

# def report_network_summary(summary):
#     table = PrettyTable()
#     table.field_names = ["Total Calls", "Total SMS", "Total Data (MB)"]
#     table.add_row([summary['total_calls'], summary['total_sms'], f"{summary['total_data']:.2f}"])
#     print(table)
"""
Module 3: Reporting
- Generates formatted tabular and CSV reports.
- Supports customer-wise and overall network reports.
"""
import pandas as pd
from io import StringIO

def generate_customer_report_df(customer_id, summary):
    """Generates a pandas DataFrame for a single customer's report."""
    data = {
        'Customer ID': [customer_id],
        'Total Calls': [summary['total_calls']],
        'Total SMS': [summary['total_sms']],
        'Total Data (MB)': [summary['total_data']],
        'Peak Call Hour': [f"{summary['peak_call_hour']}:00" if summary['peak_call_hour'] is not None else "N/A"]
    }
    return pd.DataFrame(data)

def generate_network_report_df(summary):
    """Generates a pandas DataFrame for the network summary report."""
    data = {
        'Total Calls': [summary['total_calls']],
        'Total SMS': [summary['total_sms']],
        'Total Data (GB)': [summary['total_data'] / 1024]
    }
    return pd.DataFrame(data)

def to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()