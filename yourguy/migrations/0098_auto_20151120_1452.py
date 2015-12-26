# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0097_auto_20151031_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='pickup_guy',
            field=models.ForeignKey(related_name='pickup_dg', blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='timeslots',
            field=models.ManyToManyField(to='yourguy.TimeSlot'),
        ),
    ]
