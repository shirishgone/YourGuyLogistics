# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0030_auto_20150522_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='address',
            field=models.ManyToManyField(to='yourguy.Address'),
        ),
    ]
