# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yourguy', '0019_auto_20150516_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.EmailField(max_length=50, blank=True)),
                ('picture_link', models.CharField(max_length=50, blank=True)),
                ('branch', models.CharField(max_length=50, blank=True)),
                ('role', models.CharField(default=b'EMPLOYEE', max_length=15, choices=[(b'EMPLOYEE', b'EMPLOYEE'), (b'MANAGER', b'MANAGER')])),
                ('address', models.ForeignKey(blank=True, to='yourguy.Address', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='consumer',
            old_name='is_verified',
            new_name='phone_verified',
        ),
        migrations.RenameField(
            model_name='deliveryguy',
            old_name='availability',
            new_name='status',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='alternate_phone_number',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='assigned_area',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='escalation_phone_number',
        ),
        migrations.RemoveField(
            model_name='deliveryguy',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='picture_link',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='user',
        ),
        migrations.AddField(
            model_name='consumer',
            name='name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='deliveryguy',
            name='name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='address',
            field=models.ForeignKey(blank=True, to='yourguy.Address', null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='alternate_phone_number',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='notes',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='pan_card',
            field=models.CharField(max_length=15, blank=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='address',
            field=models.ForeignKey(blank=True, to='yourguy.Address', null=True),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='email',
            field=models.EmailField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='address',
            field=models.ForeignKey(blank=True, to='yourguy.Address', null=True),
        ),
        migrations.AlterField(
            model_name='deliveryguy',
            name='email',
            field=models.EmailField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='address',
            field=models.ForeignKey(related_name='vendor_address', blank=True, to='yourguy.Address', null=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='email',
            field=models.EmailField(max_length=50),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='store_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name='vendoragent',
            name='vendor',
            field=models.ForeignKey(related_name='vendor', to='yourguy.Vendor'),
        ),
    ]
