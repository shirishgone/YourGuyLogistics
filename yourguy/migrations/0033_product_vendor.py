# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0032_auto_20150522_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(blank=True, to='yourguy.Vendor', null=True),
        ),
    ]
