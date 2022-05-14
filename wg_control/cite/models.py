import imp
from operator import mod
from django.db import models
from api.models import User
# Create your models here.


class Reviews(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    description = models.TextField(max_length=512)
    rate = models.IntegerField()