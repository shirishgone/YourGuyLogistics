# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0017_auto_20150515_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=15, choices=[(b'QUEUED', b'Queued'), (b'INTRANSIT', b'InTransit'), (b'DELIVERED', b'Delivered')]),
        ),
    ]
