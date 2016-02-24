# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0124_auto_20160223_0739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdeliverystatus',
            name='cod_status',
        ),
    ]
