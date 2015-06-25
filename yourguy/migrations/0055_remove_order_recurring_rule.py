# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0054_order_recurring_rule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='recurring_rule',
        ),
    ]
