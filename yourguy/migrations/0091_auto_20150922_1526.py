# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0090_auto_20150808_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='vendor_order_id',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
