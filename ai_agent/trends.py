from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
class TrendAnalyzer:
    def analyze(self, sales_data: pd.DataFrame, period: int = 30):
        """Decompose sales trends"""
        result = seasonal_decompose(
            sales_data.set_index('date')['quantity'], 
            period=period
        )
        return {
            'trend': result.trend,
            'seasonal': result.seasonal,
            'residual': result.resid
        }