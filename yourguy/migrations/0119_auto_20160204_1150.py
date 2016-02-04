# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0118_deliveryguy_deactivated_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='deactivated_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
