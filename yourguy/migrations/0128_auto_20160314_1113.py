# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0127_codtransaction_bank_deposit_proof'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proofofbankdeposit',
            old_name='declined_time_stamp',
            new_name='updated_time_stamp',
        ),
        migrations.RemoveField(
            model_name='proofofbankdeposit',
            name='declined_by_user',
        ),
        migrations.RemoveField(
            model_name='proofofbankdeposit',
            name='verified_by_user',
        ),
        migrations.RemoveField(
            model_name='proofofbankdeposit',
            name='verified_time_stamp',
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='proof_status',
            field=models.CharField(default=b'NONE', max_length=30, choices=[(b'NONE', b'NONE'), (b'VERIFIED', b'VERIFIED'), (b'DECLINED', b'DECLINED')]),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='receipt_number',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='updated_by_user',
            field=models.ForeignKey(related_name='updated_by_user', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
