# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0042_order_delivered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(null=True),
        ),
    ]
