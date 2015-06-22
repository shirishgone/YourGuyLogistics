# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0052_auto_20150622_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='last_connected_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
