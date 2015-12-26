# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0072_auto_20150709_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='shift_end_datetime',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='shift_start_datetime',
            field=models.TimeField(null=True, blank=True),
        ),
    ]
