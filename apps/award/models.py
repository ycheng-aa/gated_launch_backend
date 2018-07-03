from django.db import models
from apps.common.models import CommonInfoModel
from django.conf import settings
from apps.common.models import Image
from apps.app.models import App
from benchmark_django_rest_framework.benchmark_model import BenchmarkModel
# Create your models here.


class Award(BenchmarkModel, CommonInfoModel):
    name = models.CharField(max_length=255)
    app = models.ForeignKey(App)
    image = models.ForeignKey(Image, null=True)
    desc = models.TextField(null=True)

    def __str__(self):
        return u"%s" % self.name


class Awardee(BenchmarkModel, CommonInfoModel):
    award = models.ForeignKey(Award)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    desc = models.TextField(null=True)

    class Meta:
        unique_together = (('award', 'user'),)
