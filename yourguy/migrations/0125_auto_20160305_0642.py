# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0124_consumer_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumer',
            name='vendor',
            field=models.ForeignKey(related_name='single_vendor', blank=True, to='yourguy.Vendor', null=True),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='associated_vendor',
            field=models.ManyToManyField(related_name='multiple_vendor', to='yourguy.Vendor', blank=True),
        ),
    ]
