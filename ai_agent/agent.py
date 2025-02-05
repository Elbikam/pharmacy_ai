import os
from dotenv import load_dotenv
from twilio.rest import Client
from django.utils import timezone
from inventory.models import Inventory, Product
from inventory.models import *
from datetime import timedelta 
import pandas as pd
load_dotenv()
from .forecasting import DemandForecaster
from .recommendations import PharmacyRecommender
from .anomalies import AnomalyDetector
from .trends import TrendAnalyzer
from django.db.models import Sum 
from .drug_processing import DrugQueryProcessor



class PharmacyAIAgent:
    def __init__(self, inventory_df: pd.DataFrame=None):
        if inventory_df is None:
            inventory_df = self.load_inventory_data()
        self.drug_processor = DrugQueryProcessor()    
        self.forecaster = DemandForecaster()
        self.recommender = PharmacyRecommender(inventory_df)
        self.detector = AnomalyDetector()
        self.analyzer = TrendAnalyzer()
        self.client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        self.from_whatsapp = f'whatsapp:{os.getenv("TWILIO_PHONE_NUMBER")}'
        self.to_whatsapp = f'whatsapp:{os.getenv("PHARMACY_MANAGER_NUMBER")}'
    @staticmethod
    def load_inventory_data():
        """Load inventory data from database"""
        return pd.DataFrame.from_records(
            Inventory.objects.all().values(
                'id', 
                'product',
                'quantity',
                'safety_stock',
                'expiry_date',
                'selling_price'
            )
        )
    
    def send_test_message(self):
        """Basic message verification"""
        message = self.client.messages.create(
            body='🚨 TEST: Pharmacy AI Connection Working',
            from_=self.from_whatsapp,
            to=self.to_whatsapp
        )
        return message.sid
    
    
    
    def monitor_inventory(self):
        """Check stock levels and expiry dates daily"""
        low_stock_items = Inventory.objects.filter(
            quantity__lte=models.F('reorder_level')
        )
        
        expired_items = ReceiptItem.objects.filter(
            expiry_date__lte=timezone.now().date() + timedelta(days=7)
        )

        if low_stock_items.exists() or expired_items.exists():
            message = "🔔 Pharmacy Inventory Alert:\n"
            
            if low_stock_items.exists():
                message += "\nLow Stock:\n" + "\n".join(
                    f"- {item.product.name} ({item.quantity} left)"
                    for item in low_stock_items
                )
            
            if expired_items.exists():
                message += "\nExpiring Soon:\n" + "\n".join(
                    f"- {item.product.name} (Exp: {item.expiry_date})"
                    for item in expired_items
                )
            
            self.send_alert(message)

    def send_alert(self, message: str):
        """Simplified version that works like test_message"""
        return self.client.messages.create(
            body=message,  # Use body instead of template
            from_=self.from_whatsapp,
            to=self.to_whatsapp,
            
        )
    
  
    
    
    def handle_whatsapp_message(self, message, from_number):
        message = message.lower()
        if "paracetamol" in message:
            return "Yes! Paracetamol 500mg tablets are available. 🟢"
        return "Please inquire about specific medications. 🔴"
        
        
                    
            
    

if __name__ == "__main__":
    # Create agent with auto-generated inventory DF
    agent = PharmacyAIAgent.from_inventory()
    
    # Rest of main code remains the same
    if os.getenv('DEMO_MODE', 'False').lower() == 'true':
        agent.generate_demo_report()
    else:
        agent.monitor_inventory()