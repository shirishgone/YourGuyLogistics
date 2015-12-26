# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0076_auto_20150716_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='capacity',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='current_load',
            field=models.IntegerField(default=0),
        ),
    ]
