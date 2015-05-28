# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0040_auto_20150527_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'QUEUED', max_length=15, choices=[(b'QUEUED', b'QUEUED'), (b'OUTFORPICKUP', b'OUTFORPICKUP'), (b'INTRANSIT', b'INTRANSIT'), (b'DELIVERED', b'DELIVERED')]),
        ),
    ]
