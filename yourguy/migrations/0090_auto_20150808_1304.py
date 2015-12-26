# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0089_auto_20150803_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
