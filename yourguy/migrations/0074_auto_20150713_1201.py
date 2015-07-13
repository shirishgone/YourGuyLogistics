# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0073_auto_20150713_0838'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dgattendance',
            old_name='login_time',
            new_name='login',
        ),
        migrations.RenameField(
            model_name='dgattendance',
            old_name='logout_time',
            new_name='logout',
        ),
    ]
