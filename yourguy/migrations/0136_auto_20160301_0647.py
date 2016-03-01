# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0135_auto_20160301_0608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='codtransaction',
            old_name='cod_transaction',
            new_name='action',
        ),
        migrations.RenameField(
            model_name='codtransaction',
            old_name='transaction_id',
            new_name='transaction_uuid',
        ),
    ]
