from django.db import models
from apps.common.models import CommonInfoModel
from apps.common.models import Image
from benchmark_django_rest_framework.benchmark_model import BenchmarkModel
from django.conf import settings
# Create your models here.


class AppType(BenchmarkModel, CommonInfoModel):
    # define constant
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
    Other = "other"

    name = models.CharField(max_length=20, unique=True)
    desc = models.TextField(null=True)

    def __str__(self):
        return u"%s" % self.name


class AppComponent(CommonInfoModel):
    """
    定义app对应jira上的模块和默认经办人，issue转jira会用到
    """
    name = models.CharField(max_length=50, verbose_name="模块名称", unique=True)
    desc = models.CharField(max_length=100, verbose_name="模块描述", null=False)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, verbose_name="默认经办人")

    def __str__(self):
        return "{} : {}".format(self.name, self.operator)


class AppStatus(CommonInfoModel):
    """
    项目状态
    """
    ORIGIN_STATUS = "unReviewed"
    REVIEWED_PASS_STATUS = "reviewedPass"
    REVIEWED_FAIL_STATUS = "reviewedFail"
    name = models.CharField(max_length=256, verbose_name="状态名称")
    description = models.CharField(default="", max_length=256, verbose_name="状态中文名称")

    def __str__(self):
        return self.name

    @staticmethod
    def get_original_status():
        return AppStatus.objects.get(name=AppStatus.ORIGIN_STATUS)


class App(BenchmarkModel, CommonInfoModel):
    name = models.CharField(max_length=255, unique=True)
    component = models.ForeignKey(AppComponent, on_delete=models.SET_DEFAULT, default=1)
    image = models.ForeignKey(Image, null=True, blank=True)
    types = models.ManyToManyField(AppType, blank=True)
    desc = models.TextField(null=True)
    bp_app_id = models.IntegerField(null=True, blank=True)
    apphub_name = models.CharField(max_length=255, default=None, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    bp_channels_name = models.CharField(max_length=255, default=None, null=True)
    status = models.ForeignKey(AppStatus, null=True, blank=True)

    def __str__(self):
        return u"%s" % self.name
