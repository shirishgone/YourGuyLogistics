# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0087_auto_20150728_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='url',
            field=models.CharField(max_length=250, blank=True),
        ),
    ]
