# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0091_auto_20150922_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_collected_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_remarks',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
