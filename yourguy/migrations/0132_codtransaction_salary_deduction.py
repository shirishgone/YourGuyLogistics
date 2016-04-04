# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0131_auto_20160319_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='codtransaction',
            name='salary_deduction',
            field=models.FloatField(default=0.0),
        ),
    ]
