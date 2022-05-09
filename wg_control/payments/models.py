from django.db import models


class Payment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    tariff = models.ForeignKey( 
        'api.Tariff',
        on_delete=models.SET_NULL,
        null=True
    )
    user = models.ForeignKey(
        'api.User',
        related_name='payment',
        on_delete=models.SET_NULL,
        null=True
    )
    credits_amount = models.BigIntegerField()
    is_refund = models.BooleanField(default=False)