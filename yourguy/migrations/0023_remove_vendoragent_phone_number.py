# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0022_vendoragent_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendoragent',
            name='phone_number',
        ),
    ]
