# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0035_auto_20150525_1351'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consumer',
            old_name='address',
            new_name='addresses',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='address',
        ),
        migrations.AddField(
            model_name='vendor',
            name='addresses',
            field=models.ManyToManyField(to='yourguy.Address'),
        ),
    ]
