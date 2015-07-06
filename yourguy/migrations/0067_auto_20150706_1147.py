# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0066_auto_20150703_0715'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rates', models.FloatField(default=0.0)),
                ('balance', models.FloatField(default=0.0)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='vendor',
            name='account',
            field=models.ForeignKey(related_name='account', to='yourguy.VendorAccount', null=True),
        ),
    ]
