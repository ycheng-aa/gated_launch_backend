from django.conf import settings
from django.db import models, transaction, IntegrityError
from rest_framework.exceptions import ValidationError

from apps.common.models import CommonInfoModel, Image
from apps.app.models import App
from apps.strategy.models import AbsInnerStrategy, AbsOuterStrategy
from apps.common.gated_logger import gated_debug_logger


class GrayStatus(CommonInfoModel):
    """
    灰度状态
    """
    ORIGIN_STATUS = "preparation"
    TESTING_STATUS = "testing"
    FINISH_STATUS = "finished"
    name = models.CharField(max_length=256, verbose_name="状态名称")
    description = models.CharField(default="", max_length=256, verbose_name="状态中文名称")

    def __str__(self):
        return self.name

    @staticmethod
    def get_original_status():
        qs = GrayStatus.objects.filter(name=GrayStatus.ORIGIN_STATUS)
        if qs:
            return qs[0]
        else:
            return None


class GrayTask(CommonInfoModel):
    """
    灰度任务表

    """
    task_name = models.CharField(max_length=128, verbose_name="任务名称", unique=True)
    app = models.ForeignKey(App, verbose_name="app 外键")
    start_date = models.DateField(verbose_name="开始日期")
    end_date = models.DateField(verbose_name="结束日期")
    image = models.ForeignKey(Image, null=True, verbose_name="图片id")
    inner_strategy = models.CharField(max_length=256, blank=True, null=True, verbose_name="内部策略id 列表")
    inner_strategy_steps = models.IntegerField(default=0, verbose_name="内部策略总步数")
    outer_strategy = models.CharField(max_length=256, blank=True, null=True, verbose_name="外部策略id 列表")
    total_strategy_steps = models.IntegerField(default=0, verbose_name="策略总步数")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户id")
    current_status = models.ForeignKey(GrayStatus, verbose_name="灰度任务状态外键")
    is_display = models.BooleanField(default=False, verbose_name="是否置顶")
    version_desc = models.TextField(verbose_name="版本描述信息, 支持文本", default="")
    award_rule = models.TextField(verbose_name="获奖规则, 支持文本", default="")
    contact = models.TextField(verbose_name="联系方式, 支持文本", default="")
    is_join_kesutong = models.BooleanField(default=False, verbose_name="是否接入客诉通找茬")

    def __str__(self):
        return "Task name: %s, status:%s" % (self.task_name, self.current_status)

    def to_dict(self, detail=False):
        try:
            res = {
                "id": self.id,
                "name": self.task_name,
                "isDisplay": self.is_display,
                "isJoinKesutong": self.is_join_kesutong,
                "startDate": self.start_date,
                "endDate": self.end_date,
                "innerStrategy": self.inner_strategy,
                "outerStrategy": self.outer_strategy,
                "imageId": self.image.image_id if self.image else "",
                "creator": self.creator.username,
                "currentStatus": self.current_status.description,
                "createdDate": self.created_time.date(),
                "versionDesc": self.version_desc,
                "awardRule": self.award_rule,
                "contact": self.contact,
                "app": {
                    "appId": self.app.id,
                    "name": self.app.name,
                    "desc": self.app.desc,
                }
            }

            grap_version = self.grayappversion_set.all()
            # android，ios下载次数需要每步求和
            from apps.issue.models import Issue
            res["qualityData"] = {
                "androidDownload": sum([d.android_download_number for d in grap_version]),
                "iosDownload": sum([d.ios_download_number for d in grap_version]),
                "feedback": Issue.objects.filter(task=self).count()
            }
            res["appVersion"] = [
                {
                    "step": a.current_step,
                    "stepName": a.current_step_name,
                    "androidVersion": a.android_version,
                    "androidURL": a.android_download_url,
                    "androidCreateDate": a.android_release_date,
                    "iosVersion": a.ios_version,
                    "iosURL": a.ios_download_url,
                    "iosCreateDate": a.ios_release_date,
                    "updatedTime": a.updated_time.strftime("%Y-%m-%d %H:%M:%S")
                }
                for a in grap_version]

            res['steps'] = SnapshotInnerStrategy.to_list(self) + SnapshotOuterStrategy.to_list(self)
            # 当前步骤是最后的值, 如果没有版本信息，则步骤为0
            res["current_step"] = res["appVersion"][-1]["step"] if res["appVersion"] else 0
            res["current_step_name"] = \
                res["steps"][res["current_step"] - 1]["name"] if res[
                    "steps"] else 0

        except Exception as e:
            gated_debug_logger.error("Task:{}, instance to dict fail, {}".format(self.id, e))
            raise ValidationError({"msg": "Task: {}, instance to dict fail, {}".format(self.id, e)})
        return res

    def update_status(self, status):
        if self.current_status.id < status.id:
            self.current_status = status
            self.save()
            gated_debug_logger.debug("Update task:{},status:{}, successfully".format(self.id, status.name))
        else:
            gated_debug_logger.error("Update task:{},status:{}, Fail".format(self.id, status.name))
            raise ValidationError({"msg": "Task can not be set to this status: {}".format(status.name)})

    def set_is_display(self, is_display):
        try:
            with transaction.atomic():
                GrayTask.objects.filter(app=self.app, is_display=True).update(is_display=False)
                self.is_display = True if is_display == 'true' else False
                self.save()
                gated_debug_logger.debug("Set App {}, Task: {} DisPlay Successful".format(self.app.id, self.id))
        except IntegrityError:
            gated_debug_logger.error("Set App {}, Task: {} DisPlay Fail".format(self.app.id, self.id))
            return False
        return self


