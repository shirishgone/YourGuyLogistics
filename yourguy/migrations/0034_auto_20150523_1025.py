# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0033_product_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='area_code',
        ),
        migrations.AddField(
            model_name='address',
            name='area',
            field=models.ForeignKey(blank=True, to='yourguy.Area', null=True),
        ),
    ]
