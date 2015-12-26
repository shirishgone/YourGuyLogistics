# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0012_auto_20150514_0816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='area',
        ),
        migrations.RemoveField(
            model_name='address',
            name='building_name',
        ),
        migrations.RemoveField(
            model_name='address',
            name='flat_number',
        ),
        migrations.RemoveField(
            model_name='address',
            name='floor_number',
        ),
        migrations.RemoveField(
            model_name='address',
            name='road',
        ),
        migrations.RemoveField(
            model_name='address',
            name='wing',
        ),
        migrations.AddField(
            model_name='address',
            name='area_code',
            field=models.CharField(default=b'NA', max_length=10),
        ),
        migrations.AddField(
            model_name='address',
            name='mini_address',
            field=models.CharField(default=b'NA', max_length=250),
        ),
    ]
