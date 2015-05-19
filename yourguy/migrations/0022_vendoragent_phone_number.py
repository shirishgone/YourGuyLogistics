# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0021_auto_20150519_0747'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendoragent',
            name='phone_number',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
