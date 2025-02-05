from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Product(models.Model):
    id = models.BigIntegerField(primary_key=True)
    product = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=250)
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def in_inventory(self):
        """Check if product exists in inventory"""
        return hasattr(self, 'inventory')
    @property
    def get_selling_price(self):
        return self.selling_price
    @get_selling_price.setter
    def get_selling_price(self,value):
        self.selling_price = value
        
    def get_inventory(self):
        """Safe method to retrieve inventory or None"""
        try:
            return self.inventory
        except Inventory.DoesNotExist:
            return None

    def add_to_inventory(self, initial_quantity=0, reorder_level=10):
        """Create inventory entry for product"""
        if self.in_inventory:
            raise ValidationError("Product already exists in inventory")
        return Inventory.objects.create(
            product=self,
            quantity=initial_quantity,
            reorder_level=reorder_level
        )

    def __str__(self):
        return f"{self.id} (ID: {self.product})"

class Inventory(models.Model):
    id = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        
    )
    product = models.CharField(max_length=15)
    description = models.CharField(max_length=250)
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    safety_stock = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField()
    selling_price = models.DecimalField(max_digits=10,decimal_places=2)

    @property
    def needs_restock(self):
        return self.quantity <= self.safety_stock
    @property
    def current_quantity(self):
        return self.quantity
    @current_quantity.setter
    def current_quantity(self,value):
        self.quantity = value
    

    def __str__(self):
        return f"Inventory for {self.product.name} (Qty: {self.quantity})"

class Receipt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_note = models.CharField(max_length=255)
    supplier = models.CharField(max_length=255)

    def __str__(self):
        return f"Receipt #{self.id} from {self.supplier}"

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='receiptitem_set')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    product = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    safety_stock = models.PositiveIntegerField(validators=[MinValueValidator(1)])


   

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Cost: ${self.cost_price})"