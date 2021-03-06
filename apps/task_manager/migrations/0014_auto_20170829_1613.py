# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-29 16:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0013_auto_20170828_1733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graytask',
            name='award_rules',
        ),
        migrations.RemoveField(
            model_name='graytask',
            name='contact_way',
        ),
        migrations.AddField(
            model_name='graytask',
            name='award_rule',
            field=models.TextField(default='', verbose_name='获奖规则, 支持文本'),
        ),
        migrations.AddField(
            model_name='graytask',
            name='contact',
            field=models.TextField(default='', verbose_name='联系方式, 支持文本'),
        ),
        migrations.AlterField(
            model_name='graytask',
            name='version_desc',
            field=models.TextField(default='', verbose_name='版本描述信息, 支持文本'),
        ),
    ]
