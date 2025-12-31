# """
# training_pipeline.py
# - A dedicated module for all advanced machine learning tasks.
# - Performs customer segmentation, trains multiple churn models, evaluates them,
#   and generates strategic recommendations.
# """
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# import lightgbm as lgb
# from sklearn.metrics import accuracy_score, classification_report

# class AnalyticsPipeline:
#     def __init__(self, features_df):
#         self.features_df = features_df.copy()
#         self.segmented_df = None
#         self.churn_models = {}
#         self.model_reports = {}
#         self.final_df = None
#         self.feature_importances = None

#     def perform_segmentation(self):
#         """
#         Groups customers into High, Medium, and Low-Value segments using KMeans clustering.
#         """
#         segment_features = self.features_df[['Recency', 'Frequency', 'MonetaryValue']]
#         scaler = StandardScaler()
#         scaled_features = scaler.fit_transform(segment_features)
        
#         kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
#         self.features_df['Segment_ID'] = kmeans.fit_predict(scaled_features)
        
#         segment_centers = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=['Recency', 'Frequency', 'MonetaryValue'])
#         high_value_cluster = segment_centers.sort_values(by='MonetaryValue', ascending=False).index[0]
#         low_value_cluster = segment_centers.sort_values(by='Recency', ascending=False).index[0]
        
#         segment_map = { high_value_cluster: 'High-Value', low_value_cluster: 'Low-Value' }
#         medium_value_cluster = list({0, 1, 2} - set(segment_map.keys()))[0]
#         segment_map[medium_value_cluster] = 'Medium-Value'
        
#         self.features_df['Segment'] = self.features_df['Segment_ID'].map(segment_map)
#         self.segmented_df = self.features_df
#         return self.segmented_df

#     def train_churn_models(self):
#         """
#         Trains and evaluates multiple ML models and captures feature importances.
#         """
#         self.segmented_df['Churn'] = (self.segmented_df['Recency'] > 30).astype(int)
        
#         if self.segmented_df['Churn'].nunique() < 2:
#             return

#         features = ['Recency', 'Frequency', 'MonetaryValue', 'TotalDataMB', 'TotalCalls', 'TotalSMS']
#         target = 'Churn'
        
#         X = self.segmented_df[features]
#         y = self.segmented_df[target]
        
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        
#         # Train Models
#         lr = LogisticRegression(random_state=42)
#         lr.fit(X_train, y_train)
#         self.churn_models['Logistic Regression'] = lr
#         self.model_reports['Logistic Regression'] = classification_report(y_test, lr.predict(X_test), output_dict=True)
        
#         lgbm = lgb.LGBMClassifier(random_state=42)
#         lgbm.fit(X_train, y_train)
#         self.churn_models['LightGBM'] = lgbm
#         self.model_reports['LightGBM'] = classification_report(y_test, lgbm.predict(X_test), output_dict=True)
        
#         # Capture Feature Importances from the best model (LightGBM)
#         self.feature_importances = pd.DataFrame({'Feature': features, 'Importance': lgbm.feature_importances_}).sort_values(by='Importance', ascending=False)
        
#         self.segmented_df['Churn_Probability'] = lgbm.predict_proba(X)[:, 1]

#     def generate_recommendations(self):
#         """
#         Generates extensive, business-focused recommendations.
#         """
#         recommendations = []
#         for _, row in self.segmented_df.iterrows():
#             rec_text = ""
#             # High-Value Customers
#             if row['Segment'] == 'High-Value':
#                 if row['Churn_Probability'] > 0.6:
#                     rec_text = """
#                     **Segment:** High-Value Customer (At Risk)
#                     - **Situation Analysis:** This is a top-tier customer who is showing significant signs of churning. Losing them would be a major revenue loss.
#                     - **Immediate Action:** Assign a senior retention manager to personally contact the customer. Do not use automated messages.
#                     - **Business Recommendation:** Authorize the manager to offer a significant, personalized incentive. Examples: A 25% discount for the next 6 months, a free upgrade to the next device tier, or a premium service bundle at no extra cost. The goal is immediate retention.
#                     """
#                 else:
#                     rec_text = """
#                     **Segment:** High-Value Customer (Loyal)
#                     - **Situation Analysis:** This is a loyal and profitable customer. The goal is to reinforce their loyalty and make them feel valued.
#                     - **Business Recommendation:** Proactively enroll them in the company's VIP program. Offer them early access to new products or services. A small, unexpected gift (e.g., bonus data pack, free movie rental) can go a long way in strengthening the relationship.
#                     """
            
