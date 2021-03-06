# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-20 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def preset_user_group_type(apps, schema_editor):
    types = ['angel', 'company', 'custom']
    type_model = apps.get_model('user_group', 'UserGroupType')
    for t in types:
        type_model.objects.create(name=t)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('expired', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserGroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('expired', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='usergroup',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_group.UserGroupType'),
        ),
        migrations.RunPython(preset_user_group_type, reverse_code=migrations.RunPython.noop),
    ]
