# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0120_auto_20160210_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(default=b'caller', max_length=50, choices=[(b'sales', b'sales'), (b'sales_manager', b'sales_manager'), (b'operations', b'operations'), (b'operations_manager', b'operations_manager'), (b'accounts', b'accounts'), (b'caller', b'caller'), (b'HR', b'hr'), (b'admin', b'admin')]),
        ),
    ]
