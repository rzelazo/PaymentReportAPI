from django.db import models


class Report(models.Model):
    """
    Model for storing report jsons in the database.
    Reports are identified by the customer_id.
    """
    customer_id = models.PositiveBigIntegerField(primary_key=True)
    content = models.BinaryField()
