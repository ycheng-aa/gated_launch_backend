from django.db import models
from apps.common.models import CommonInfoModel


class ExampleUser(CommonInfoModel):
    username = models.CharField(max_length=50, default="test1", verbose_name="username")
    email = models.EmailField(default="test1@wanda.cn", verbose_name="email")
    is_staff = models.BooleanField(default=False, verbose_name="is_stuff")

    def __str__(self):
        return "Example User name: %s, email:%s" % (self.username, self.email)
