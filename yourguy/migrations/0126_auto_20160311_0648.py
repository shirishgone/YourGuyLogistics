# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0125_auto_20160305_0642'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proofofbankdeposit',
            old_name='date_time',
            new_name='created_time_stamp',
        ),
        migrations.RemoveField(
            model_name='proofofbankdeposit',
            name='by_user',
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='pending_salary_deduction',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='bank_deposit_proof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.ProofOfBankDeposit', null=True),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='created_by_user',
            field=models.ForeignKey(related_name='pobd_created_by_user', on_delete=django.db.models.deletion.PROTECT, default='', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='declined_by_user',
            field=models.ForeignKey(related_name='pobd_declined_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='declined_time_stamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='verified_by_user',
            field=models.ForeignKey(related_name='pobd_verified_by_user', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='verified_time_stamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
