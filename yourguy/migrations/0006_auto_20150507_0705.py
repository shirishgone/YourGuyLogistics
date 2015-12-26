# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0005_auto_20150506_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area_code', models.CharField(max_length=10)),
                ('area_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='address',
            name='area_name',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='assigned_locality_code',
        ),
        migrations.AddField(
            model_name='consumer',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='address',
            name='area',
            field=models.ForeignKey(related_name='area', default=0, to='yourguy.Area'),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='assigned_area',
            field=models.ForeignKey(related_name='assigned_area', default=0, blank=True, to='yourguy.Area'),
        ),
    ]
