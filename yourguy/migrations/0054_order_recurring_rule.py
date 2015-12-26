# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0053_auto_20150622_0808'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='recurring_rule',
            field=models.CharField(max_length=2000, blank=True),
        ),
    ]
