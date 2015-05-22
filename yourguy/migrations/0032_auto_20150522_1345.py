# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0031_auto_20150522_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='consumer',
            field=models.ForeignKey(to='yourguy.Consumer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(to='yourguy.Vendor'),
        ),
    ]
