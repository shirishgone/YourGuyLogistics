# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0054_auto_20150622_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='latitude',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='longitude',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
