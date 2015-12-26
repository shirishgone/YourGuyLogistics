# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0084_picture_proofofdelivery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumer',
            name='picture_link',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='picture_link',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='picture_link',
        ),
        migrations.RemoveField(
            model_name='vendoragent',
            name='picture_link',
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='delivery_proof',
            field=models.ForeignKey(related_name='delivery_pod', blank=True, to='yourguy.ProofOfDelivery', null=True),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='pickup_proof',
            field=models.ForeignKey(related_name='pickup_pod', blank=True, to='yourguy.ProofOfDelivery', null=True),
        ),
    ]
