# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0133_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumer',
            name='associated_vendor',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='notifications',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='profile_picture',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='user',
        ),
    ]
