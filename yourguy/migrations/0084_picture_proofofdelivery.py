# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0083_auto_20150721_0949'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('url', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='ProofOfDelivery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('receiver_name', models.CharField(max_length=100)),
                ('pictures', models.ManyToManyField(to='yourguy.Picture')),
                ('signature', models.ForeignKey(related_name='pod_signature', to='yourguy.Picture')),
            ],
        ),
    ]
