# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0136_auto_20160415_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='is_email_updates_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vendor',
            name='is_pod_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vendor',
            name='is_pop_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vendor',
            name='sms_when_cod_collected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vendor',
            name='sms_when_order_delivered',
            field=models.BooleanField(default=False),
        ),
    ]
