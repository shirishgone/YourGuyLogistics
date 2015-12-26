# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0002_remove_order_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryguy',
            name='availability',
            field=models.CharField(default=b'AV', max_length=2, choices=[(b'AV', b'Available'), (b'BS', b'Busy')]),
        ),
    ]
