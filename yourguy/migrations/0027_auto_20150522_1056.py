# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0026_auto_20150522_1002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestedvendor',
            name='address',
        ),
        migrations.DeleteModel(
            name='RequestedVendor',
        ),
    ]
