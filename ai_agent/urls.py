from django.urls import path
from . import views
from .views import WhatsAppWebhook
app_name="ai_agent "

urlpatterns = [
   
    path('whatsapp-webhook/', WhatsAppWebhook, name='whatsapp_webhook'),
   
]