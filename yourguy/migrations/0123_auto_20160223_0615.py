# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0122_auto_20160223_0556'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proofofbankdeposit',
            old_name='picture',
            new_name='receipt',
        ),
    ]
