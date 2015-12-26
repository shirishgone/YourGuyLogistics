# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0004_auto_20150506_0744'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='alternate_phone_number',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='escalation_phone_number',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
