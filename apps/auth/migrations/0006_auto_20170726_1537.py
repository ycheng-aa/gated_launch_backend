# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-26 15:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gated_launch_auth', '0005_auto_20170712_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gated_launch_auth.Role'),
        ),
    ]