#             # Medium-Value Customers
#             elif row['Segment'] == 'Medium-Value':
#                 if row['Churn_Probability'] > 0.5:
#                     rec_text = """
#                     **Segment:** Medium-Value Customer (At Risk)
#                     - **Situation Analysis:** This customer forms the core of the business and is at risk. Their churn could indicate a wider problem with this segment.
#                     - **Business Recommendation:** Target them with a high-value upsell offer. For example, "Get double the data for only ₹100 more per month for the next 3 months." This both provides more value to the customer and increases their revenue potential, making them less likely to leave.
#                     """
#                 else:
#                     rec_text = """
#                     **Segment:** Medium-Value Customer (Stable)
#                     - **Situation Analysis:** This is a stable customer with potential for growth.
#                     - **Business Recommendation:** Analyze their specific usage to identify an upsell opportunity. If they are a heavy data user, promote data booster packs. If they make many international calls, promote an international calling plan. The recommendation should be targeted and data-driven.
#                     """

#             # Low-Value Customers
#             else: # Low-Value
#                 rec_text = """
#                 **Segment:** Low-Value Customer
#                 - **Situation Analysis:** This customer has low engagement and revenue. While their churn is not a high priority, retaining them is still beneficial.
#                 - **Business Recommendation:** Do not invest heavily in retaining this segment. Instead, use low-cost, automated marketing campaigns. Include them in SMS blasts about new network-wide promotions or a basic "We miss you!" offer with a small data bonus to encourage re-engagement.
#                 """
            
#             recommendations.append(rec_text)
        
#         self.segmented_df['Recommendation'] = recommendations
#         self.final_df = self.segmented_df
#         return self.final_df

# """
# training_pipeline.py
# - A dedicated module for all advanced machine learning tasks.
# - Performs customer segmentation, trains multiple churn models, evaluates them,
#   and generates strategic recommendations.
# """
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# import lightgbm as lgb
# from sklearn.metrics import accuracy_score, classification_report

# class AnalyticsPipeline:
#     def __init__(self, features_df):
#         self.features_df = features_df.copy()
#         self.segmented_df = None
#         self.churn_models = {}
#         self.model_reports = {}
#         self.final_df = None
#         self.feature_importances = None

#     def perform_segmentation(self):
#         """
#         Groups customers into High, Medium, and Low-Value segments using KMeans clustering.
#         """
#         segment_features = self.features_df[['Recency', 'Frequency', 'MonetaryValue']]
#         scaler = StandardScaler()
#         scaled_features = scaler.fit_transform(segment_features)
        
#         kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
#         self.features_df['Segment_ID'] = kmeans.fit_predict(scaled_features)
        
#         segment_centers = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=['Recency', 'Frequency', 'MonetaryValue'])
#         high_value_cluster = segment_centers.sort_values(by='MonetaryValue', ascending=False).index[0]
#         low_value_cluster = segment_centers.sort_values(by='Recency', ascending=False).index[0]
        
#         segment_map = { high_value_cluster: 'High-Value', low_value_cluster: 'Low-Value' }
#         medium_value_cluster = list({0, 1, 2} - set(segment_map.keys()))[0]
#         segment_map[medium_value_cluster] = 'Medium-Value'
        
#         self.features_df['Segment'] = self.features_df['Segment_ID'].map(segment_map)
#         self.segmented_df = self.features_df
#         return self.segmented_df

#     def train_churn_models(self):
#         """
#         Trains and evaluates multiple ML models and captures feature importances.
#         """
#         self.segmented_df['Churn'] = (self.segmented_df['Recency'] > 30).astype(int)
        
#         if self.segmented_df['Churn'].nunique() < 2:
#             return

#         features = ['Recency', 'Frequency', 'MonetaryValue', 'TotalDataMB', 'TotalCalls', 'TotalSMS']
#         target = 'Churn'
        
#         X = self.segmented_df[features]
#         y = self.segmented_df[target]
        
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        
#         # Train Models
#         lr = LogisticRegression(random_state=42)
#         lr.fit(X_train, y_train)
#         self.churn_models['Logistic Regression'] = lr
#         self.model_reports['Logistic Regression'] = classification_report(y_test, lr.predict(X_test), output_dict=True)
        
#         lgbm = lgb.LGBMClassifier(random_state=42)
#         lgbm.fit(X_train, y_train)
#         self.churn_models['LightGBM'] = lgbm
#         self.model_reports['LightGBM'] = classification_report(y_test, lgbm.predict(X_test), output_dict=True)
        
#         # Capture Feature Importances from the best model (LightGBM)
#         self.feature_importances = pd.DataFrame({'Feature': features, 'Importance': lgbm.feature_importances_}).sort_values(by='Importance', ascending=False)
        
#         self.segmented_df['Churn_Probability'] = lgbm.predict_proba(X)[:, 1]

