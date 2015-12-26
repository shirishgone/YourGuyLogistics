# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0024_auto_20150519_1228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='alternate_phone_number',
        ),
        migrations.AddField(
            model_name='vendor',
            name='phone_number',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='flat_number',
            field=models.CharField(max_length=50),
        ),
    ]
