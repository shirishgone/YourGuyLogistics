# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0131_codtransaction_deliveries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codtransaction',
            name='deliveries',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
