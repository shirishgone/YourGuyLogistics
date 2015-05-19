# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0020_auto_20150518_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestedVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('store_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=50)),
                ('website_url', models.CharField(max_length=100, blank=True)),
                ('alternate_phone_number', models.CharField(max_length=15, blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('pan_card', models.CharField(max_length=15, blank=True)),
                ('notes', models.CharField(max_length=500, blank=True)),
                ('address', models.ForeignKey(to='yourguy.Address')),
            ],
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='address',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='address',
        ),
        migrations.RemoveField(
            model_name='vendoragent',
            name='address',
        ),
    ]
