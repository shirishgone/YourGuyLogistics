# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0007_auto_20150513_0854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='address',
            field=models.ForeignKey(related_name='vendor_address', blank=True, to='yourguy.Address', null=True),
        ),
    ]
