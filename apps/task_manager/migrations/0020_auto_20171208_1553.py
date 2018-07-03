# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-08 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0019_graytask_is_join_kesutong'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graytask',
            name='inner_strategy',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='内部策略id 列表'),
        ),
        migrations.AlterField(
            model_name='graytask',
            name='outer_strategy',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='外部策略id 列表'),
        ),
    ]