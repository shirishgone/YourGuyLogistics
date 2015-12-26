# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0028_auto_20150522_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='cost',
            field=models.FloatField(default=0.0),
        ),
    ]
