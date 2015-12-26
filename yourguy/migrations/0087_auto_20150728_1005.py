# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0086_auto_20150727_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='app_version',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
