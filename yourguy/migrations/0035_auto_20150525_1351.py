# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0034_auto_20150523_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.FloatField(default=1.0)),
                ('cost', models.FloatField(default=0.0)),
                ('product', models.ManyToManyField(to='yourguy.Product')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='order_items',
            field=models.ManyToManyField(to='yourguy.OrderItem'),
        ),
    ]
