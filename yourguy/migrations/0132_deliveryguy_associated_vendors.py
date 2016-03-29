# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0131_auto_20160319_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='associated_vendors',
            field=models.ManyToManyField(related_name='associated_vendors', to='yourguy.Vendor', blank=True),
        ),
    ]
