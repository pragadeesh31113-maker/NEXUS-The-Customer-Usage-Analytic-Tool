"""
Module 5: Advanced ML Analytics
- Provides functions for churn prediction using a Gradient Boosting model.
- Includes data preprocessing, model training, prediction, and explanation.
- Generates actionable recommendations for at-risk customers.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

def train_churn_model(df):
    """
    Preprocesses data and trains a churn prediction model.
    """
    if df.empty or len(df) < 10:
        return None, None, None, "Not enough data to train model."

    # Define churn: customers with low activity and high recency
    df['churn'] = ((df['total_calls'] < 5) & (df['total_data_mb'] < 100) & (df['recency_days'] > 30)).astype(int)
    
    if df['churn'].nunique() < 2:
        return None, None, None, "Not enough churn examples to train a model."

    features = ['total_calls', 'total_sms', 'total_data_mb', 'avg_call_duration', 'recency_days']
    target = 'churn'

    X = df[features]
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.25, random_state=42, stratify=y)

    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return model, scaler, features, report

def predict_churn_and_recommend(model, scaler, features, df):
    """
    Predicts churn for all customers and generates tailored recommendations.
    """
    X = df[features]
    X_scaled = scaler.transform(X)

    df['churn_prediction'] = model.predict(X_scaled)
    df['churn_probability'] = model.predict_proba(X_scaled)[:, 1]

    at_risk_customers = df[df['churn_prediction'] == 1].copy()

    recommendations = []
    for _, row in at_risk_customers.iterrows():
        rec = f"**Customer:** {row['name']} (Churn Probability: {row['churn_probability']:.0%})\n"
        if row['total_data_mb'] < 50:
            rec += "- **Issue:** Very low data usage. \n- **Recommendation:** Offer a bonus data pack or a discount on data plans."
        elif row['recency_days'] > 45:
            rec += "- **Issue:** Inactive for a long time. \n- **Recommendation:** Launch a re-engagement campaign with a special 'welcome back' offer."
        elif row['total_calls'] < 2:
            rec += "- **Issue:** Low call engagement. \n- **Recommendation:** Offer bonus minutes or free calls to specific networks."
        else:
            rec += "- **Issue:** General low engagement. \n- **Recommendation:** Conduct a customer satisfaction survey to identify pain points."
        recommendations.append(rec)
        
    at_risk_customers['recommendation'] = recommendations
    return at_risk_customers[['name', 'churn_probability', 'recommendation']]