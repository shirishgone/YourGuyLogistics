# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0018_auto_20150516_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='availability',
            field=models.CharField(default=b'AVAILABLE', max_length=15, choices=[(b'AVAILABLE', b'AVAILABLE'), (b'BUSY', b'BUSY')]),
        ),
        migrations.AlterField(
            model_name='dgattendance',
            name='status',
            field=models.CharField(default=b'UNKNOWN', max_length=15, choices=[(b'LEAVE', b'LEAVE'), (b'WORKING', b'WORKING'), (b'UNKNOWN', b'UNKNOWN')]),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(default=b'CALLER', max_length=15, choices=[(b'SALES', b'SALES'), (b'OPERATIONS', b'OPERATIONS'), (b'CALLER', b'CALLER'), (b'MANAGER', b'MANAGER')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=15, choices=[(b'QUEUED', b'QUEUED'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
    ]
