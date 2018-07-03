"""gated_launch_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.utils.module_loading import autodiscover_modules
from apps.common.routers import routers

from apps.auth.views import weixin_auth_token

from apps.common.views.image_view import ImageView, UploadImageView
from apps.common.views.login_view import LoginView
from apps.common.views.id_code_view import IdCodeView
from apps.common.views.app_module_view import AppModuleView
from apps.common.views.app_version_view import AppVersionView
from apps.common.views.sms_view import SmsView
from apps.common.views.email_view import EmailView
from apps.bp.views import BpVersionView, BpVersionPlatform, BpVersionChannel
from apps.award.views import AwardView, AwardeeView
from apps.info.views import MySummaryView, MyAppsView, TakenStatsView, WeiXinLogInStatsView
from apps.issue.views import IssueStatsView, CreateJiraView, jiraToIssue

from django.conf import settings

autodiscover_modules('routers')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^api/v1/login/', views.obtain_auth_token),
    url(r'^api/v1/', include(routers.urls)),

    # common: 图片相关接口
    url(r'^api/v1/uploadImages/?$', UploadImageView.as_view()),
    url(r'^api/v1/images/(?P<pk>[\w|.]+)/?$', ImageView.as_view(has_pk=True)),
    url(r'^api/v1/images/?$', ImageView.as_view()),

    # common: 登录相关接口
    url(r'^api/v1/login/?', LoginView.as_view(), name='Login'),
    url(r'^api/v1/idCode/?', IdCodeView.as_view(), name='IdCode'),  # 获取验证码图片

    # common: app 模块接口
    url(r'^api/v1/appModules/(?P<pk>\w+)/?$', AppModuleView.as_view(has_pk=True)),
    url(r'^api/v1/appModules/?$', AppModuleView.as_view()),

    # common: 从 apphub 获取版本列表
    url(r'^api/v1/appVersions/(?P<app>\w+)/?$', AppVersionView.as_view()),
    url(r'^api/v1/appVersions/?$', AppVersionView.as_view()),

    # common: 发送信息相关接口
    url(r'^api/v1/sms/?$', SmsView.as_view()),
    url(r'^api/v1/email/?$', EmailView.as_view()),

    # BP后台管理接口 by wangxiaodong37
    url(r'^api/v1/bpVersions/?$', BpVersionView.as_view()),
    url(r'^api/v1/bpVersions/version/(?P<version>\d+)/?$', BpVersionView.as_view(has_pk=True)),
    url(r'^api/v1/bpVersions/platform/(?P<clienttype>\d+)/?$', BpVersionPlatform.as_view(has_pk=True)),
    url(r'^api/v1/bpVersions/channels/?$', BpVersionChannel.as_view()),

    # app管理接口 by wangxiaodong37
    # TODO remove following 2 lines after verified it works fine
    # url(r'^api/v1/apps/?$', AppView.as_view(), name='apps'),
    # url(r'^api/v1/apps/(?P<pk>\d+)/?$', AppView.as_view(has_pk=True), name='apps-detail'),

    # 激励管理接口 by wangxiaodong37
    # 激励列表页url
    url(r'^api/v1/awards/?$', AwardView.as_view()),
    # 激励详情页url
    url(r'^api/v1/awards/(?P<pk>\w+)/?$', AwardView.as_view(has_pk=True)),
    # 特定激励的获奖人员列表页url
    url(r'^api/v1/awards/(?P<award>\w+)/awardees/?$', AwardeeView.as_view(has_pk=True)),
    # 获奖人员列表页url
    url(r'^api/v1/awardees/?$', AwardeeView.as_view(has_pk=True)),
    # 获奖人员详情页url
    url(r'^api/v1/awardees/(?P<pk>\d+)/?$', AwardeeView.as_view(has_pk=True)),
    # 登陆用户获奖信息页url
    url(r'^api/v1/awardees/user/(?P<user>\d+)/?$', AwardeeView.as_view(has_pk=True)),

    # info接口
    url(r'^api/v1/mySummary/?$', MySummaryView.as_view(), name='mysummary'),
    url(r'^api/v1/myApps/?$', MyAppsView.as_view()),
    url(r'^api/v1/takenStats/?$', TakenStatsView.as_view(), name='takenstats'),

    # issue统计接口
    url(r'^api/v1/issueStats/?$', IssueStatsView.as_view(), name='issuestats'),
    url(r'^api/v1/issueToJira/?$', CreateJiraView.as_view(), name='issuetojira'),
    url(r'^api/v1/jiraToIssue/?$', jiraToIssue.as_view(), name='jiratoissue'),

    url(r'^api/v1/weixin_login/$', weixin_auth_token),

    # 微信小程序登录统计接口
    url(r'^api/v1/weixinLoginStats/?$', WeiXinLogInStatsView.as_view(), name='weixinloginstats'),

]

if getattr(settings, 'DEBUG'):
    # production env should not have this lib
    # swagger
    try:
        from apps.common.swagger_utils import get_swagger_view
    except ImportError:
        from rest_framework_swagger.views import get_swagger_view
    urlpatterns.append(url(r'^swagger/$', get_swagger_view(title='灰度发布 API')))

    from apps.auth.views import obtain_expiring_auth_token

    urlpatterns.append(url(r'^api/v1/dev_login/$', obtain_expiring_auth_token))
    from apps.utils.views import force_sync_user_info

    urlpatterns.append(url(r'^api/v1/force_sync/?$', force_sync_user_info))
    from apps.bp.views import BpVersionConfig

    urlpatterns.append(url(r'^api/v1/bpVersions/config/?$', BpVersionConfig.as_view()))
    from apps.bp.views import BpVersionOnline

    urlpatterns.append(url(r'^api/v1/bpVersions/online/?$', BpVersionOnline.as_view()))
