# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0098_auto_20151120_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='order_id_in_order_table',
            field=models.IntegerField(default=0),
        ),
    ]
