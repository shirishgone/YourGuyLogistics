# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0008_auto_20150513_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='assigned_to',
            field=models.ForeignKey(related_name='assinged_dg', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='cancel_request_by_user',
            field=models.ForeignKey(related_name='cancelled_by_user', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='cancel_request_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='completed_datetime',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='modified_by_user',
            field=models.ForeignKey(related_name='order_modified_by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='modified_date_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(blank=True, to='yourguy.Vendor', null=True),
        ),
    ]
