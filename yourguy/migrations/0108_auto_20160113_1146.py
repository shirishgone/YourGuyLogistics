# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0107_product_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='associate_delivery_guys',
            field=models.ManyToManyField(related_name='ops_associate_delivery_guys', to='yourguy.DeliveryGuy', blank=True),
        ),
    ]
