from django.db import models
from django.db.models import SET_NULL
from apps.common.models import CommonInfoModel, Image, AppModule
from apps.app.models import App
from apps.task_manager.models import GrayTask, IssueExtField
from django.conf import settings
from mptt import models as mptt_models


class IssueType(CommonInfoModel):
    '''
    Issus类型
    '''

    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")

    def __str__(self):
        return self.name


class IssueStatus(CommonInfoModel):
    '''
    Issus状态
    '''
    CREATE_STATUS = "待处理"
    PROCESSING_STATUS = "处理中"
    CLOSE_STATUS = "关闭"
    VERIFYING_STATUS = '验证'
    SUSPENDING_STATUS = '挂起'
    NEW_STATUS = "新增"

    name = models.CharField(max_length=50, unique=True, verbose_name="状态名称")
    description = models.CharField(max_length=50, unique=True, verbose_name="状态描述", null=False, default="")

    def __str__(self):
        return self.name


class BusinessModuleTree(mptt_models.MPTTModel):
    name = models.CharField(max_length=50, verbose_name="业务模块名称")
    description = models.CharField(max_length=256, verbose_name="业务模块描述", null=True, blank=True)
    parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children')
    disabled = models.BooleanField(default=False, verbose_name="业务模块是否下架")

    class Meta:
        ordering = ("level", "disabled", "-id")
        unique_together = (('name', 'parent'),)

    def __str__(self):
        return self.name


class PhoneBrand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="手机品牌")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="所属大区")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class IssueReportSource(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="问题报告来源名称")
    desc = models.CharField(max_length=100, null=True, blank=True, verbose_name="问题报告来源描述")

    def __str__(self):
        return self.name


class IssuePriority(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="英文名称")
    desc = models.CharField(max_length=100, unique=True, verbose_name="中文描述")

    URGENT = 'urgent'
    NORMAL = 'normal'
    UNURGENT = 'unurgent'

    def __str__(self):
        return "{} : {}".format(self.name, self.desc)

    @classmethod
    def get_default_obj(cls):
        return cls.objects.get(name=cls.NORMAL)

    @classmethod
    def get_default_desc(cls):
        return cls.NORMAL


class Issue(CommonInfoModel):
    app = models.ForeignKey(App)
    task = models.ForeignKey(GrayTask)
    app_module = models.ForeignKey(AppModule, null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_issues')
    marker = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='+')
    title = models.CharField(max_length=200)
    detail = models.TextField()
    images = models.ManyToManyField(Image, blank=True)
    score = models.IntegerField(blank=True, null=True, default=0)
    jira_link = models.CharField(max_length=200, blank=True, null=True)
    status = models.ForeignKey(IssueStatus, null=True, blank=True)
    type = models.ForeignKey(IssueType, null=True, blank=True)
    report_source = models.ForeignKey(IssueReportSource, on_delete=SET_NULL, null=True, blank=True)
    other = models.TextField(null=True, blank=True, verbose_name="附加信息，如小程序特定信息等")
    priority = models.ForeignKey(IssuePriority, on_delete=SET_NULL, null=True)
    kst_unread_flag = models.NullBooleanField(default=False)
    plat_unread_flag = models.NullBooleanField(default=False)
    zc_change_logs = models.TextField(null=True, blank=True, verbose_name="众测平台操作日志")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='operated_issues',
                                 on_delete=SET_NULL, null=True, verbose_name="经办人")

    def get_ext_field_value(self, field_name):
        result = None
        ext_field = IssueExtField.objects.filter(task=self.task, name=field_name).first()
        if ext_field:
            ext_value_obj = IssueExtValue.objects.filter(issue=self, field=ext_field).first()
            if ext_value_obj:
                result = ext_value_obj.value
        return result

    def set_ext_field_value(self, field_name, value):
        """
        :param field_name: 扩展字段名
        :param value: 期望设置值
        :return: 成功返回True, 否则False
        """
        result = False
        ext_field = IssueExtField.objects.filter(task=self.task, name=field_name).first()
        if ext_field:
            ext_value_obj, _ = IssueExtValue.objects.get_or_create(issue=self, field=ext_field)
            if ext_value_obj:
                ext_value_obj.value = value
                ext_value_obj.save()
                result = True
        return result

    class Meta:
        index_together = ('app', 'task', 'creator')
        ordering = ("-created_time", "type")
        verbose_name = 'issues'

    def __str__(self):
        return u"%s" % self.title


class IssueExtValue(CommonInfoModel):
    issue = models.ForeignKey(Issue, related_name='ext_values', verbose_name="对应的issue")
    field = models.ForeignKey(IssueExtField)
    value = models.TextField(verbose_name="扩展字段值")

    class Meta:
        unique_together = ('issue', 'field')

    def __str__(self):
        return "{} - {}: {}".format(self.issue.title, self.field.name, self.value)
