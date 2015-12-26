# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0096_deliveryguy_employee_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=50, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'REJECTED', b'REJECTED'), (b'QUEUED', b'QUEUED'), (b'PICKUPATTEMPTED', b'PICKUPATTEMPTED'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERYATTEMPTED', b'DELIVERYATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=50, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'REJECTED', b'REJECTED'), (b'QUEUED', b'QUEUED'), (b'PICKUPATTEMPTED', b'PICKUPATTEMPTED'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERYATTEMPTED', b'DELIVERYATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
    ]
