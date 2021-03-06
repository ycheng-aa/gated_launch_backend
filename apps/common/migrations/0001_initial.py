# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-26 07:05
from __future__ import unicode_literals

import benchmark_django_rest_framework.benchmark_model
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('image_id', models.CharField(max_length=18, primary_key=True, serialize=False, verbose_name='主键, 图片id, 即图床上传成功后接口返回字段 tfs_key')),
                ('image_name', models.CharField(max_length=1024, null=True, verbose_name='图片原始文件名')),
                ('image_desc', models.TextField(null=True, verbose_name='图片描述, 支持文本或 json')),
            ],
            bases=(benchmark_django_rest_framework.benchmark_model.BenchmarkModel, models.Model),
        ),
    ]
