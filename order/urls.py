from django.urls import path
from . import views
from .views import SaleCreate #fetch_products

app_name = "order"

urlpatterns = [
    path("order/create/", views.SaleCreate.as_view(), name="order_create"),  # Added trailing slash and improved name consistency
    # path('fetch-products/', fetch_products, name='fetch_products'),
]