# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0047_auto_20150618_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdeliverystatus',
            name='order',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_status',
            field=models.ManyToManyField(to='yourguy.OrderDeliveryStatus'),
        ),
    ]
