# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0092_auto_20150922_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='full_address',
            field=models.CharField(default=b'-', max_length=500),
        ),
    ]
