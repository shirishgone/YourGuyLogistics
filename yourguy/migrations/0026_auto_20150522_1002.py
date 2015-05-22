# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0025_auto_20150520_1836'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumer',
            name='email',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='name',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='email',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='name',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='email',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='name',
        ),
        migrations.RemoveField(
            model_name='vendoragent',
            name='email',
        ),
        migrations.RemoveField(
            model_name='vendoragent',
            name='name',
        ),
    ]
