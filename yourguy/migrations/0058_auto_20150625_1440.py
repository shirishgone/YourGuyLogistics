# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0057_auto_20150625_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=15, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=15, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
    ]
