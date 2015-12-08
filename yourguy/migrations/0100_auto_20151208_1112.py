# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0099_orderdeliverystatus_order_id_in_order_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='delivery_status',
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='order',
            field=models.ForeignKey(related_name='order', blank=True, to='yourguy.Order', null=True),
        ),
    ]
