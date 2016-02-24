# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0121_auto_20160220_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='CODAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10, blank=True)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CODTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_stamp', models.DateTimeField(null=True, blank=True)),
                ('remarks', models.CharField(max_length=500, blank=True)),
                ('transaction_type', models.CharField(max_length=200, blank=True)),
                ('transaction_status', models.CharField(max_length=200, blank=True)),
                ('action', models.ForeignKey(to='yourguy.CODAction', on_delete=django.db.models.deletion.PROTECT)),
                ('by_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('location', models.ForeignKey(blank=True, to='yourguy.Location', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProofOfBankDeposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('total_cod', models.FloatField(default=0.0)),
                ('by_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('picture', models.ManyToManyField(to='yourguy.Picture', blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(default=b'caller', max_length=50, choices=[(b'sales', b'sales'), (b'sales_manager', b'sales_manager'), (b'operations', b'operations'), (b'operations_manager', b'operations_manager'), (b'accounts', b'accounts'), (b'caller', b'caller'), (b'hr', b'hr'), (b'admin', b'admin')]),
        ),
    ]
