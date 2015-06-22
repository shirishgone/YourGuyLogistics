# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0050_auto_20150620_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgtracking',
            name='time_stamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
