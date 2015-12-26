# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0043_order_recurrences'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pushdetail',
            name='user',
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='device_token',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='PushDetail',
        ),
    ]
