from django.db import models
from inventory.models import Inventory

# Create your models here.
class Order(models.Model):
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order {self.id} on {self.date}"

class LineItem(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Line Item {self.id} on {self.created_at}"
    class Meta:
        abstract = True

class OrderItem(LineItem):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    def __str__(self):
        return f"Order Item {self.id} on {self.created_at}"
   
    