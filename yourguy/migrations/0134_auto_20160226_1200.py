# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0133_auto_20160226_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codtransaction',
            name='deliveries',
            field=models.CommaSeparatedIntegerField(max_length=500, null=True, blank=True),
        ),
    ]
