# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0016_auto_20150515_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='phone_number',
            field=models.CharField(unique=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='phone_number',
            field=models.CharField(unique=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='employee',
            name='phone_number',
            field=models.CharField(unique=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='phone_number',
            field=models.CharField(unique=True, max_length=15),
        ),
    ]
