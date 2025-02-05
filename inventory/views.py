from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from inventory.models import *
from inventory.forms import ProductForm, ReciptForm, ReciptItemForm, ReceiptItemFormSet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.db import transaction
from django.contrib import messages
# Create your views here.
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)

class ProductView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')
class ProductListView(ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'

class ReciptView(CreateView):
    template_name = 'inventory/recipt_form.html'
    success_url = reverse_lazy('inventory:recipt_list')

    def get(self, request, *args, **kwargs):
        receipt_form = ReciptForm()
        receiptitem_set = ReceiptItemFormSet()
        return render(request, self.template_name, {
            'receipt_form': receipt_form,
            'receiptitem_set': receiptitem_set,
        })

    
    def post(self, request, *args, **kwargs):
        receipt_form = ReciptForm(request.POST)
        receiptitem_set = ReceiptItemFormSet(request.POST)
        if receipt_form.is_valid() and receiptitem_set.is_valid():
            with transaction.atomic():
                receipt_form=receipt_form.save(commit=False)
                receipt_form.save()
                for receiptitem in receiptitem_set:
                    if is_form_not_empty(receiptitem):
                        receiptitem_form = receiptitem.save(commit=False)
                        receiptitem_form.receipt = receipt_form
                        receiptitem_form.save()
                      
                        #update price 
                        product=Product.objects.get(id=receiptitem_form.product_id.id)
                        product.get_selling_price = receiptitem_form.selling_price
                        product.save()
                        #update inventory
                        try:
                            #if product in Inventory update quantity of product
                            inventory = Inventory.objects.get(product=receiptitem_form.product_id.id)
                            inventory.current_quantity += receiptitem_form.quantity
                            inventory.save()
                        except Inventory.DoesNotExist:
                            #if product not in Inventory create new inventory
                            product_fk = Product.objects.get(id=receiptitem_form.product_id.id)
                            inventory = Inventory.objects.create(id=product_fk,product=product_fk.product ,quantity=receiptitem_form.quantity,
                                        selling_price=receiptitem_form.selling_price,expiry_date=receiptitem_form.expiry_date,
                                        safety_stock=receiptitem_form.safety_stock)
                            inventory.save()
                        

            return redirect('inventory:inventory_list')
        return render(request, self.template_name, {
            'receipt_form': receipt_form,
            'receiptitem_set': receiptitem_set,   
        })

def fetch_in_products(request):
    product_id = request.GET.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
        response_data = {
            'id': product.id,
            'product': product.product,  # Assuming you have a related Product model
            'description': product.description,  # Assuming you have a related Product model
            'selling_price': product.selling_price,  # Assuming you have a related Product model
        }
        return JsonResponse(response_data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)
    
class InventoryListView(ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'products'
