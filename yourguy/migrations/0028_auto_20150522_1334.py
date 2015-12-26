# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0027_auto_20150522_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pickedup_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ManyToManyField(to='yourguy.Product'),
        ),
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='details',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='address',
        ),
        migrations.AddField(
            model_name='consumer',
            name='address',
            field=models.ManyToManyField(to='yourguy.Address', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.FloatField(default=1.0),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
