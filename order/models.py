from django.db import models
from inventory.models import Inventory
from django.core.validators import EmailValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta 
from django.db.models import Avg, Count
from ai_agent.agent import PharmacyAIAgent
# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('placed', 'Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    expected_delivery = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    ai_notes = models.TextField(
        blank=True,
        help_text="AI-generated order insights"
    )
    def generate_ai_notes(self):
        """Generate AI insights for this order"""
        from ai_agent.agent import PharmacyAIAgent  # Avoid circular import
        agent = PharmacyAIAgent()
        
        notes = [
            "📊 Order Insights:",
            f"- Total Items: {self.items.count()}",
            f"- Predicted Delivery Risk: {self._calculate_delivery_risk()}"
        ]
        
        # Add inventory checks
        for item in self.items.all():
            inventory = item.product
            if inventory.days_of_stock < 7:
                notes.append(f"⚠️ Low stock after order: {inventory.product.name}")
        
        self.ai_notes = '\n'.join(notes)
        self.save()
    
    def _calculate_delivery_risk(self):
        """Predict delivery success probability"""
        # Placeholder for ML model integration
        return "Low Risk"  # Replace with actual prediction
    def __str__(self):
        return f"Order {self.id} on {self.date}"

class LineItem(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=15,blank=True)
    description = models.CharField(max_length=250,blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Line Item {self.id} on {self.created_at}"
    class Meta:
        abstract = True

class OrderItem(LineItem):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    @property
    def total_price(self):
        return (self.unit_price * self.quantity) - self.discount
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    def __str__(self):
        return f"Order Item {self.id} on {self.created_at}"
   
class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    address = models.TextField()
    lead_time = models.PositiveIntegerField(
        help_text="Average delivery time in days",
        default=7
    )
    reliability_score = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    preferred = models.BooleanField(
        default=False,
        help_text="Mark as preferred supplier"
    )
    @classmethod
    def recommend_suppliers(cls, product):
        """AI-powered supplier recommendations"""
        agent = PharmacyAIAgent()
        
        # Base queryset
        queryset = cls.objects.annotate(
            avg_lead=Avg('orders__items__unit_cost'),
            total_orders=Count('orders')
        ).filter(
            orders__items__product=product
        )
        
        # Get AI-enhanced scores
        return agent.rank_suppliers(queryset, product)
    
    def ai_score(self):
        """Calculate AI performance score"""
        from ai_agent.agent import PharmacyAIAgent
        agent = PharmacyAIAgent()
        return agent.calculate_supplier_score(self)
    def __str__(self):
        return f"{self.name} ({'⭐' if self.preferred else ''})"  
class PurchaseOrder(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent to Supplier'),
            ('confirmed', 'Confirmed'),
            ('shipped', 'Shipped'),
            ('received', 'Received'),
            ('cancelled', 'Cancelled')
        ],
        default='draft'
    )
    tracking_number = models.CharField(max_length=255, blank=True)
    ai_notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        """Auto-calculate expected delivery date"""
        if not self.expected_delivery:
            self.expected_delivery = self.order_date + timedelta(
                days=self.supplier.lead_time
            )
        super().save(*args, **kwargs)   

class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_cost(self):
        return self.quantity * self.unit_cost    



class SupplierPerformance(models.Model):
    supplier = models.OneToOneField(
        Supplier,
        on_delete=models.CASCADE,
        primary_key=True
    )
    on_time_deliveries = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    quality_issues = models.PositiveIntegerField(default=0)
    
    @property
    def on_time_percentage(self):
        if self.total_orders == 0:
            return 0.0
        return (self.on_time_deliveries / self.total_orders) * 100
    
    def update_performance(self, on_time=True, quality_issue=False):
        self.total_orders += 1
        if on_time:
            self.on_time_deliveries += 1
        if quality_issue:
            self.quality_issues += 1
        self.save()