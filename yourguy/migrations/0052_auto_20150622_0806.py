# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0051_auto_20150620_1035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dgtracking',
            name='dg',
        ),
        migrations.RenameField(
            model_name='deliveryguy',
            old_name='last_connected',
            new_name='last_connected_time',
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='latitude',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='longitude',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.DeleteModel(
            name='DGTracking',
        ),
    ]
