# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yourguy', '0101_auto_20151210_1651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='user',
        ),
        migrations.RemoveField(
            model_name='group',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.RemoveField(
            model_name='suggestion',
            name='user',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='from_user',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='to_user',
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usersetting',
            name='user',
        ),
        migrations.RemoveField(
            model_name='consumer',
            name='facebook_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='cancel_request_by_user',
        ),
        migrations.RemoveField(
            model_name='order',
            name='cancel_request_time',
        ),
        migrations.RemoveField(
            model_name='order',
            name='completed_datetime',
        ),
        migrations.RemoveField(
            model_name='order',
            name='delivered_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='delivery_guy',
        ),
        migrations.RemoveField(
            model_name='order',
            name='is_cod_collected',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='pickedup_datetime',
        ),
        migrations.RemoveField(
            model_name='order',
            name='recurrences',
        ),
        migrations.RemoveField(
            model_name='order',
            name='rejection_reason',
        ),
        migrations.RemoveField(
            model_name='order',
            name='transport_mode',
        ),
        migrations.RemoveField(
            model_name='orderdeliverystatus',
            name='order_id_in_order_table',
        ),
        migrations.DeleteModel(
            name='Account',
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='Suggestion',
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
        migrations.DeleteModel(
            name='UserGroup',
        ),
        migrations.DeleteModel(
            name='UserSetting',
        ),
    ]
