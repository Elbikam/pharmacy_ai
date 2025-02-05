import stanza
import logging
from django.db.models import Sum, Q
from django.utils import timezone
from inventory.models import Product, Inventory, ReceiptItem





class DrugQueryProcessor:
    def __init__(self):
        # Consider using smaller models for faster loading
        import stanza
        self.nlp = stanza.Pipeline(
            lang='en',
            package='combined',  # Try 'default' for smaller footprint
            processors='tokenize,ner',  # Remove mwt if not needed
            verbose=False  # Reduces console output
        )
        
    def extract_drug_name(self, text: str) -> str:
        """Extract medication names using NLP"""
        doc = self.nlp(text)
        for sentence in doc.sentences:
            for ent in sentence.ents:
                if ent.type == 'DRUG':
                    return ent.text.lower()
        return None

    def check_inventory(self, drug_name: str) -> tuple:
        """Check product availability in inventory"""
        try:
            product = Inventory.objects.get(
                Q(product__iexact=drug_name) |
                Q(description__icontains=drug_name)
            )
            
            return (product, product.current_quantity if product else 0)
        except Inventory.DoesNotExist:
            return (None, 0)

    def process_message(self, message: str) -> str:
        """Main processing method for drug inquiries"""
        drug_name = self.extract_drug_name(message)
        if not drug_name:
            return "Could not identify medication in your message. Please provide the exact drug name."
            
        product, quantity = self.check_inventory(drug_name)
        
        if not product:
            return f"❌ {drug_name.capitalize()} is not currently available in our inventory."
            
        return (f"✅ {drug_name.capitalize()} is available!\n"
                f"Current stock: {quantity} units\n"
                f"Price: ${product.selling_price}")
    