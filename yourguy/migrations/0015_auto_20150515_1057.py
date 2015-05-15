# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0014_auto_20150514_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='mini_address',
        ),
        migrations.AddField(
            model_name='address',
            name='building',
            field=models.CharField(default=b'NONE', max_length=100),
        ),
        migrations.AddField(
            model_name='address',
            name='flat_number',
            field=models.CharField(default=b'NONE', max_length=10),
        ),
        migrations.AddField(
            model_name='address',
            name='latitude',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='longitude',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AddField(
            model_name='address',
            name='street',
            field=models.CharField(default=b'NONE', max_length=100),
        ),
    ]
