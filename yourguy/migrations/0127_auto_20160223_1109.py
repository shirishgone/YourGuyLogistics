# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0126_orderdeliverystatus_cod_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.CODTransaction', null=True),
        ),
    ]
