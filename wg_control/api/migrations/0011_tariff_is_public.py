# Generated by Django 3.2.13 on 2022-05-15 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20220515_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='tariff',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]
