# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0058_auto_20150625_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='is_retail',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.CharField(default=b'UNKNOWN', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'ATTEMPTED', b'ATTEMPTED'), (b'UNKNOWN', b'UNKNOWN')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivered_at',
            field=models.CharField(default=b'UNKNOWN', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'ATTEMPTED', b'ATTEMPTED'), (b'UNKNOWN', b'UNKNOWN')]),
        ),
    ]
