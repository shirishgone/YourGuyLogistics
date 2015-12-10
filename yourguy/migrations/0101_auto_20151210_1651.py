# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0100_auto_20151208_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='reported_reason',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='reported_solution',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
