from sklearn.ensemble import IsolationForest
import pandas as pd
class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05)
    
    def detect(self, sales_data: pd.DataFrame):
        """Identify unusual sales patterns"""
        features = sales_data[['quantity', 'day_of_week', 'month']]
        anomalies = self.model.fit_predict(features)
        return sales_data[anomalies == -1]