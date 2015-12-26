# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0015_auto_20150515_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='building',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='address',
            name='flat_number',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=100),
        ),
    ]
