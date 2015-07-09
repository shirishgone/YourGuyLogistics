# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0070_auto_20150706_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=50, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'REJECTED', b'REJECTED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'OUTFORDELIVERY', b'OUTFORDELIVERY'), (b'ATTEMPTED', b'ATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=50, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'REJECTED', b'REJECTED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'OUTFORDELIVERY', b'OUTFORDELIVERY'), (b'ATTEMPTED', b'ATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
    ]
