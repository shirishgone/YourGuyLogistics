# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0071_auto_20150709_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='rejection_reason',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='rejection_reason',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
