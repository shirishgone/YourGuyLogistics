# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0119_auto_20160204_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='deactivated_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
