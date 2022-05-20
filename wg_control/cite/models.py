from django.db import models
from api.models import User, Order, Referral, Tariff
# Create your models here.


class OrderRequest(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class Refiew(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    class Rates(models.IntegerChoices):
        BAD = 1
        NORMAL = 2
        GOOD = 3
        BEST = 4
        EXCELLENT = 5

    rate = models.IntegerField(choices=Rates.choices)
    description = models.TextField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

