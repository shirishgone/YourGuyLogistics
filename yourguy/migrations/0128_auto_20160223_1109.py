# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0127_auto_20160223_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
            field=models.ManyToManyField(to='yourguy.CODTransaction', blank=True),
        ),
    ]
