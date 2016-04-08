# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0130_auto_20160319_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proofofbankdeposit',
            name='receipt_number',
            field=models.CharField(max_length=100),
        ),
    ]
