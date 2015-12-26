# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0078_area_pin_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='account',
            field=models.ForeignKey(related_name='account', blank=True, to='yourguy.VendorAccount', null=True),
        ),
    ]
