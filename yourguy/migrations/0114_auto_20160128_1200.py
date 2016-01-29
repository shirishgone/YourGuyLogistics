# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0113_auto_20160125_0448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryguy',
            name='area',
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=50, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'REJECTED', b'REJECTED'), (b'QUEUED', b'QUEUED'), (b'PICKUPATTEMPTED', b'PICKUPATTEMPTED'), (b'INTRANSIT', b'INTRANSIT'), (b'OUTFORDELIVERY', b'OUTFORDELIVERY'), (b'DELIVERYATTEMPTED', b'DELIVERYATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
    ]
