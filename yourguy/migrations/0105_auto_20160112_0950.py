# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0104_auto_20160111_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='addresses',
            field=models.ManyToManyField(to='yourguy.Address', blank=True),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification', blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification', blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryteamlead',
            name='associate_delivery_guys',
            field=models.ManyToManyField(related_name='associate_delivery_guys', to='yourguy.DeliveryGuy', blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryteamlead',
            name='serving_pincodes',
            field=models.ManyToManyField(to='yourguy.ServiceablePincode', blank=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification', blank=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='serving_pincodes',
            field=models.ManyToManyField(to='yourguy.ServiceablePincode', blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_items',
            field=models.ManyToManyField(to='yourguy.OrderItem', blank=True),
        ),
        migrations.AlterField(
            model_name='orderdeliverystatus',
            name='delivery_transactions',
            field=models.ManyToManyField(to='yourguy.DeliveryTransaction', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='timeslots',
            field=models.ManyToManyField(to='yourguy.TimeSlot', blank=True),
        ),
        migrations.AlterField(
            model_name='proofofdelivery',
            name='pictures',
            field=models.ManyToManyField(to='yourguy.Picture', blank=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='addresses',
            field=models.ManyToManyField(to='yourguy.Address', blank=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='industries',
            field=models.ManyToManyField(to='yourguy.Industry', blank=True),
        ),
        migrations.AlterField(
            model_name='vendoragent',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification', blank=True),
        ),
    ]
