# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0130_auto_20160225_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='codtransaction',
            name='deliveries',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
