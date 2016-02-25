# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0129_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='codtransaction',
            name='cod_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='dg_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='dg_tl_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='transaction_id',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='codtransaction',
            name='transaction_status',
            field=models.CharField(default=b'INITIATED', max_length=30, choices=[(b'INITIATED', b'INITIATED'), (b'VERIFIED', b'VERIFIED'), (b'DECLINED', b'DECLINED')]),
        ),
        migrations.AlterField(
            model_name='codtransaction',
            name='transaction_type',
            field=models.CharField(default=b'UNKNOWN', max_length=30, choices=[(b'TRANSFER', b'TRANSFER'), (b'BANKDEPOSIT', b'BANKDEPOSIT'), (b'UNKNOWN', b'UNKNOWN')]),
        ),
    ]
