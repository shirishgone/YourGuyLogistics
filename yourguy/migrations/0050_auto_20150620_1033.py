# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0049_auto_20150620_0645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgtracking',
            name='time_stamp',
            field=models.DateTimeField(),
        ),
    ]
