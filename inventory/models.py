from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def get_price(self):
        return self.selling_price 
    @get_price.setter
    def get_price(self,value):
        self.selling_price = value
    def __str__(self):
        return f"{self.name} (ID: {self.id})"

class Receipt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_note = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.pk} {self.delivery_note} - {self.created_at.strftime('%Y-%m-%d')}"

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity}) - {self.price} for {self.receipt}"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, blank=True, primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def current_quantity(self):
        return self.quantity
    
    @current_quantity.setter
    def current_quantity(self, value):
        self.quantity = value

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    
