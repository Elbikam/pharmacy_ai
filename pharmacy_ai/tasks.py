# pharmacy_ai/celery.py
from celery import Celery
from pharmacy_ai.utils import check_reorder_levels

app = Celery('pharmacy_ai')

@app.task
def check_inventory():
    check_reorder_levels()