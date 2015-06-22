# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0053_auto_20150622_0808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='latitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='longitude',
            field=models.FloatField(default=0.0),
        ),
    ]
