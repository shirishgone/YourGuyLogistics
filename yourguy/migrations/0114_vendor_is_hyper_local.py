# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0113_auto_20160125_0448'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='is_hyper_local',
            field=models.BooleanField(default=False),
        ),
    ]
