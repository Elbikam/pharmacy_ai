from django import forms
from inventory.models import Product, Receipt, ReceiptItem
from django.forms import inlineformset_factory, ModelForm
from django.core.exceptions import ValidationError
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['id','product', 'description', 'selling_price']

class ReciptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['delivery_note']

class ReciptItemForm(forms.ModelForm):
    class Meta:
        model = ReceiptItem
        fields = ['product_id','product','description',
                'cost_price', 'quantity', 'selling_price',
                'expiry_date','safety_stock']
    
    product_id = forms.CharField(label="Product ID", widget=forms.TextInput(attrs={'placeholder': 'Enter Product ID'}))

    def clean_product_id(self):
        # Corrected from self.clean to self.cleaned_data
        item_id = self.cleaned_data['product_id']
        try:
            # Return the Product instance instead of just validating
            product = Product.objects.get(id=item_id)
            return product  # This will assign the Product instance to the ForeignKey
        except Product.DoesNotExist:
            raise ValidationError("Invalid product ID. Please enter a valid ID.")

ReceiptItemFormSet = inlineformset_factory(
    Receipt, ReceiptItem, form=ReciptItemForm, extra=1, can_delete=True
)