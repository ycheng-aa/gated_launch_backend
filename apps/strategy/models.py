from django.db import models
from apps.common.models import CommonInfoModel
from apps.app.models import App
from apps.user_group.models import UserGroup
from django.conf import settings


class PushChannel(CommonInfoModel):
    # define constant
    SMS = "sms"
    MAIL = "mail"

    name = models.CharField(max_length=255, verbose_name="推送类型名称", default="")

    def __str__(self):
        return u"%s" % self.name


class AbsInnerStrategy(CommonInfoModel):
    name = models.CharField(max_length=255, verbose_name="内灰策略名称", default="")
    app = models.ForeignKey(App)
    push_content = models.TextField(verbose_name="推送内容", default="")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    user_groups = models.ManyToManyField(UserGroup, blank=True)
    push_channels = models.ManyToManyField(PushChannel, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return u"%s" % self.name


class AbsOuterStrategy(CommonInfoModel):
    name = models.CharField(max_length=255, verbose_name="外灰策略名称", default="")
    app = models.ForeignKey(App)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    version = models.CharField(max_length=255, verbose_name="版本", default="", blank=True)
    allow_users = models.TextField(verbose_name="外灰用户列表", default="", blank=True)
    range_dates = models.CharField(max_length=2048, verbose_name="外灰时间范围及次数限额", default="", blank=True)
    cities = models.CharField(max_length=1024, verbose_name="城市列表", default="", blank=True)
    city_enable = models.BooleanField(verbose_name="包含或不包含城市", default=True)
    channels = models.TextField(verbose_name="外灰渠道", default="", blank=True)
    percentage = models.IntegerField(verbose_name="百分比", default=0, blank=True)
    status = models.BooleanField(verbose_name="状态", default=False)
    is_compatible = models.IntegerField(verbose_name="是否强制执行", default=0)
    frequency = models.IntegerField(verbose_name="每天提示次数", default=0)
    change_log = models.TextField(verbose_name="推送给app的内容", default="", blank=True)
    change_log_img = models.CharField(max_length=200, verbose_name="上传到图床返回的名称", default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return u"%s" % self.name


class InnerStrategy(AbsInnerStrategy):
    pass


class OuterStrategy(AbsOuterStrategy):
    pass


class Strategy(CommonInfoModel):
    type = models.CharField(max_length=255, verbose_name="策略类型", default="")
    name = models.CharField(max_length=255, verbose_name="策略名称", default="")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    inner_strategy = models.ForeignKey(InnerStrategy, blank=True, null=True)
    outer_strategy = models.ForeignKey(OuterStrategy, blank=True, null=True)
    app = models.ForeignKey(App)
