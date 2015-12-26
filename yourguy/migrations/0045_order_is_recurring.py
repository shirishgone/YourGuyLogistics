# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0044_auto_20150602_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_recurring',
            field=models.BooleanField(default=False),
        ),
    ]
