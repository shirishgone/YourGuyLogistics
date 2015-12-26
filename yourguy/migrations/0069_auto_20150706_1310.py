# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0068_auto_20150706_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendoraccount',
            name='pan_card',
        ),
        migrations.AddField(
            model_name='vendoraccount',
            name='pan',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
