# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0128_auto_20160314_1113'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proofofbankdeposit',
            name='receipt',
        ),
        migrations.AddField(
            model_name='proofofbankdeposit',
            name='receipt',
            field=models.ForeignKey(blank=True, to='yourguy.Picture', null=True),
        ),
    ]
