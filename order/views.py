from django.shortcuts import render
from order.models import Order,OrderItem
from inventory.models import Inventory
from django.views.generic import View
from order.forms import OrderItemForm,OrderForm,OrderItemFormset
from django.shortcuts import redirect
from django.db import transaction
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
# Create your views here.
def is_form_not_empty(form):
    return any(field.value() for field in form if field.name != 'DELETE')

def is_formset_not_empty(formset):
    return any(is_form_not_empty(form) for form in formset)

class SaleCreate(View):
    template_name = 'order/order_form.html'  # Updated template path to match actual location
    def get(self, request, *args, **kwargs):       
        order_form = OrderForm()
        orders = OrderItemFormset()

        context = {
            'order_form': order_form,
            'orders': orders,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        orders_set = OrderItemFormset(request.POST)
        
        if order_form.is_valid() and orders_set.is_valid():
            try:
                with transaction.atomic():
                    order_instance = order_form.save(commit=False)
                    order_instance.save()
                    
                    for form in orders_set:  # Renamed variable to avoid conflict
                        if is_form_not_empty(form):
                            order_item = form.save(commit=False)
                            order_item.order = order_instance  # Fixed variable reference
                            order_item.save()
                            
                            try:
                                inventory = Inventory.objects.get(product=order_item.product)
                                if order_item.quantity > inventory.current_quantity:
                                    messages.error(request, f"Insufficient quantity for {inventory.product.product_name}. Available: {inventory.current_quantity}")
                                    raise Inventory.DoesNotExist
                                
                                # Update inventory
                                inventory.current_quantity -= order_item.quantity
                                inventory.save()
                                
                            except Inventory.DoesNotExist:
                                messages.error(request, f"Product {order_item.product.product_name} not found in inventory")
                                raise
                            
                    messages.success(request, "Order created successfully!")
                    return redirect('order:orders_list')
            
            except Exception as e:
                messages.error(request, f"Error processing order: {str(e)}")
                return render(request, self.template_name, {
                    'order_form': order_form,
                    'orders': orders_set,   
                })
        
        return render(request, self.template_name, {
            'order_form': order_form,
            'orders': orders_set,   
        })
def fetch_products(request):
    product_id = request.GET.get('product_id')
    try:
        product = Inventory.objects.get(id=product_id)
        response_data = {
            'id': product.id,
            'product': product,  # Assuming you have a related Product model
            'description': product.description,  # Assuming you have a related Product model
            'selling_price': product.selling_price,
             'quantity':product.current_quantity  # Assuming you have a related Product model
        }
        return JsonResponse(response_data)
    except Inventory.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)