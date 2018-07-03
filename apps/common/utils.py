from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.forms.models import model_to_dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests
import smtplib
from functools import wraps
from apps.common.gated_logger import gated_debug_logger
from apps.app.models import AppType
from apps.common.serializers import AppVersionSerializer
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView


# 从模型A实例拷贝同属性名到另一个模型B,根据两个dict分别改变之前和之后的属性值，返回模型实例B


def copy_model_to_model(instance_from, model_name_to, pop_change_dict={}, change_dict={}, data_change_dict={}):
    data = model_to_dict(instance_from)
    for k, v in pop_change_dict.items():
        data[k] = data.pop(v)
    for k, v in data_change_dict.items():
        data[k] = v
    instance_to = model_name_to(**data)
    for k, v in change_dict.items():
        setattr(instance_to, k, v)
    return instance_to


def log_wrapper(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        gated_debug_logger.debug("Start Function: {} ,args: {} {}".format(func.__name__, args, kwargs))
        ret = func(*args, **kwargs)
        gated_debug_logger.debug("End Function: {} ,args: {} {}".format(func.__name__, args, kwargs))
        return ret
    return _wrapper


def send_sms(phones, message):
    if not phones:
        return
    # TODO open comments when it's ok in business
    # message = '[["","","' + str(message) + '"]]'
    # for phone in phones:
    #     valid_time = int(time.time()) + 3600
    #     url = settings.OTHER_PLATFORM_URLS['SMS']
    #     data = {
    #         'templateId': 388,
    #         'deviceList': '[' + str(phone) + ']',
    #         'deviceType': 0,
    #         'argsList': message,
    #         'validTime': valid_time,
    #         'contentType': 0
    #     }
    #     try:
    #         response = requests.post(url=url, data=data)
    #         response = json.loads(response.text)
    #         if response['status'] == 200:
    #             gated_debug_logger.debug('手机号: ' + str(phone) + ', 短信发送成功. smsOutboxId: ' + str(response['data']['smsOutboxId']))
    #         else:
    #             gated_debug_logger.debug('手机号: ' + str(phone) + ', 短信发送失败. 失败原因: ' + response['message'])
    #     except Exception as e:
    #         gated_debug_logger.debug('手机号: ' + str(phone) + ', 短信发送失败. 失败原因: ' + str(e))


def send_email(emails, subject=None, context=None):
    """
    :param emails         收件人邮箱, 字符串或字符串数组
    :param subject        邮件标题
    :param context        邮件内容, 若开头为 <html> 标记, 则以 html 格式发送邮件
    目前不支持发送附件; 收件人单独, 看不到其他收件人
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    if isinstance(context, str):
        if context.startswith('<html>'):
            context = MIMEText(context, 'html')
        else:
            context = MIMEText(context, 'plain')
        msg.attach(context)
    msg = msg.as_string()
    while len(emails) > 0:
        # 邮件服务器限制, 每次只能发送 100 个邮件
        _emails, emails = emails[:100], emails[100:]
        try:
            gated_debug_logger.debug('发送邮件开始. 邮箱: ' + str(_emails))
            smtp = smtplib.SMTP(settings.EMAIL_SERVER)
            try:
                # 有的服务器上不支持 ssl 加密, 没有找到服务器哪里配置不同导致, 那就不加密了
                # 异常信息是: [SSL: SSL_NEGATIVE_LENGTH] dh key too small (_ssl.c:645)
                smtp.starttls()
            except Exception as e:
                gated_debug_logger.debug('发送邮件SSL加密失败, 不使用加密. 失败原因: ' + str(e) + ', 异常类型: ' + str(type(e)))
                smtp = smtplib.SMTP(settings.EMAIL_SERVER)
            smtp.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            smtp.sendmail(settings.EMAIL_USERNAME, _emails, msg)
            smtp.quit()
            gated_debug_logger.debug('发送邮件成功. 邮箱: ' + str(_emails))
        except Exception as e:
            gated_debug_logger.debug('发送邮件失败. 失败原因: ' + str(e))
            gated_debug_logger.debug('发送邮件失败. 邮箱: ' + str(_emails))


def log_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            gated_debug_logger.error(str(e))
            raise e
    return wrapper


APPHUB_ANDROID = 0
APPHUB_IOS = 1


def get_app_versions(app_id=None, app_type=None, download_urls=None):
    '''
    :param app_id: App 主键, None 为查询全部
    :param app_type: "ios" 或 "android", None 为查询全部
    :param download_urls: 下载链接的字符串数组, None 为查询最近内测的相应最新上线的版本
    :return: 带有 status, msg, data 的字典. 格式规范同请求返回的 json
    '''
    params = {}
    if app_id is not None:
        params['app'] = str(app_id)
    if app_type is not None:
        params['app_type'] = app_type
    if download_urls is not None and isinstance(download_urls, str):
        download_urls = [download_urls]
    serializer = AppVersionSerializer(data=params)
    serializer.is_valid(raise_exception=True)
    if app_id is None:
        apphub_names = [value for value in AppVersionSerializer.app_id_to_apphub_name.values() if value is not None]
    else:
        apphub_name = AppVersionSerializer.app_id_to_apphub_name[app_id]
        if apphub_name is None:
            return BenchmarkAPIView.get_response_by_code(1010)
        apphub_names = (AppVersionSerializer.app_id_to_apphub_name[app_id],)
    if app_type is None:
        app_types = AppVersionSerializer.app_type_choices
    else:
        app_types = (app_type,)
    apphub_res_versions = []
    if download_urls is None:
        for app_type in app_types:
            if app_type == AppType.ANDROID:
                dev_type = APPHUB_ANDROID
            else:
                dev_type = APPHUB_IOS
            for apphub_name in apphub_names:
                params = {'prod_id': apphub_name, 'dev_type': dev_type, 'is_closed': 0}
                try:
                    res = json.loads(requests.get(settings.OTHER_PLATFORM_URLS['APPHUB_APPS'], params=params).text)
                    if res['status'] != 0:    # prod_id 查不到
                        continue
                    apphub_res_versions.extend(res['result'])
                except Exception as e:
                    return BenchmarkAPIView.get_response_by_code(1006, msg_append=str(e))
    else:
        for url in download_urls:
            if url is None or url == '':
                continue
            params = {'dwn_url': url}
            try:
                res = json.loads(requests.get(settings.OTHER_PLATFORM_URLS['APPHUB_APPS'], params=params).text)
                # 下载链接 url 查询不到
                if res['status'] != 0:
                    continue
                apphub_res_versions.extend(res['result'])
            except Exception as e:
                return BenchmarkAPIView.get_response_by_code(1006, msg_append=str(e))
    versions = []
    for version in apphub_res_versions:
        app_type = AppType.ANDROID if version['dev_type'] == APPHUB_ANDROID else AppType.IOS
        app_id = AppVersionSerializer.apphub_name_to_app_id_and_name[version['prod_id']]['app_id']
        app_name = AppVersionSerializer.apphub_name_to_app_id_and_name[version['prod_id']]['app_name']
        versions.append({
            'app_id': app_id, 'app_name': app_name, 'version_id': version['build_num'], 'app_type': app_type,
            'url_download': version['app_url'], 'create_date': version['create_time'][:10],
            'amount_of_download': version['amount_of_download'], 'is_closed': version['is_closed']
        })
    return BenchmarkAPIView.get_response_by_code(data=versions)


def get_response_business_status_code(response):
        return getattr(response, 'data', {}).get('status', 0)


def register(*app_list):
    for app_label in app_list:
        for model in apps.get_app_config(app_label).get_models():
            try:
                admin.site.register(model)
            except AlreadyRegistered:
                pass
