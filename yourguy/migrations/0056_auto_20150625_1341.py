# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0055_remove_order_recurring_rule'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='transport_mode',
            field=models.CharField(default=b'PUBLIC_TRANSPORT', max_length=20, choices=[(b'PUBLIC_TRANSPORT', b'PUBLIC_TRANSPORT'), (b'NON_AC_VEHICLE', b'NON_AC_VEHICLE'), (b'AC_VEHICLE', b'AC_VEHICLE'), (b'BIKE', b'BIKE')]),
        ),
        migrations.AddField(
            model_name='order',
            name='transport_mode',
            field=models.CharField(default=b'PUBLIC_TRANSPORT', max_length=20, choices=[(b'PUBLIC_TRANSPORT', b'PUBLIC_TRANSPORT'), (b'NON_AC_VEHICLE', b'NON_AC_VEHICLE'), (b'AC_VEHICLE', b'AC_VEHICLE'), (b'BIKE', b'BIKE')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=20, choices=[(b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order_status',
            field=models.CharField(default=b'ORDER_PLACED', max_length=20, choices=[(b'ORDER_PLACED', b'ORDER_PLACED'), (b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
    ]