#     def generate_recommendations(self):
#         """
#         Generates extensive, business-focused recommendations.
#         """
#         recommendations = []
#         for _, row in self.segmented_df.iterrows():
#             rec_text = ""
#             # High-Value Customers
#             if row['Segment'] == 'High-Value':
#                 if row['Churn_Probability'] > 0.6:
#                     rec_text = """
#                     **Segment:** High-Value Customer (At Risk)
#                     - **Situation Analysis:** This is a top-tier customer who is showing significant signs of churning. Losing them would be a major revenue loss.
#                     - **Immediate Action:** Assign a senior retention manager to personally contact the customer. Do not use automated messages.
#                     - **Business Recommendation:** Authorize the manager to offer a significant, personalized incentive. Examples: A 25% discount for the next 6 months, a free upgrade to the next device tier, or a premium service bundle at no extra cost. The goal is immediate retention.
#                     """
#                 else:
#                     rec_text = """
#                     **Segment:** High-Value Customer (Loyal)
#                     - **Situation Analysis:** This is a loyal and profitable customer. The goal is to reinforce their loyalty and make them feel valued.
#                     - **Business Recommendation:** Proactively enroll them in the company's VIP program. Offer them early access to new products or services. A small, unexpected gift (e.g., bonus data pack, free movie rental) can go a long way in strengthening the relationship.
#                     """
            
#             # Medium-Value Customers
#             elif row['Segment'] == 'Medium-Value':
#                 if row['Churn_Probability'] > 0.5:
#                     rec_text = """
#                     **Segment:** Medium-Value Customer (At Risk)
#                     - **Situation Analysis:** This customer forms the core of the business and is at risk. Their churn could indicate a wider problem with this segment.
#                     - **Business Recommendation:** Target them with a high-value upsell offer. For example, "Get double the data for only ₹100 more per month for the next 3 months." This both provides more value to the customer and increases their revenue potential, making them less likely to leave.
#                     """
#                 else:
#                     rec_text = """
#                     **Segment:** Medium-Value Customer (Stable)
#                     - **Situation Analysis:** This is a stable customer with potential for growth.
#                     - **Business Recommendation:** Analyze their specific usage to identify an upsell opportunity. If they are a heavy data user, promote data booster packs. If they make many international calls, promote an international calling plan. The recommendation should be targeted and data-driven.
#                     """

#             # Low-Value Customers
#             else: # Low-Value
#                 rec_text = """
#                 **Segment:** Low-Value Customer
#                 - **Situation Analysis:** This customer has low engagement and revenue. While their churn is not a high priority, retaining them is still beneficial.
#                 - **Business Recommendation:** Do not invest heavily in retaining this segment. Instead, use low-cost, automated marketing campaigns. Include them in SMS blasts about new network-wide promotions or a basic "We miss you!" offer with a small data bonus to encourage re-engagement.
#                 """
            
#             recommendations.append(rec_text)
        
#         self.segmented_df['Recommendation'] = recommendations
#         self.final_df = self.segmented_df
#         return self.final_df

"""
training_pipeline.py
- A dedicated module for all advanced machine learning tasks.
- Performs customer segmentation, trains multiple churn models, evaluates them,
  and generates strategic recommendations.
- New: Calculates SHAP values for model explainability.
"""
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
from sklearn.metrics import classification_report
import shap