class GrayTaskLog(CommonInfoModel):
    """
    灰度任务表更新记录
    """
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, verbose_name="操作人员")
    gray_task = models.ForeignKey(GrayTask)

    update_log = models.TextField(max_length=2000, verbose_name="更新字段名称和值")

    def __str__(self):
        return self.update_log


class GrayTaskRunStatus(CommonInfoModel):
    """
    灰度任务运行状态表
    """
    gray_task = models.ForeignKey(GrayTask, verbose_name="任务外键")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户外键")
    current_step = models.IntegerField(verbose_name="当前步骤")
    current_step_name = models.CharField(max_length=256, default="", verbose_name="当前步骤")
    task_status = models.ForeignKey(GrayStatus, verbose_name="任务状态")
    update_info = models.TextField(max_length=2000, verbose_name="任务更新信息")

    def __str__(self):
        return "Task: %s, step: %s, status: %s" % (self.gray_task.task_name, self.current_step, self.task_status)


class SnapshotInnerStrategy(AbsInnerStrategy):
    """
    内部灰度策略
    """
    gray_task = models.ForeignKey(GrayTask, verbose_name="灰度任务id", null=False)
    index = models.IntegerField(verbose_name="策略顺序", default=0, null=False)

    def __str__(self):
        return "Task:{},index:{} strategy:{}".format(self.gray_task.task_name, self.index, self.name)

    @staticmethod
    def to_list(task):
        snaps = SnapshotInnerStrategy.objects.filter(gray_task=task).all()
        snaps_list = [
            {
                "id": s.id,
                "index": s.index,
                "name": s.name,
                "type": "inner"
            }
            for s in snaps
        ]
        return snaps_list


class SnapshotOuterStrategy(AbsOuterStrategy):
    """
    外部灰度策略
    """
    gray_task = models.ForeignKey(GrayTask, verbose_name="灰度任务id")
    index = models.IntegerField(verbose_name="策略顺序")

    def __str__(self):
        return "Task:{},index:{} strategy:{}".format(self.gray_task.task_name, self.index, self.name)

    @staticmethod
    def to_list(task):
        snaps = SnapshotOuterStrategy.objects.filter(gray_task=task).all()
        snaps_list = [
            {
                "id": s.id,
                "index": s.index,
                "name": s.name,
                "type": "outer"
            }
            for s in snaps]
        return snaps_list


