# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0080_auto_20150720_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='cod_collected',
            new_name='is_cod_collected',
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='is_cod_collected',
            field=models.BooleanField(default=False),
        ),
    ]
