import os
from dotenv import load_dotenv
from twilio.rest import Client
from django.utils import timezone
from inventory.models import *
from notification.models import Notification


load_dotenv()

class PharmacyAIAgent:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.admin_number = os.getenv('PHARMACY_MANAGER_NUMBER')
        self.low_stock_threshold = float(os.getenv('LOW_STOCK_THRESHOLD', 0.2))

    def monitor_inventory(self):
        """Check stock levels and expiry dates daily"""
        low_stock_items = Inventory.objects.filter(
            quantity__lte=models.F('reorder_level')
        )
        
        expired_items = ReceiptItem.objects.filter(
            expiry_date__lte=timezone.now().date() + timedelta(days=7) # type: ignore
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

    def send_alert(self, message):
        """Send notification via WhatsApp and save to database"""
        # Send via Twilio
        self.twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{os.getenv("TWILIO_PHONE_NUMBER")}',
            to=f'whatsapp:{self.admin_number}'
        )
        
        # Save to database
        Notification.objects.create(
            message=message,
            phone_number=self.admin_number,
            notification_type='W'
        )

    def handle_whatsapp_command(self, command):
        """Process incoming WhatsApp commands"""
        command = command.strip().lower()
        response = ""
        
        if "inventory report" in command:
            low_stock = Inventory.objects.filter(
                quantity__lte=models.F('reorder_level')
            )
            response = "📊 Inventory Report:\n" + "\n".join(
                f"- {item.product.name}: {item.quantity} units"
                f"{' (LOW)' if item.needs_restock else ''}"
                for item in Inventory.objects.all()
            )
            
        elif "stock check" in command:
            product_name = command.replace("stock check", "").strip()
            try:
                product = Product.objects.get(name__iexact=product_name)
                inventory = product.get_inventory()
                status = inventory.quantity if inventory else "Not in inventory"
                response = f"📦 {product.name} stock: {status}"
            except Product.DoesNotExist:
                response = f"❌ Product {product_name} not found"
                
        elif "expiry alert" in command:
            expiring_soon = ReceiptItem.objects.filter(
                expiry_date__range=[
                    timezone.now().date(),
                    timezone.now().date() + timedelta(days=30) # type: ignore
                ]
            )
            response = "⚠️ Expiring Soon:\n" + "\n".join(
                f"- {item.product.name} (Exp: {item.expiry_date})"
                for item in expiring_soon
            )
            
        else:
            response = ("❌ Unrecognized command. Try:\n"
                        "- 'Inventory report'\n"
                        "- 'Stock check [product]'\n"
                        "- 'Expiry alert'")
        
        self.send_alert(response)
        return response

    def generate_demo_report(self):
        """Generate sample report for customer demo"""
        demo_data = {
            "low_stock": Inventory.objects.filter(needs_restock=True)[:3],
            "expiring_soon": ReceiptItem.objects.filter(
                expiry_date__lte=timezone.now() + timedelta(days=14) # type: ignore
            )[:3]
        }
        
        report = "📋 Demo Inventory Overview:\n"
        report += "\n🚨 Low Stock Items:\n" + "\n".join(
            f"- {item.product.name} ({item.quantity} units)"
            for item in demo_data["low_stock"]
        )
        report += "\n\n⏳ Expiring Soon:\n" + "\n".join(
            f"- {item.product.name} (Exp: {item.expiry_date})"
            for item in demo_data["expiring_soon"]
        )
        
        print("Demo Report Generated:")
        print(report)
        return report

if __name__ == "__main__":
    agent = PharmacyAIAgent()
    
    # Run demo mode
    if os.getenv('DEMO_MODE', 'False').lower() == 'true':
        agent.generate_demo_report()
    else:
        agent.monitor_inventory()