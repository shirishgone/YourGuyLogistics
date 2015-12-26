# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0075_auto_20150713_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='capacity',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='current_load',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='status',
            field=models.CharField(default=b'UN_AVAILABLE', max_length=50, choices=[(b'UN_AVAILABLE', b'UN_AVAILABLE'), (b'AVAILABLE', b'AVAILABLE'), (b'BUSY', b'BUSY')]),
        ),
    ]
