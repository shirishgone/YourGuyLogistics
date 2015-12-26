# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0045_order_is_recurring'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderDeliveryStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('pickedup_datetime', models.DateTimeField()),
                ('completed_datetime', models.DateTimeField()),
                ('order_status', models.CharField(default=b'QUEUED', max_length=15, choices=[(b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')])),
                ('delivered_at', models.CharField(default=b'NOT_DELIVERED', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'ATTEMPTED', b'ATTEMPTED'), (b'NOT_DELIVERED', b'NOT_DELIVERED')])),
                ('delivery_guy', models.ForeignKey(related_name='assigned_dg', blank=True, to='yourguy.DeliveryGuy', null=True)),
                ('order', models.ForeignKey(to='yourguy.Order')),
            ],
        ),
    ]
