# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0114_vendor_is_hyper_local'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryguy',
            name='area',
        ),
    ]
