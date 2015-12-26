# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0061_auto_20150626_1212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='is_COD',
            new_name='is_cod',
        ),
    ]
