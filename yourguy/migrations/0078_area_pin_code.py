# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0077_auto_20150717_0844'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='pin_code',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
