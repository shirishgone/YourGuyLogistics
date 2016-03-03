# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0123_auto_20160302_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumer',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
