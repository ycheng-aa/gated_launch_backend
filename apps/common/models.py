from django.db import models
from benchmark_django_rest_framework.benchmark_model import BenchmarkModel


class CommonInfoModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Image(BenchmarkModel, CommonInfoModel):
    '''
        图片表
    '''
    image_id = models.CharField(primary_key=True, max_length=18, verbose_name='主键, 图片id, 即图床上传成功后接口返回字段 tfs_key')
    image_name = models.CharField(max_length=1024, verbose_name='图片原始文件名', null=True)
    image_desc = models.TextField(verbose_name='图片描述, 支持文本或 json', null=True)

    def __str__(self):
        return u"%s" % self.image_id


class AppModule(BenchmarkModel, CommonInfoModel):
    from apps.app.models import App
    app = models.ForeignKey(App)
    module_name = models.CharField(max_length=100)

    class Meta:
        unique_together = (('app', 'module_name'),)

    def __str__(self):
        return u"%s" % self.module_name


# save arbitrary key - value pair
class Property(CommonInfoModel):
    key = models.CharField(max_length=1000)
    value = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return u"%s : %s" % (self.key, self.value)
