# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0079_auto_20150720_0646'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cod_collected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_charges',
            field=models.FloatField(default=0.0),
        ),
    ]
