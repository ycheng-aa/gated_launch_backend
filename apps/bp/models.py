from django.db import models
from benchmark_django_rest_framework.benchmark_model import BenchmarkModel

# Create your models here.


class AppVersions(BenchmarkModel, models.Model):
    version = models.IntegerField(primary_key=True)
    app_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    allow_users = models.CharField(max_length=512)
    range_dates = models.CharField(max_length=256)
    citys = models.CharField(max_length=256)
    city_enable = models.IntegerField()
    # sit 环境有percentage 字段
    # percentage = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_versions'
        unique_together = (('version', 'app_id'),)


class Clientversion(BenchmarkModel, models.Model):
    cvid = models.AutoField(primary_key=True)
    app_id = models.CharField(max_length=20)
    channel = models.CharField(max_length=20)
    clienttype = models.SmallIntegerField()
    version = models.ForeignKey(AppVersions, db_column='version')
    version_name = models.CharField(max_length=20)
    changelogimg = models.CharField(max_length=200, blank=True, null=True)
    changelog = models.CharField(max_length=20000, blank=True, null=True)
    size = models.IntegerField()
    url = models.CharField(max_length=256)
    iscompatible = models.SmallIntegerField()
    createtime = models.DateTimeField()
    minimumversion = models.IntegerField()
    frequency = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'clientversion'
