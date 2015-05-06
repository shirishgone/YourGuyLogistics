# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0003_deliveryguy_availability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=b'UN', max_length=2, choices=[(b'UN', b'UnAssigned'), (b'AS', b'Assigned'), (b'CD', b'Completed')]),
        ),
    ]
