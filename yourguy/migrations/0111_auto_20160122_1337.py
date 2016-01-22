# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0110_deliveryaction_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='delivery_id',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
    ]