class AnalyticsPipeline:
    def __init__(self, features_df):
        self.features_df = features_df.copy()
        self.segmented_df = None
        self.churn_models = {}
        self.model_reports = {}
        self.final_df = None
        self.feature_importances = None
        # --- NEW ATTRIBUTES FOR SHAP ---
        self.shap_explainer = None
        self.shap_values = None
        self.X = None # Will store the feature set

    def perform_segmentation(self):
        """
        Groups customers into High, Medium, and Low-Value segments using KMeans clustering.
        """
        segment_features = self.features_df[['Recency', 'Frequency', 'MonetaryValue']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(segment_features)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.features_df['Segment_ID'] = kmeans.fit_predict(scaled_features)
        
        segment_centers = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=['Recency', 'Frequency', 'MonetaryValue'])
        high_value_cluster = segment_centers.sort_values(by='MonetaryValue', ascending=False).index[0]
        low_value_cluster = segment_centers.sort_values(by='Recency', ascending=False).index[0]
        
        segment_map = { high_value_cluster: 'High-Value', low_value_cluster: 'Low-Value' }
        medium_value_cluster = list({0, 1, 2} - set(segment_map.keys()))[0]
        segment_map[medium_value_cluster] = 'Medium-Value'
        
        self.features_df['Segment'] = self.features_df['Segment_ID'].map(segment_map)
        self.segmented_df = self.features_df
        return self.segmented_df

    def train_churn_models(self):
        """
        Trains and evaluates multiple ML models and calculates SHAP values for explainability.
        """
        self.segmented_df['Churn'] = (self.segmented_df['Recency'] > 30).astype(int)
        
        if self.segmented_df['Churn'].nunique() < 2:
            return

        features = ['Recency', 'Frequency', 'MonetaryValue', 'TotalDataMB', 'TotalCalls', 'TotalSMS']
        target = 'Churn'
        
        self.X = self.segmented_df[features] # Store X for SHAP
        y = self.segmented_df[target]
        
        X_train, X_test, y_train, y_test = train_test_split(self.X, y, test_size=0.3, random_state=42, stratify=y)
        
        # Train models (code remains the same)
        lr = LogisticRegression(random_state=42)
        lr.fit(X_train, y_train)
        self.churn_models['Logistic Regression'] = lr
        self.model_reports['Logistic Regression'] = classification_report(y_test, lr.predict(X_test), output_dict=True)
        
        lgbm = lgb.LGBMClassifier(random_state=42)
        lgbm.fit(X_train, y_train)
        self.churn_models['LightGBM'] = lgbm
        self.model_reports['LightGBM'] = classification_report(y_test, lgbm.predict(X_test), output_dict=True)
        
        self.feature_importances = pd.DataFrame({'Feature': features, 'Importance': lgbm.feature_importances_}).sort_values(by='Importance', ascending=False)
        self.segmented_df['Churn_Probability'] = lgbm.predict_proba(self.X)[:, 1]

        # --- NEW: CALCULATE SHAP VALUES ---
        # We use the TreeExplainer for tree-based models like LightGBM
        explainer = shap.TreeExplainer(lgbm)
        # Calculate SHAP values for the positive class (Churn=1)
        self.shap_values = explainer.shap_values(self.X)[1]
        self.shap_explainer = explainer


    def generate_recommendations(self):
        """
        Generates extensive, business-focused recommendations personalized with customer data.
        """
        recommendations = []
        for _, row in self.segmented_df.iterrows():
            rec_text = ""
            if row['Segment'] == 'High-Value':
                if row['Churn_Probability'] > 0.6:
                    rec_text = f"""
                    **Segment:** High-Value Customer (At Risk)
                    - **Situation Analysis:** This is a top-tier customer showing significant churn risk. They have been inactive for **{int(row['Recency'])} days**, which is the primary risk factor. Their total call duration is **{int(row['MonetaryValue']/60)} minutes**. Losing them would be a major revenue loss.
                    - **Immediate Action:** Assign a senior retention manager for personal contact. Reference their long period of inactivity.
                    - **Business Recommendation:** Offer a significant, personalized incentive directly addressing their inactivity. **Example:** "We've noticed you haven't been active recently. To welcome you back, we're offering a 25% discount for the next 6 months and a bonus 10GB of data."
                    """
                else:
                    rec_text = f"""
                    **Segment:** High-Value Customer (Loyal)
                    - **Situation Analysis:** This is a loyal and profitable customer with **{int(row['Frequency'])} total activities** recorded. The goal is to reinforce their loyalty.
                    - **Business Recommendation:** Proactively enroll them in the company's VIP program. Offer them early access to new products. A small, unexpected gift (e.g., bonus data pack, free movie rental) can go a long way in strengthening the relationship.
                    """
            
            elif row['Segment'] == 'Medium-Value':
                if row['Churn_Probability'] > 0.5:
                    rec_text = f"""
                    **Segment:** Medium-Value Customer (At Risk)
                    - **Situation Analysis:** This customer forms the core of the business and is at risk, having been inactive for **{int(row['Recency'])} days**. Their churn could indicate a wider problem.
                    - **Business Recommendation:** Target them with a high-value upsell offer. Given their total usage of **{int(row['TotalDataMB'])} MB**, a data-focused plan would be effective. **Example:** "Get double the data for only ₹100 more per month for the next 3 months."
                    """
                else:
                    rec_text = f"""
                    **Segment:** Medium-Value Customer (Stable)
                    - **Situation Analysis:** This is a stable customer with potential for growth. Their total data usage is **{int(row['TotalDataMB'])} MB** and they've made **{int(row['TotalCalls'])} calls**.
                    - **Business Recommendation:** Analyze their specific usage to identify an upsell opportunity. If they are a heavy data user, promote data booster packs. If they make many calls, promote a plan with more minutes. The recommendation should be targeted.
                    """

            else: # Low-Value
                rec_text = f"""
                **Segment:** Low-Value Customer
                - **Situation Analysis:** This customer has low engagement and revenue, with only **{int(row['Frequency'])} total activities**. Their last activity was **{int(row['Recency'])} days** ago.
                - **Business Recommendation:** Use automated marketing campaigns. Include them in SMS blasts about new network-wide promotions or a basic "We miss you!" offer with a small data bonus to encourage re-engagement.
                """
            
            recommendations.append(rec_text)
        
        self.segmented_df['Recommendation'] = recommendations
        self.final_df = self.segmented_df
        return self.final_df

