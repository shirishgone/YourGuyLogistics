# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0069_auto_20150706_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='building',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='address',
            name='country_code',
            field=models.CharField(default=b'IN', max_length=25),
        ),
        migrations.AlterField(
            model_name='address',
            name='flat_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='address',
            name='landmark',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='latitude',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='longitude',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='pin_code',
            field=models.CharField(max_length=25, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='area',
            name='area_code',
            field=models.CharField(unique=True, max_length=25),
        ),
        migrations.AlterField(
            model_name='area',
            name='area_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='picture_link',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='latitude',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='longitude',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='picture_link',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='status',
            field=models.CharField(default=b'AVAILABLE', max_length=25, choices=[(b'AVAILABLE', b'AVAILABLE'), (b'BUSY', b'BUSY')]),
        ),
        migrations.AlterField(
            model_name='employee',
            name='picture_link',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='vendoragent',
            name='picture_link',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
