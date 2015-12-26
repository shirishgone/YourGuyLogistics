# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0065_auto_20150703_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.CharField(default=b'NOT_DELIVERED', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'NOT_DELIVERED', b'NOT_DELIVERED')]),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivered_at',
            field=models.CharField(default=b'NOT_DELIVERED', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'NOT_DELIVERED', b'NOT_DELIVERED')]),
        ),
    ]
