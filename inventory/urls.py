from django.urls import path
from . import views
from .views import fetch_in_products, InventoryListView
app_name = "inventory"

urlpatterns = [
    path("product/create/", views.ProductView.as_view(), name="product_create"),
    path("product/list/", views.ProductListView.as_view(), name="product_list"),
    path("recipt/create/", views.ReciptView.as_view(), name="recipt_create"),
    path('fetch-products/', fetch_in_products, name='fetch_in_products'),
    path('inventory/list/', InventoryListView.as_view(), name='inventory_list'),
]

