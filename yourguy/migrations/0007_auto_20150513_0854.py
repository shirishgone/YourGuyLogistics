# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0006_auto_20150507_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumer',
            name='user_type',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='user_type',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='user_type',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='user_type',
        ),
    ]
