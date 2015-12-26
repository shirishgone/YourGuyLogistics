# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0039_auto_20150527_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='assigned_deliveryGuy',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_guy',
            field=models.ForeignKey(related_name='delivery_guy', blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
    ]
