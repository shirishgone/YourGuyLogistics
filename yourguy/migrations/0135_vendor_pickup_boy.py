# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0134_auto_20160408_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='pickup_boy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
    ]
