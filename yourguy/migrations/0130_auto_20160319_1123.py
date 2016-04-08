# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0129_auto_20160314_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='codtransaction',
            name='utr_number',
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Vendor', null=True),
        ),
    ]
