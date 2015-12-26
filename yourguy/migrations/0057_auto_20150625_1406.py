# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0056_auto_20150625_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryguy',
            name='transport_mode',
            field=models.CharField(default=b'PUBLIC_TRANSPORT', max_length=25, choices=[(b'PUBLIC_TRANSPORT', b'PUBLIC_TRANSPORT'), (b'NON_AC_VEHICLE', b'NON_AC_VEHICLE'), (b'AC_VEHICLE', b'AC_VEHICLE'), (b'BIKE', b'BIKE')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='transport_mode',
            field=models.CharField(default=b'PUBLIC_TRANSPORT', max_length=25, choices=[(b'PUBLIC_TRANSPORT', b'PUBLIC_TRANSPORT'), (b'NON_AC_VEHICLE', b'NON_AC_VEHICLE'), (b'AC_VEHICLE', b'AC_VEHICLE'), (b'BIKE', b'BIKE')]),
        ),
    ]
