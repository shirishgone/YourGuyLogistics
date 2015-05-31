# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0041_auto_20150528_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.CharField(default=b'NOT_DELIVERED', max_length=15, choices=[(b'DOOR_STEP', b'DOOR_STEP'), (b'SECURITY', b'SECURITY'), (b'RECEPTION', b'RECEPTION'), (b'CUSTOMER', b'CUSTOMER'), (b'ATTEMPTED', b'ATTEMPTED'), (b'NOT_DELIVERED', b'NOT_DELIVERED')]),
        ),
    ]
