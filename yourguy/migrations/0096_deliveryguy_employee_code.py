# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0095_auto_20151008_0722'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='employee_code',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
