# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0074_auto_20150713_1201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dgattendance',
            old_name='login',
            new_name='login_time',
        ),
        migrations.RenameField(
            model_name='dgattendance',
            old_name='logout',
            new_name='logout_time',
        ),
    ]
