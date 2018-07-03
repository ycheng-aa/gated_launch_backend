# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-27 12:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('module_name', models.CharField(max_length=100)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.App')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]