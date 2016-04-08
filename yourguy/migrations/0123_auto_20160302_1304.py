# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0122_auto_20160224_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='CODAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CODTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time_stamp', models.DateTimeField(auto_now_add=True)),
                ('verified_time_stamp', models.DateTimeField(null=True, blank=True)),
                ('remarks', models.CharField(max_length=500, blank=True)),
                ('transaction_status', models.CharField(default=b'INITIATED', max_length=30, choices=[(b'INITIATED', b'INITIATED'), (b'VERIFIED', b'VERIFIED'), (b'DECLINED', b'DECLINED')])),
                ('transaction_uuid', models.CharField(max_length=500)),
                ('dg_id', models.IntegerField(null=True, blank=True)),
                ('dg_tl_id', models.IntegerField(null=True, blank=True)),
                ('cod_amount', models.FloatField(default=0.0)),
                ('deliveries', models.CommaSeparatedIntegerField(max_length=500)),
                ('created_by_user', models.ForeignKey(related_name='created_by_user', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(blank=True, to='yourguy.Location', null=True)),
                ('transaction', models.ForeignKey(to='yourguy.CODAction', on_delete=django.db.models.deletion.PROTECT)),
                ('verified_by_user', models.ForeignKey(related_name='verified_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProofOfBankDeposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('total_cod', models.FloatField(default=0.0)),
                ('by_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('receipt', models.ManyToManyField(to='yourguy.Picture', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_status',
            field=models.CharField(default=b'COD_NOT_AVAILABLE', max_length=100, choices=[(b'COD_NOT_AVAILABLE', b'COD_NOT_AVAILABLE'), (b'COD_COLLECTED', b'COD_COLLECTED'), (b'COD_TRANSFERRED_TO_TL', b'COD_TRANSFERRED_TO_TL'), (b'COD_BANK_DEPOSITED', b'COD_BANK_DEPOSITED'), (b'COD_VERIFIED', b'COD_VERIFIED'), (b'COD_TRANSFERRED_TO_CLIENT', b'COD_TRANSFERRED_TO_CLIENT')]),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='cod_transactions',
            field=models.ManyToManyField(to='yourguy.CODTransaction', blank=True),
        ),
    ]
