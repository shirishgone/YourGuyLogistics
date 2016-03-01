# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0138_auto_20160301_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='cod_status',
            field=models.CharField(max_length=100, choices=[(b'COD_NOT_AVAILABLE', b'COD_NOT_AVAILABLE'), (b'COD_COLLECTED', b'COD_COLLECTED'), (b'COD_TRANSFERRED_TO_TL', b'COD_TRANSFERRED_TO_TL'), (b'COD_BANK_DEPOSITED', b'COD_BANK_DEPOSITED'), (b'COD_VERIFIED', b'COD_VERIFIED'), (b'COD_TRANSFERRED_TO_CLIENT', b'COD_TRANSFERRED_TO_CLIENT')]),
        ),
    ]
