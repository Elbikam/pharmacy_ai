# Corrected version
from __future__ import absolute_import
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_ai.settings')

# Create Celery application instance
app = Celery('pharmacy_ai')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()
@app.task
def monitor_inventory_task():
    from ai_agent.agent import PharmacyAIAgent
    agent = PharmacyAIAgent()
    agent.monitor_inventory()