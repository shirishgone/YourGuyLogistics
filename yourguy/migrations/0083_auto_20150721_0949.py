# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0082_auto_20150721_0857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='industry',
        ),
        migrations.AddField(
            model_name='vendor',
            name='industries',
            field=models.ManyToManyField(to='yourguy.Industry'),
        ),
    ]
