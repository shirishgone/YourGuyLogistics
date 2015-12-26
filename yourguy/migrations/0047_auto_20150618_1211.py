# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0046_orderdeliverystatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='completed_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='pickedup_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
