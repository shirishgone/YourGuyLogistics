# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0109_auto_20160115_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryaction',
            name='code',
            field=models.CharField(max_length=10, blank=True),
        ),
    ]
