# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0023_remove_vendoragent_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestedvendor',
            name='alternate_phone_number',
        ),
        migrations.RemoveField(
            model_name='requestedvendor',
            name='notes',
        ),
        migrations.RemoveField(
            model_name='requestedvendor',
            name='pan_card',
        ),
        migrations.RemoveField(
            model_name='requestedvendor',
            name='verified',
        ),
        migrations.RemoveField(
            model_name='requestedvendor',
            name='website_url',
        ),
        migrations.AddField(
            model_name='requestedvendor',
            name='phone_number',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
