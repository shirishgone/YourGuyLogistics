# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0111_auto_20160122_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='consumer',
            field=models.ForeignKey(to='yourguy.Consumer', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_by_user',
            field=models.ForeignKey(related_name='order_created_by', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_address',
            field=models.ForeignKey(related_name='delivery_address', on_delete=django.db.models.deletion.PROTECT, to='yourguy.Address'),
        ),
        migrations.AlterField(
            model_name='order',
            name='modified_by_user',
            field=models.ForeignKey(related_name='order_modified_by', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='pickup_address',
            field=models.ForeignKey(related_name='pickup_address', on_delete=django.db.models.deletion.PROTECT, to='yourguy.Address'),
        ),
        migrations.AlterField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(to='yourguy.Vendor', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivery_guy',
            field=models.ForeignKey(related_name='assigned_dg', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivery_proof',
            field=models.ForeignKey(related_name='delivery_pod', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.ProofOfDelivery', null=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='order',
            field=models.ForeignKey(related_name='order', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Order', null=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='pickup_guy',
            field=models.ForeignKey(related_name='pickup_dg', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.DeliveryGuy', null=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='pickup_proof',
            field=models.ForeignKey(related_name='pickup_pod', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.ProofOfDelivery', null=True),
        ),
    ]
