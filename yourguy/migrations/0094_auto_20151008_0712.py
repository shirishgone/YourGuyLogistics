# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0093_address_full_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.CharField(default=b'NONE', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'NONE', b'NONE')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=50, choices=[(b'QUEUED', b'QUEUED'), (b'PICKUPATTEMPTED', b'PICKUPATTEMPTED'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERYATTEMPTED', b'DELIVERYATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivered_at',
            field=models.CharField(default=b'NONE', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'NONE', b'NONE')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=50, choices=[(b'QUEUED', b'QUEUED'), (b'PICKUPATTEMPTED', b'PICKUPATTEMPTED'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERYATTEMPTED', b'DELIVERYATTEMPTED'), (b'DELIVERED', b'DELIVERED'), (b'CANCELLED', b'CANCELLED')]),
        ),
    ]
