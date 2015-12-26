# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0037_auto_20150525_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='city_name',
            field=models.CharField(default=b'MUMBAI', max_length=100),
        ),
        migrations.AlterField(
            model_name='area',
            name='area_code',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
