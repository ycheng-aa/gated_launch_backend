# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-01 10:13
from __future__ import unicode_literals

from django.db import migrations, models


def preset_app_type(apps, schema_editor):
    type_model = apps.get_model('app', 'AppType')
    type_model.objects.get_or_create(name='web')


def remove_app_type(apps, schema_editor):
    type_model = apps.get_model('app', 'AppType')
    type_model.objects.filter(name='web').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_app_component'),
    ]

    operations = [
        migrations.RunPython(preset_app_type, reverse_code=remove_app_type),
    ]