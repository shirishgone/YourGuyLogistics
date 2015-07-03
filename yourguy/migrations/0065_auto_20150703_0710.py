# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0064_auto_20150703_0658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=15, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'ATTEMPTED', b'ATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=15, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'ATTEMPTED', b'ATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
    ]
