# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0039_auto_20150527_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='assigned_deliveryGuy',
            field=models.ForeignKey(related_name='assinged_dg', blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
    ]
