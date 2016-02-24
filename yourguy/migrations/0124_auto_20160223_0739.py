# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0123_auto_20160223_0615'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_status',
            field=models.CharField(default=b'COD_PENDING', max_length=100, choices=[(b'COD_PENDING', b'COD_PENDING'), (b'COD_COLLECTED', b'COD_COLLECTED'), (b'COD_TRANSFERRED_TO_TL', b'COD_TRANSFERRED_TO_TL'), (b'COD_BANK_DEPOSITED', b'COD_BANK_DEPOSITED'), (b'COD_VERIFIED', b'COD_VERIFIED'), (b'COD_TRANSFERRED_TO_CLIENT', b'COD_TRANSFERRED_TO_CLIENT'), (b'COD_CLOSED', b'COD_CLOSED')]),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
            field=models.ManyToManyField(to='yourguy.CODTransaction', blank=True),
        ),
    ]
