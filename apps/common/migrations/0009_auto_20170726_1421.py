# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-26 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20170725_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appmodule',
            name='app',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.App'),
            preserve_default=False,
        ),
    ]
