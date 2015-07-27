# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0085_auto_20150727_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumer',
            name='profile_picture',
            field=models.ForeignKey(blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='profile_picture',
            field=models.ForeignKey(blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='profile_picture',
            field=models.ForeignKey(blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AddField(
            model_name='vendoragent',
            name='profile_picture',
            field=models.ForeignKey(blank=True, to='yourguy.Picture', null=True),
        ),
    ]
