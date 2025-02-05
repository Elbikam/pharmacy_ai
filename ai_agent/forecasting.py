import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error

class DemandForecaster:
    def __init__(self):
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
    
    def train(self, historical_data: pd.DataFrame):
        """Train on historical sales data"""
        df = historical_data.rename(columns={
            'date': 'ds',
            'quantity_sold': 'y'
        })
        self.model.fit(df)
    
    def predict(self, days: int = 7) -> pd.DataFrame:
        """Generate forecast for next X days"""
        future = self.model.make_future_dataframe(periods=days)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][-days:]
    
    def evaluate(self, test_data: pd.DataFrame) -> float:
        """Calculate MAE on test set"""
        forecast = self.predict(len(test_data))
        return mean_absolute_error(test_data['quantity_sold'], forecast['yhat'])