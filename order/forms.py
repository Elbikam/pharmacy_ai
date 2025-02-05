from django import forms
from order.models import Order, OrderItem
from inventory.models import Inventory
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'expected_delivery']
        widgets = {
            'expected_delivery': forms.DateInput(attrs={'type': 'date'})
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product','product_name','description','quantity','price']
    product= forms.CharField(label="Product ID", widget=forms.TextInput(attrs={'placeholder': 'Enter Product ID'}))    

OrderItemFormset = inlineformset_factory(Order,OrderItem,
                        form=OrderItemForm,extra=1,can_delete=True)