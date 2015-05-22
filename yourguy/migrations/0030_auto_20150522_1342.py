# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0029_product_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='amount',
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost',
            field=models.FloatField(default=0.0),
        ),
    ]
