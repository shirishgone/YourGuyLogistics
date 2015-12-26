# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.FloatField(default=0.0)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flat_number', models.CharField(max_length=50)),
                ('area_name', models.CharField(max_length=50)),
                ('floor_number', models.CharField(max_length=50, blank=True)),
                ('building_name', models.CharField(max_length=50, blank=True)),
                ('wing', models.CharField(max_length=50, blank=True)),
                ('road', models.CharField(max_length=50, blank=True)),
                ('landmark', models.CharField(max_length=50, blank=True)),
                ('pin_code', models.CharField(max_length=10, blank=True)),
                ('country_code', models.CharField(default=b'IN', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(unique=True, max_length=100)),
                ('user_type', models.CharField(default=b'EM', max_length=2, choices=[(b'DG', b'DeliveryGuy'), (b'VN', b'Vendor'), (b'CN', b'Consumer'), (b'EM', b'Employee')])),
                ('picture_link', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('facebook_id', models.CharField(max_length=50, blank=True)),
                ('address', models.ForeignKey(related_name='consumer_address', blank=True, to='yourguy.Address')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DeliveryGuy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(unique=True, max_length=100)),
                ('user_type', models.CharField(default=b'EM', max_length=2, choices=[(b'DG', b'DeliveryGuy'), (b'VN', b'Vendor'), (b'CN', b'Consumer'), (b'EM', b'Employee')])),
                ('picture_link', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('assigned_locality_code', models.CharField(max_length=10)),
                ('latitude', models.CharField(max_length=10, blank=True)),
                ('longitude', models.CharField(max_length=10, blank=True)),
                ('address', models.ForeignKey(related_name='dg_home_address', blank=True, to='yourguy.Address')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DGAttendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('status', models.CharField(default=b'UN', max_length=2, choices=[(b'LE', b'Leave'), (b'WG', b'Working'), (b'UN', b'UN')])),
                ('login_time', models.DateTimeField(blank=True)),
                ('logout_time', models.DateTimeField(blank=True)),
                ('dg', models.ForeignKey(to='yourguy.DeliveryGuy')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(unique=True, max_length=100)),
                ('user_type', models.CharField(default=b'EM', max_length=2, choices=[(b'DG', b'DeliveryGuy'), (b'VN', b'Vendor'), (b'CN', b'Consumer'), (b'EM', b'Employee')])),
                ('picture_link', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('employee_code', models.CharField(max_length=20)),
                ('department', models.CharField(default=b'CC', max_length=2, choices=[(b'SL', b'Sales'), (b'OP', b'Operations'), (b'CC', b'CallCenter'), (b'MG', b'Manager')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('created_date_time', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickup_datetime', models.DateTimeField()),
                ('delivery_datetime', models.DateTimeField()),
                ('created_date_time', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(default=b'PP', max_length=2, choices=[(b'PP', b'Preparing'), (b'DS', b'Dispatched'), (b'IT', b'InTransit'), (b'CD', b'Completed')])),
                ('is_COD', models.BooleanField(default=False)),
                ('completed_datetime', models.DateTimeField(blank=True)),
                ('modified_date_time', models.DateTimeField(blank=True)),
                ('quantity', models.FloatField(blank=True)),
                ('cancel_request_time', models.DateTimeField(blank=True)),
                ('amount', models.CharField(max_length=50, blank=True)),
                ('notes', models.CharField(max_length=500, blank=True)),
                ('vendor_order_id', models.CharField(max_length=10, blank=True)),
                ('tags', models.CharField(max_length=500, blank=True)),
                ('assigned_to', models.ForeignKey(related_name='assinged_dg', blank=True, to=settings.AUTH_USER_MODEL)),
                ('cancel_request_by_user', models.ForeignKey(related_name='cancelled_by_user', blank=True, to=settings.AUTH_USER_MODEL)),
                ('created_by_user', models.ForeignKey(related_name='order_created_by', to=settings.AUTH_USER_MODEL)),
                ('delivery_address', models.ForeignKey(related_name='delivery_address', to='yourguy.Address')),
                ('modified_by_user', models.ForeignKey(related_name='order_modified_by', blank=True, to=settings.AUTH_USER_MODEL)),
                ('pickup_address', models.ForeignKey(related_name='pickup_address', to='yourguy.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PushDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_token', models.CharField(max_length=200)),
                ('device_id', models.CharField(max_length=100, blank=True)),
                ('platform', models.CharField(max_length=10, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('amount', models.FloatField(default=0.0)),
                ('from_user', models.ForeignKey(related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='to_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='yourguy.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_push_enabled', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(unique=True, max_length=100)),
                ('user_type', models.CharField(default=b'EM', max_length=2, choices=[(b'DG', b'DeliveryGuy'), (b'VN', b'Vendor'), (b'CN', b'Consumer'), (b'EM', b'Employee')])),
                ('picture_link', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('store_name', models.CharField(max_length=200)),
                ('website_url', models.CharField(max_length=100, blank=True)),
                ('address', models.ForeignKey(related_name='vendor_address', blank=True, to='yourguy.Address')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(to='yourguy.Vendor', blank=True),
        ),
        migrations.AddField(
            model_name='consumer',
            name='associated_vendor',
            field=models.ManyToManyField(to='yourguy.Vendor', blank=True),
        ),
        migrations.AddField(
            model_name='consumer',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
