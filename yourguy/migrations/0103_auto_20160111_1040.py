# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0102_auto_20160108_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryTeamLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_stamp', models.DateTimeField(null=True, blank=True)),
                ('remarks', models.CharField(max_length=500, blank=True)),
                ('action', models.ForeignKey(to='yourguy.DeliveryAction')),
                ('by_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitude', models.CharField(max_length=50)),
                ('longitude', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('delivery_id', models.CharField(max_length=25, null=True, blank=True)),
                ('message', models.CharField(max_length=500, null=True, blank=True)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('code', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceableCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city_code', models.CharField(unique=True, max_length=10)),
                ('city_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceablePincode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pincode', models.CharField(unique=True, max_length=10)),
                ('city', models.ForeignKey(to='yourguy.ServiceableCity')),
            ],
        ),
        migrations.AddField(
            model_name='consumer',
            name='full_name',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='consumer',
            name='phone_number',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='is_teamlead',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(default=b'caller', max_length=15, choices=[(b'sales', b'sales'), (b'sales_manager', b'sales_manager'), (b'operations', b'operations'), (b'operations_manager', b'operations_manager'), (b'accounts', b'accounts'), (b'caller', b'caller'), (b'manager', b'manager')]),
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.ForeignKey(to='yourguy.NotificationType'),
        ),
        migrations.AddField(
            model_name='deliverytransaction',
            name='location',
            field=models.ForeignKey(blank=True, to='yourguy.Location', null=True),
        ),
        migrations.AddField(
            model_name='deliveryteamlead',
            name='associate_delivery_guys',
            field=models.ManyToManyField(related_name='associate_delivery_guys', to='yourguy.DeliveryGuy'),
        ),
        migrations.AddField(
            model_name='deliveryteamlead',
            name='delivery_guy',
            field=models.ForeignKey(related_name='current_delivery_guy', to='yourguy.DeliveryGuy'),
        ),
        migrations.AddField(
            model_name='deliveryteamlead',
            name='serving_pincodes',
            field=models.ManyToManyField(to='yourguy.ServiceablePincode'),
        ),
        migrations.AddField(
            model_name='consumer',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification'),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification'),
        ),
        migrations.AddField(
            model_name='dgattendance',
            name='checkin_location',
            field=models.ForeignKey(related_name='checkin_location', blank=True, to='yourguy.Location', null=True),
        ),
        migrations.AddField(
            model_name='dgattendance',
            name='checkout_location',
            field=models.ForeignKey(related_name='checkout_location', blank=True, to='yourguy.Location', null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='city',
            field=models.ForeignKey(blank=True, to='yourguy.ServiceableCity', null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification'),
        ),
        migrations.AddField(
            model_name='employee',
            name='serving_pincodes',
            field=models.ManyToManyField(to='yourguy.ServiceablePincode'),
        ),
        migrations.AddField(
            model_name='orderdeliverystatus',
            name='delivery_transactions',
            field=models.ManyToManyField(to='yourguy.DeliveryTransaction'),
        ),
        migrations.AddField(
            model_name='vendoragent',
            name='notifications',
            field=models.ManyToManyField(to='yourguy.Notification'),
        ),
    ]
