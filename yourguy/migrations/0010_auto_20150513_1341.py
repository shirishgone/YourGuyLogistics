# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0009_auto_20150513_1214'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='assigned_to',
            new_name='assigned_deliveryGuy',
        ),
        migrations.AddField(
            model_name='order',
            name='consumer',
            field=models.ForeignKey(blank=True, to='yourguy.Consumer', null=True),
        ),
    ]
