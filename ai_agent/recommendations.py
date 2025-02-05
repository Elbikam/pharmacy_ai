import pandas as pd
from datetime import datetime, timedelta

class PharmacyRecommender:
    def __init__(self, inventory_df: pd.DataFrame):
        self.inventory = inventory_df
        self.today = datetime.today()
    
    def generate_recommendations(self):
        """Combine multiple recommendation types"""
        recs = []
        
        # Low stock alerts
        recs.extend(self._low_stock_recommendations())
        
        # Expiry alerts
        recs.extend(self._expiry_recommendations())
        
        # Seasonal demand
        recs.extend(self._seasonal_recommendations())
        
        return pd.DataFrame(recs)

    def _low_stock_recommendations(self):
        """Items below safety stock level"""
        low_stock = self.inventory[
            self.inventory.current_stock < self.inventory.safety_stock
        ]
        return [{
            'type': 'low_stock',
            'medication': row['name'],
            'message': f"Reorder {row['name']} (Stock: {row['current_stock']}, Safety: {row['safety_stock']})",
            'urgency': 'high'
        } for _, row in low_stock.iterrows()]

    def _expiry_recommendations(self):
        """Items expiring within 30 days"""
        expiry_threshold = self.today + timedelta(days=30)
        expiring = self.inventory[
            pd.to_datetime(self.inventory.expiry_date) <= expiry_threshold
        ]
        return [{
            'type': 'expiring',
            'medication': row['name'],
            'message': f"Discount {row['name']} (Expires: {row['expiry_date']})",
            'urgency': 'medium'
        } for _, row in expiring.iterrows()]

    def _seasonal_recommendations(self):
        """Seasonal demand predictions"""
        # Integrate with forecasting model
        return [{
            'type': 'seasonal',
            'medication': 'Antihistamines',
            'message': "Increase stock for allergy season",
            'urgency': 'medium'
        }]