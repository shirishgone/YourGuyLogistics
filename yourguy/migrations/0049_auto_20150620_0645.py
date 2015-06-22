# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0048_auto_20150618_1217'),
    ]

    operations = [
        migrations.CreateModel(
            name='DGTracking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.FloatField(default=0.0)),
                ('longitude', models.FloatField(default=0.0)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='longitude',
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='app_version',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='battery_percentage',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='last_connected',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 20, 6, 45, 51, 913040, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dgtracking',
            name='dg',
            field=models.ForeignKey(to='yourguy.DeliveryGuy'),
        ),
    ]
