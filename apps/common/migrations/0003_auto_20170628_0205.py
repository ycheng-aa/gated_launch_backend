# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-28 02:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_appmodule'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='updated_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
