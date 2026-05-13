"""Marketplace agent category — add ecommerce lifecycle categories.

Choices are validated at the application/admin layer, not in the DB, so
this migration is metadata-only (no schema change).
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="marketplaceagent",
            name="category",
            field=models.CharField(
                choices=[
                    ("lead_management", "Lead management"),
                    ("deal_hygiene", "Deal hygiene"),
                    ("comms", "Communications"),
                    ("integrations", "Integrations"),
                    ("operations", "Operations"),
                    ("cart_recovery", "Cart recovery"),
                    ("fulfillment", "Fulfillment"),
                    ("payments", "Payments"),
                    ("customer_service", "Customer service"),
                ],
                default="operations",
                max_length=64,
            ),
        ),
    ]
