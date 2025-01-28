# Generated by Django 5.1.5 on 2025-01-28 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField()),
                ("phone_number", models.CharField(max_length=15)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
