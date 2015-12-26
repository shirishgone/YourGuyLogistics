# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0011_auto_20150513_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='address',
            field=models.ForeignKey(related_name='consumer_address', blank=True, to='yourguy.Address', null=True),
        ),
    ]