class GrayAppVersion(CommonInfoModel):
    """
    灰度版本更新记录
    """
    gray_task = models.ForeignKey(GrayTask, verbose_name="任务外键")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="user")
    current_step = models.IntegerField(default=0, verbose_name="当前步骤")
    current_step_name = models.CharField(default="", max_length=256, verbose_name="当前策略名称")
    android_version = models.CharField(default="", max_length=256, verbose_name="android版本名称")
    android_release_date = models.DateField(null=True, verbose_name="android版本创建时间")
    android_download_url = models.CharField(default="", max_length=1000, verbose_name="android版本下载链接")
    android_download_number = models.IntegerField(default=0, verbose_name="android版本下载量")
    ios_version = models.CharField(default="", max_length=256, verbose_name="ios版本号")
    ios_release_date = models.DateField(null=True, verbose_name="ios版本创建时间")
    ios_download_url = models.CharField(default="", max_length=1000, verbose_name="ios版本下载链接")
    ios_download_number = models.IntegerField(default=0, verbose_name="ios版本下载量")
    is_current_use = models.BooleanField(default=False, verbose_name="是否当前使用")
    expired = models.BooleanField(default=False, verbose_name="是否过期")

    def __str__(self):
        return "Task:{}, current step: {}, {}".format(self.gray_task.task_name, self.current_step,
                                                      self.current_step_name)

    @staticmethod
    def update_version(data):
        """
        1、步骤总数不能大于策略和，
        2、每次只能更新当前步骤或者+1步，
        3、没有版本时步骤必须为1,即第一个步骤
        4、任务状态不能为 结束
        :param data:
        :return:
        """
        task = data['gray_task']
        if task.current_status.name == GrayStatus.FINISH_STATUS:
            raise ValidationError({"msg": "Task was test completed!"})

        if task.total_strategy_steps < data['current_step']:
            raise ValidationError({"msg": "current_step is large then max step"})

        versions = GrayAppVersion.objects.filter(gray_task=data['gray_task']).order_by('-current_step').all()

        if versions and data['current_step'] not in (
                versions[0].current_step, min(versions[0].current_step + 1, task.total_strategy_steps)):
            raise ValidationError({"msg": "current_step mast step by step or not large max"})

        if not versions and data['current_step'] != 1:
            raise ValidationError({"msg": "current_step must be 1"})

        snap = SnapshotInnerStrategy if data['current_step'] <= task.inner_strategy_steps else SnapshotOuterStrategy
        strategy = snap.objects.filter(gray_task=task, index=data['current_step']).first()
        data['current_step_name'] = strategy.name
        try:
            with transaction.atomic():
                if data['current_step'] == 1:
                    task.current_status = GrayStatus.objects.filter(name=GrayStatus.TESTING_STATUS).first()
                    task.save()
                gray_version = GrayAppVersion(**data)
                gray_version.save()
        except IntegrityError:
            gated_debug_logger.error("Start Test Fail {}".format(data))
            return False
        return True


class IssueExtField(CommonInfoModel):
    task = models.ForeignKey(GrayTask, related_name='ext_fields', verbose_name='对其问题做字段扩展的任务')
    name = models.CharField(max_length=200)
    default = models.CharField(max_length=200, null=True, blank=True, verbose_name='字段默认值')
    is_optional = models.BooleanField(default=True, verbose_name='是否为可选，默认为可选')
    type = models.CharField(max_length=20, null=True, blank=True,
                            verbose_name='字符串表示字段类型，未指定则字段为字符串类型')

    class Meta:
        unique_together = ('task', 'name')

    def __str__(self):
        return u"%s %s" % (self.task.task_name, self.name)
