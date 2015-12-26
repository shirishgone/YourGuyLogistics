# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0060_auto_20150626_0700'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cod_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='order',
            name='is_reverse_pickup',
            field=models.BooleanField(default=False),
        ),
    ]
