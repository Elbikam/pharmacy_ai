from django import forms
from inventory.models import Product, Receipt, ReceiptItem
from django.forms import inlineformset_factory, ModelForm
from django.core.exceptions import ValidationError
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','name', 'description', 'selling_price']

class ReciptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['delivery_note']

class ReciptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItem
        fields = ['product', 'product_name', 'description','cost_price', 'quantity', 'selling_price','reorder_level']
    product= forms.CharField(label="Product ID", widget=forms.TextInput(attrs={'placeholder': 'Enter Product ID'}))
    def clean_product(self):
        product = self.cleaned_data['product']
        try:
            return Product.objects.get(id=product)  # Fetch the Item instance based on the ID
        except Product.DoesNotExist:
            raise ValidationError("Invalid product ID. Please enter a valid ID.")

ReceiptItemFormSet = inlineformset_factory(
    Receipt, ReceiptItem, form=ReciptItemForm, extra=1, can_delete=True
)