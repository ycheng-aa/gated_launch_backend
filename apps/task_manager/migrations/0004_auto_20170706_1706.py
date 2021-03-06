# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-06 17:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20170629_1517'),
        ('task_manager', '0003_auto_20170628_1547'),
    ]

    operations = [
        migrations.RenameField(
            model_name='graystatus',
            old_name='status_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='graytask',
            old_name='outer_Strategy',
            new_name='outer_strategy',
        ),
        migrations.RemoveField(
            model_name='graystatus',
            name='status_id',
        ),
        migrations.RemoveField(
            model_name='graytask',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='graytask',
            name='image_url',
        ),
        migrations.AddField(
            model_name='graytask',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Image', verbose_name='图片id'),
        ),
        migrations.AlterField(
            model_name='graytask',
            name='current_step',
            field=models.IntegerField(default=1, verbose_name='当前步骤'),
        ),
    ]
