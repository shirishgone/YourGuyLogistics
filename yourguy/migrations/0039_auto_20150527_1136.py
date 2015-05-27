# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0038_auto_20150526_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(default=b'caller', max_length=15, choices=[(b'sales', b'sales'), (b'operations', b'operations'), (b'caller', b'caller'), (b'manager', b'manager')]),
        ),
    ]
