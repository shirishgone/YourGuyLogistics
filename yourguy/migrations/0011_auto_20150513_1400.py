# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0010_auto_20150513_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='address',
            field=models.ForeignKey(related_name='dg_home_address', blank=True, to='yourguy.Address', null=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='assigned_area',
            field=models.ForeignKey(related_name='assigned_area', default=0, blank=True, to='yourguy.Area', null=True),
        ),
        migrations.AlterField(
            model_name='dgattendance',
            name='login_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dgattendance',
            name='logout_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
