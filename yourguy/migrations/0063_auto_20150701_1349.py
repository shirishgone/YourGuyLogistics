# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0062_auto_20150626_1228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryguy',
            name='transport_mode',
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='area',
            field=models.ForeignKey(blank=True, to='yourguy.Area', null=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='assignment_type',
            field=models.CharField(default=b'ALL', max_length=50, choices=[(b'CORPORATE', b'CORPORATE'), (b'RETAIL', b'RETAIL'), (b'ALL', b'ALL')]),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='transportation_mode',
            field=models.CharField(default=b'WALKER', max_length=50, choices=[(b'WALKER', b'WALKER'), (b'BIKER', b'BIKER'), (b'CAR_DRIVER', b'CAR_DRIVER')]),
        ),
    ]
