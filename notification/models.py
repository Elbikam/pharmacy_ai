from django.db import models

# Create your models here.
from django.db import models

class Notification(models.Model):
    message = models.TextField()
    phone_number = models.CharField(max_length=15)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.phone_number}"