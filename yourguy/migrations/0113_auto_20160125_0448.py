# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0112_auto_20160125_0443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='profile_picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='profile_picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AlterField(
            model_name='deliveryteamlead',
            name='delivery_guy',
            field=models.ForeignKey(related_name='current_delivery_guy', on_delete=django.db.models.deletion.PROTECT, to='yourguy.DeliveryGuy'),
        ),
        migrations.AlterField(
            model_name='deliverytransaction',
            name='action',
            field=models.ForeignKey(to='yourguy.DeliveryAction', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='dgattendance',
            name='dg',
            field=models.ForeignKey(to='yourguy.DeliveryGuy', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='employee',
            name='profile_picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.ForeignKey(to='yourguy.NotificationType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Product', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.ProductCategory', null=True),
        ),
        migrations.AlterField(
            model_name='serviceablepincode',
            name='city',
            field=models.ForeignKey(to='yourguy.ServiceableCity', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='account',
            field=models.ForeignKey(related_name='account', on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.VendorAccount', null=True),
        ),
        migrations.AlterField(
            model_name='vendoraccount',
            name='billing_address',
            field=models.ForeignKey(related_name='billing_address', on_delete=django.db.models.deletion.PROTECT, to='yourguy.Address', null=True),
        ),
        migrations.AlterField(
            model_name='vendoragent',
            name='profile_picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='yourguy.Picture', null=True),
        ),
        migrations.AlterField(
            model_name='vendoragent',
            name='vendor',
            field=models.ForeignKey(related_name='vendor', on_delete=django.db.models.deletion.PROTECT, to='yourguy.Vendor'),
        ),
    ]
