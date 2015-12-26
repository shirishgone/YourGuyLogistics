# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0013_auto_20150514_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='area_code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='address',
            name='mini_address',
            field=models.CharField(max_length=250),
        ),
    ]
