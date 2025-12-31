"""
Streamlit Web Application: Customer Usage Analytics
- A multi-page app for telecom data analysis and churn prediction.
- Features role-based access control, interactive dashboards, and ML-driven insights.
"""
# Add this with your other imports at the top of streamlit_app.py
# Change this line at the top of streamlit_app.py
import plotly.graph_objects as go
from module2_analytics import (get_calendar_heatmap_data, get_customer_analytics, get_features_for_ml, get_network_analytics, get_data_for_ml,
                                 get_daily_network_trends, get_top_customers, get_hourly_usage_distribution,
                                 get_customer_daily_trends, get_customer_hourly_distribution,
                                 get_customer_monthly_trends) # <-- Add the new function here
import streamlit as st
import pandas as pd
from ml_models.training_pipeline import AnalyticsPipeline
import plotly.express as px
from module1_data_db import (DatabaseManager, AuthManager, DataManager, User, 
                                Customer, UsageLog, mask_phone_number)
from module2_analytics import (get_customer_analytics, get_network_analytics, get_data_for_ml,
                                 get_daily_network_trends, get_top_customers, get_hourly_usage_distribution,
                                 get_customer_daily_trends, get_customer_hourly_distribution)
from module5_ml_analysis import train_churn_model, predict_churn_and_recommend

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Telco Analytics Hub",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZATION & CACHING ---
@st.cache_resource
def init_managers():
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    data_manager = DataManager(db_manager)
    return db_manager, auth_manager, data_manager

db, auth, data_manager = init_managers()

@st.cache_data(ttl=300)
def fetch_customers_df():
    session = db.get_session()
    try:
        customers = session.query(Customer.id, Customer.name, Customer.phone_number).all()
        df = pd.DataFrame(customers, columns=["id", "name", "phone_number"])
        df["masked_phone"] = df["phone_number"].apply(mask_phone_number)
        return df
    finally:
        session.close()

# --- UI HELPER FUNCTIONS ---
def display_kpi(label, value, help_text=""):
    st.metric(label=label, value=value, help=help_text)

