# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0136_auto_20160301_0647'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codtransaction',
            old_name='action',
            new_name='transaction',
        ),
    ]
