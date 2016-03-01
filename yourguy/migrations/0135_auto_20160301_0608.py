# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0134_auto_20160226_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codtransaction',
            old_name='action',
            new_name='cod_transaction',
        ),
        migrations.RenameField(
            model_name='codtransaction',
            old_name='time_stamp',
            new_name='created_time_stamp',
        ),
        migrations.RemoveField(
            model_name='codtransaction',
            name='by_user',
        ),
        migrations.RemoveField(
            model_name='codtransaction',
            name='transaction_type',
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='created_by_user',
            field=models.ForeignKey(related_name='created_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='verified_by_user',
            field=models.ForeignKey(related_name='verified_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='codtransaction',
            name='verified_time_stamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='codtransaction',
            name='transaction_id',
            field=models.CharField(default=datetime.datetime(2016, 3, 1, 6, 8, 24, 643295, tzinfo=utc), max_length=500),
            preserve_default=False,
        ),
    ]