def show_login_page():
    st.title("📡 Telco Analytics Hub")
    st.markdown("Please log in to access the dashboard.")
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = auth.authenticate(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = user.username
                st.session_state['role'] = user.role
                st.rerun()
            else:
                st.error("Invalid username or password.")

# --- UI PAGE FUNCTIONS ---

def show_dashboard():
    st.header("Network Overview Dashboard")
    session = db.get_session()
    
    # KPIs remain at the top
    summary = get_network_analytics(session)
    cols = st.columns(4)
    with cols[0]: display_kpi("Total Customers", f"{summary['total_customers']:,}")
    with cols[1]: display_kpi("Total Calls Logged", f"{summary['total_calls']:,}")
    with cols[2]: display_kpi("Total SMS Logged", f"{summary['total_sms']:,}")
    with cols[3]: display_kpi("Total Data Usage (GB)", f"{summary['total_data_gb']:,.2f}")
    
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Peak Activity Hours")
        hourly_df = get_hourly_usage_distribution(session)
        if hourly_df.empty:
            st.info("Not enough data to show hourly trends.")
        else:
            fig = px.bar(hourly_df, x='hour', y='event_count',
                         title="Total Network Events by Hour of Day",
                         labels={'hour': 'Hour of Day (24h)', 'event_count': 'Total Events (Calls, SMS, etc.)'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Call vs. SMS Distribution")
        if summary['total_calls'] > 0 or summary['total_sms'] > 0:
            pie_data = pd.DataFrame({
                'type': ['Calls', 'SMS'],
                'count': [summary['total_calls'], summary['total_sms']]
            })
            fig = px.pie(pie_data, names='type', values='count', 
                         title="Proportion of Calls vs. SMS", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No call or SMS data to display.")

    st.markdown("---")

    # --- NEW TAB-BASED LAYOUT ---
    tab1, tab2, tab3 = st.tabs(["🗓️ Monthly Trends", "📊 Daily Trends", "🏆 Top Performers"])

    with tab1:
        st.subheader("Network Activity Calendar")
        calendar_df = get_calendar_heatmap_data(session)
        if calendar_df.empty:
            st.info("Not enough data to build an activity calendar.")
        else:
            calendar_df['month_str'] = calendar_df['date'].dt.strftime('%Y-%m (%B)')
            available_months = calendar_df['month_str'].unique()
            selected_month_str = st.selectbox("Select a month to view:", available_months, index=len(available_months)-1)

            month_data = calendar_df[calendar_df['month_str'] == selected_month_str]
            
            first_day_of_month = month_data['date'].min()
            first_weekday = first_day_of_month.dayofweek
            
            cal_data = [([None] * 7) for _ in range(6)]
            cal_text = [([None] * 7) for _ in range(6)]
            
            for i, row in month_data.iterrows():
                day_num = row['date'].day
                day_weekday = row['date'].dayofweek
                week_num = (day_num + first_weekday - 1) // 7
                
                if week_num < 6:
                    cal_data[week_num][day_weekday] = row['total_events']
                    cal_text[week_num][day_weekday] = f"<b>{day_num}</b><br>{row['total_events']} events"

            fig = go.Figure(data=go.Heatmap(
                z=cal_data,
                x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                y=[f'Week {i+1}' for i in range(6)],
                text=cal_text,
                texttemplate="%{text}",
                hoverinfo='none',
                colorscale='Reds',
                showscale=True,
                xgap=3, ygap=3
            ))
            fig.update_layout(
                title=f'Activity Calendar for {selected_month_str.split(" ")[0]}',
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Network Usage Trends (Last 30 Days)")
        trends_df = get_daily_network_trends(session)
        if trends_df.empty:
            st.info("Not enough daily data to display trends.")
        else:
            trends_df['date'] = pd.to_datetime(trends_df['date'])
            fig_line = px.line(trends_df, x='date', y=['Calls', 'SMS', 'Data_Usage_MB'],
                          title="Daily Network Activity", labels={'value': 'Count / MB', 'variable': 'Metric'})
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Peak Activity Hours")
            hourly_df = get_hourly_usage_distribution(session)
            if not hourly_df.empty:
                fig_bar = px.bar(hourly_df, x='hour', y='event_count', labels={'hour': 'Hour of Day', 'event_count': 'Total Events'})
                st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("Top 10 Customers by Data Usage")
            top_customers_df = get_top_customers(session)
            if not top_customers_df.empty:
                fig_bar_top = px.bar(top_customers_df, x='name', y='total_data_usage', labels={'name': 'Customer', 'total_data_usage': 'Data Usage (MB)'})
                st.plotly_chart(fig_bar_top, use_container_width=True)
            
    session.close()

def show_customer_report():
    st.header("Individual Customer Analytics")
    session = db.get_session()
    customers_df = fetch_customers_df()

    if customers_df.empty:
        st.warning("No customers found. Please add a customer first.")
        session.close()
        return

    selected_customer_id = st.selectbox(
        "Select a Customer", 
        customers_df["id"],
        format_func=lambda x: f"{customers_df.loc[customers_df['id'] == x, 'name'].iloc[0]} ({customers_df.loc[customers_df['id'] == x, 'masked_phone'].iloc[0]})"
    )

    if selected_customer_id:
        analytics = get_customer_analytics(session, selected_customer_id)
        if not analytics or not analytics['has_data']:
            st.error("No usage data available for this customer.")
            session.close()
            return

        st.subheader(f"Usage Snapshot for {analytics['name']}")
        
        cols = st.columns(5)
        with cols[0]: display_kpi("Customer ID", analytics['id'])
        with cols[1]: display_kpi("Total Calls", analytics['total_calls'])
        with cols[2]: display_kpi("Total SMS", analytics['total_sms'])
        with cols[3]: display_kpi("Total Data (MB)", f"{analytics['total_data_mb']:.2f}")
        with cols[4]: display_kpi("Peak Hour", analytics['peak_usage_hour'])
        
        st.markdown("---")
        
        # --- NEW VISUALIZATION LAYOUT ---
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Hourly Activity Rhythm")
            st.markdown("This curve shows the customer's activity pattern throughout the day, making it easy to spot their peak usage times.")
            hourly_df = get_customer_hourly_distribution(session, selected_customer_id)
            if hourly_df.empty:
                st.info("Not enough data for hourly analysis.")
            else:
                # Create a smooth area chart to show the curve
                fig_area_hourly = px.area(hourly_df, x='hour', y='event_count',
                                          labels={'hour': 'Hour of Day (24h)', 'event_count': 'Total Events'},
                                          line_shape='spline') # This creates the smooth curve
                fig_area_hourly.update_traces(line=dict(color='#FFA15A'))
                st.plotly_chart(fig_area_hourly, use_container_width=True)

        with col2:
            st.subheader("Monthly Engagement")
            st.markdown("This chart shows the customer's total number of events for each month, indicating their long-term engagement.")
            monthly_trends_df = get_customer_monthly_trends(session, selected_customer_id)
            if monthly_trends_df.empty:
                st.info("Not enough data to display monthly trends.")
            else:
                # Using a smooth curve for monthly trends as well
                fig_monthly_curve = px.area(monthly_trends_df, x='month', y='total_events',
                                          labels={'month': 'Month', 'total_events': 'Total Events'},
                                          line_shape='spline')
                st.plotly_chart(fig_monthly_curve, use_container_width=True)

        st.markdown("---")
        st.subheader("Daily Usage Trend by Type")
        trends_df = get_customer_daily_trends(session, selected_customer_id)
        if trends_df.empty:
            st.info("Not enough daily data to display a trend.")
        else:
            trends_df['date'] = pd.to_datetime(trends_df['date'])
            fig_line = px.line(trends_df, x='date', y=['Calls', 'SMS', 'Data_Usage_MB'],
                               labels={'value': 'Count / MB', 'variable': 'Metric'})
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)
    
    session.close()

def show_data_management():
    st.header("Data Management")
    
    tab1, tab2 = st.tabs(["Add New Customer", "Upload CDR Data"])

    with tab1:
        st.subheader("Add a New Customer")
        with st.form("add_customer_form", clear_on_submit=True):
            name = st.text_input("Customer Name")
            phone = st.text_input("Customer Phone Number")
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if name and phone:
                    if data_manager.add_customer(name, phone):
                        st.success(f"Customer '{name}' added successfully!")
                        st.cache_data.clear()
                    else:
                        st.error("A customer with this phone number already exists.")
                else:
                    st.warning("Please provide both name and phone number.")

    with tab2:
        st.subheader("Upload CDR Data from CSV")
        st.info("""
        **Required CSV Columns:** `customer_id`, `type` (call/sms/data), `timestamp` (optional), 
        `calling_number` (optional), `called_number` (optional), 
        `duration_seconds` (for calls), `data_mb_used` (for data)
        """)
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                processed_count = data_manager.process_cdr_upload(df)
                st.success(f"Successfully processed and loaded {processed_count} records.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Failed to process file: {e}")

def show_advanced_analytics():
    st.header("🧠 Advanced Analytics Engine")
    
    with st.spinner("Performing in-depth analysis... This may take a moment."):
        features_df = get_features_for_ml(db.get_session())
        if features_df.empty:
            st.error("Not enough customer data to perform advanced analytics.")
            return
            
        pipeline = AnalyticsPipeline(features_df)
        segmented_df = pipeline.perform_segmentation()
        pipeline.train_churn_models()
        final_df = pipeline.generate_recommendations()

    st.subheader("Individual Customer Deep Dive")
    
    customer_list = final_df['name'].tolist()
    selected_customer_name = st.selectbox("Select a Customer to Analyze:", customer_list)
    selected_customer_data = final_df[final_df['name'] == selected_customer_name].iloc[0]

    st.markdown("---")

    seg = selected_customer_data['Segment']
    prob = selected_customer_data['Churn_Probability']
    
    st.write(f"### Analysis for: **{selected_customer_name}**")
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("#### Churn Risk Assessment")
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = prob * 100,
            title = {'text': "Churn Probability"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "#636EFA"},
                     'steps' : [
                         {'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 75], 'color': "gray"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
        fig_gauge.update_layout(height=250, margin=dict(t=40, b=40))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.metric("Customer Segment", seg)


    with col2:
        st.write("#### Key Predictive Factors")
        
        if pipeline.feature_importances is not None:
            top_features = pipeline.feature_importances.head(3)
            fig_bar = px.bar(top_features, x='Importance', y='Feature', orientation='h',
                             title="Top 3 Factors Driving Prediction")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Feature importance data is not available.")
    
    st.markdown("---")
    st.markdown(f"#### Strategic Business Recommendation:")
    st.info(selected_customer_data['Recommendation'])

    st.markdown("---")

    st.subheader("Overall Business Insights")
    tab1, tab2, tab3 = st.tabs(["📊 Customer Segmentation", "📈 Churn Model Performance", "📋 Full Data View"])

    with tab1:
        st.subheader("Customer Segments")
        c1, c2 = st.columns([1, 2])
        segment_counts = segmented_df['Segment'].value_counts()
        fig_pie = px.pie(segment_counts, names=segment_counts.index, values=segment_counts.values, title="Distribution of Customer Segments", hole=0.4)
        c1.plotly_chart(fig_pie, use_container_width=True)
        segment_desc = {
            "High-Value": "Your most valuable customers. Goal: Retain and nurture.",
            "Medium-Value": "The stable backbone of the business. Goal: Upsell and increase value.",
            "Low-Value": "Inactive or low-spending customers. Goal: Re-engage with low-cost campaigns."
        }
        c2.write("#### Segment Descriptions:")
        for seg, desc in segment_desc.items():
            c2.markdown(f"**{seg}:** {desc}")

    with tab2:
        st.subheader("Churn Prediction Model Evaluation")
        if not pipeline.model_reports:
            st.warning("Models could not be trained.")
        else:
            c1, c2 = st.columns(2)
            for model_name, report in pipeline.model_reports.items():
                container = c1 if "Logistic" in model_name else c2
                container.write(f"#### {model_name}")
                container.json(report)
                
    with tab3:
        st.subheader("Full Analytics Data")
        st.dataframe(final_df[['name', 'Segment', 'Churn_Probability', 'Recency', 'Frequency', 'MonetaryValue', 'TotalDataMB']])


def show_admin_panel():
    st.header("🛠️ Admin Panel")

    # --- Add New User Section ---
    with st.expander("➕ Add New User"):
        with st.form("add_user_form", clear_on_submit=True):
            st.subheader("Create a New User Account")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Assign Role", ["operator", "analyst", "admin"])
            
            if st.form_submit_button("Create User"):
                if new_username and new_password:
                    if auth.create_user(new_username, new_password, new_role):
                        st.success(f"User '{new_username}' created successfully.")
                        st.cache_data.clear() # Clear cache to refresh user list
                        st.rerun()
                    else:
                        st.error(f"User '{new_username}' already exists.")
                else:
                    st.warning("Please provide both a username and a password.")

    st.markdown("---")

    # --- Main Admin View with Two Columns ---
    col1, col2 = st.columns([2, 1]) # Make the first column wider

    with col1:
        st.subheader("👥 Existing Users")
        all_users = auth.get_all_users()
        
        if all_users:
            user_data = {
                "ID": [u.id for u in all_users],
                "Username": [u.username for u in all_users],
                "Role": [u.role for u in all_users]
            }
            users_df = pd.DataFrame(user_data)
            
            st.dataframe(users_df, use_container_width=True)

            # --- Delete User Section ---
            st.markdown("---")
            st.subheader("🗑️ Delete a User")
            
            # Exclude the current user from the list of users that can be deleted
            users_to_delete_df = users_df[users_df["Username"] != st.session_state['username']]
            
            if not users_to_delete_df.empty:
                user_to_delete_name = st.selectbox(
                    "Select a user to delete:",
                    users_to_delete_df['Username'].tolist()
                )
                
                if st.button(f"Delete User: {user_to_delete_name}", type="primary"):
                    user_id_to_delete = users_to_delete_df[users_to_delete_df["Username"] == user_to_delete_name]["ID"].iloc[0]
                    if auth.delete_user(user_id_to_delete):
                        st.success(f"User '{user_to_delete_name}' has been deleted.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to delete user.")
            else:
                st.info("No other users are available to delete.")
        else:
            st.info("No users found.")

    with col2:
        st.subheader("📊 Role Distribution")
        role_dist_df = auth.get_role_distribution()
        
        if not role_dist_df.empty:
            fig_pie = px.pie(role_dist_df, names='Role', values='Count', 
                             title="User Roles", hole=0.4,
                             color_discrete_map={'admin':'#FFA15A', 'analyst':'#636EFA', 'operator':'#B6E880'})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No role data to display.")
# --- MAIN APP ROUTING ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login_page()
else:
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.markdown(f"**Role:** `{st.session_state.role}`")
    st.sidebar.markdown("---")
    
    role_pages = {
        'admin': ["Dashboard", "Customer Report", "Data Management", "Advanced Analytics", "Admin Panel"],
        'analyst': ["Dashboard", "Customer Report", "Advanced Analytics"],
        'operator': ["Data Management"]
    }
    
    pages = role_pages.get(st.session_state.role, [])
    if not pages:
        st.error("Your user role has no pages assigned. Please contact an admin.")
        st.stop()
        
    choice = st.sidebar.radio("Navigation", pages)
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if choice == "Dashboard": show_dashboard()
    elif choice == "Customer Report": show_customer_report()
    elif choice == "Data Management": show_data_management()
    elif choice == "Advanced Analytics": show_advanced_analytics()
    elif choice == "Admin Panel": show_admin_panel()