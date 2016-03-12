# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0126_auto_20160311_0648'),
    ]

    operations = [
        migrations.AddField(
            model_name='codtransaction',
            name='bank_deposit_proof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.ProofOfBankDeposit', null=True),
        ),
    ]
