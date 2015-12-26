# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0067_auto_20150706_1147'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendoraccount',
            old_name='rates',
            new_name='pricing',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='pan_card',
        ),
        migrations.RemoveField(
            model_name='vendoraccount',
            name='balance',
        ),
        migrations.AddField(
            model_name='vendor',
            name='alternate_phone_number',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vendoraccount',
            name='billing_address',
            field=models.ForeignKey(related_name='billing_address', to='yourguy.Address', null=True),
        ),
        migrations.AddField(
            model_name='vendoraccount',
            name='pan_card',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
