# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-05 16:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0003_auto_20170628_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='snapshotouterstrategy',
            name='channels',
        ),
        migrations.AddField(
            model_name='snapshotouterstrategy',
            name='channels',
            field=models.TextField(default='', verbose_name='外灰渠道'),
        ),
    ]
