# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0088_auto_20150803_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proofofdelivery',
            name='signature',
            field=models.ForeignKey(related_name='pod_signature', blank=True, to='yourguy.Picture', null=True),
        ),
    ]
