# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0116_auto_20160129_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='approved_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='approved_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
