import traceback
from django.core.cache import cache
import hashlib
import pycurl
import json
from django.contrib.auth import get_user_model
from django.db.models import Q
from requests.sessions import Session
from apps.app.models import App
from apps.auth.models import Department
from apps.common.exceptions import JiraError
from apps.common.gated_logger import gated_debug_logger
from io import BytesIO
from django.conf import settings
from rest_framework import status
from urllib.parse import quote
from apps.common.models import Property
from apps.common.utils import log_exception, send_email
from apps.issue.models import IssuePriority, IssueStatus, Issue
from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from apps.bp.models import AppVersions, Clientversion
from apps.user_group.models import UserGroup, UserGroupType
from apps.task_manager.models import SnapshotOuterStrategy, GrayTask
from apps.usage.models import EventTracking, EventType
from apps.usage.models import Property as usageProperty
import re
import copy
import datetime
import requests
from gated_launch_backend.settings import JIRA_STATUS, RTX_VERIFY_HOST, \
    IMAGES_URL, ZC_REPORT_SOURCE, ZC_SCORE_TO_JIRA_SEVERITY, JIRA_UPDATE_LIST, JIRA_API_URL, KE_SU_TONG, \
    WEIXIN_AUTH_TOKEN_API_URL, WEIXIN_NOTIFICATION_URL, STATPLAT_API_URL, STATPLAT_TOKEN, CHECK_ISSUE_STATUS, \
    ADMIN_EMAILS

LAST_TIME_STAFF_INFO_CHECKSUM = 'last time staff info checksum'
IOS = 1
Android = 2
Online = 1
Offline = 0

if settings.USE_SENTRY:
    from raven import Client
    sentry_client = Client(settings.SENTRY_CLIENT)


class ClassProperty(property):
    def __get__(self, obj, objtype=None):
        return super().__get__(objtype)

    def __set__(self, obj, value):
        super().__set__(type(obj), value)

    def __delete__(self, obj):
        super().__delete__(type(obj))


def _extract_user_data(user_info_dict):
    return {'phone': user_info_dict.get('phone'), 'user_code': user_info_dict.get('user_code'),
            'full_name': user_info_dict.get('user_name'), 'depts': user_info_dict.get('depts', [])}


def _query_info_from_service(url_suffix=None):
    """
    Query in Beidou service with url_suffix,
    and return the 'data' part of the response.

    Currently it looks like:
    [
        {
          "ffan_uid": "15000000005252376",
          "user_name": "\u6797\u5bff\u6021",
          "dept": "\u98de\u51e1\u4fe1\u606f\u516c\u53f8-\u6570\u5b57\u5546\u4e1a\u4e8b\u4e1a\u7fa4-\u6570\u5b57\u5546\u4e1a\u6280\u672f\u7814\u53d1\u7fa4-\u6570\u5b57\u5546\u4e1a\u7814\u53d1\u4e2d\u5fc3-B\u7aef\u4ea7\u54c1\u7814\u53d1\u90e8",
          "tel": "",
          "phone": "15210417188",
          "update_type": "3",
          "user_code": "linshouyi",
          "user_id": "10127"
        },
    ...............
    ]
    """
    result = {}
    if not settings.FFAN_STAFF_QUERY_URL:
        return result
    # url = "{0}&user_code={1}".format(settings.FFAN_STAFF_QUERY_URL, quote('username'))
    url = settings.FFAN_STAFF_QUERY_URL
    if url_suffix:
        url += url_suffix
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    try:
        c.perform()
        if status.is_success(c.getinfo(c.RESPONSE_CODE)):
            body = buffer.getvalue()
            data = json.loads(body.decode('utf8'))
            if data.get('data') and isinstance(data['data'], list):
                result = data['data']
    except (pycurl.error, ValueError) as e:
        gated_debug_logger.debug(str(e))
    finally:
        c.close()
    return result


def get_user_info(user_name):
    """
    Get user information from Beidou

    :param user_name: user ctx account
    :return: user information:
            {
                'phone': '1234556',
                'depts': ['飞凡', '网科集团', '技术体系', ....],
                'full_name': '张三',
                'user_code': 'zhangsan250',
                'departmentLevel1': '网科集团'，
                'departmentLevel2': '技术体系'
            }
    """
    result = {}
    url_suffix = "&user_code={0}".format(quote(user_name))
    query_data = _query_info_from_service(url_suffix)
    if query_data:
        result = _extract_user_data(query_data[0])
    return result


def get_or_create_department(dep_name, parent_dep=None):
    if not dep_name:
        return None
    return Department.objects.get_or_create(name=dep_name, parent=parent_dep)[0]


def get_or_create_departments(dep_array):
    result = None
    parent = None
    for dep in dep_array:
        # record last one, it's the lowest department.
        result = get_or_create_department(dep.get('dept_name'), parent)
        parent = result
    return result


def may_create_user_and_depts(user_name):
    result = None
    info = get_user_info(user_name)
    if info:
        dept = get_or_create_departments(info.get('depts'))
        result = get_user_model().objects.create(username=user_name,
                                                 phone=info.get('phone'),
                                                 full_name=info.get('full_name'),
                                                 email=user_name + settings.COMPANY_EMAIL_SUFFIX,
                                                 department=dept)
    return result


def _sync_user_info_from_staff_data(staff_data):
    created_count = 0
    try:
        for service_info in staff_data:
            user_data = _extract_user_data(service_info)
            if user_data:
                dep = get_or_create_departments(user_data.get('depts'))
                # create or update user and user info
                user, created = get_user_model().objects.get_or_create(username=user_data['user_code'])
                if created:
                    created_count += 1
                    gated_debug_logger.debug("User %s is created" % user_data['user_code'])
                user.phone = user_data.get('phone')
                # some departments don't follow this rule
                if user_data.get('departmentLevel2') != '快钱支付公司' and user_data.get('departmentLevel1') != '海鼎公司':
                    user.email = user_data['user_code'] + settings.COMPANY_EMAIL_SUFFIX

                if dep:
                    user.department = dep
                user.full_name = user_data.get('full_name')
                user.save()
        gated_debug_logger.debug("Created %d new users" % created_count)
    except Exception as e:
        gated_debug_logger.debug(str(e))


def _save_current_user_data_md5(data, prop_instance=None, md5_sum=None):
    gated_debug_logger.debug("Current user data md5 sum is %s. Saved to DB" % md5_sum)
    if not md5_sum:
        md5_sum = hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
    if not prop_instance:
        prop_instance, _ = Property.objects.get_or_create(key=LAST_TIME_STAFF_INFO_CHECKSUM)
    prop_instance.value = md5_sum
    prop_instance.save()
    gated_debug_logger.debug("Current user data md5 sum is %s. Saved to DB" % md5_sum)


@log_exception
def sync_user_info_to_db():
    staff_data = _query_info_from_service()
    _sync_user_info_from_staff_data(staff_data)
    _save_current_user_data_md5(staff_data)


@log_exception
def sync_user_info_to_db_if_changed():
    staff_data = _query_info_from_service()
    data_md5 = hashlib.md5(json.dumps(staff_data, sort_keys=True).encode('utf-8')).hexdigest()
    gated_debug_logger.debug("Staff data md5 is %s" % data_md5)

    current_md5_property, _ = Property.objects.get_or_create(key=LAST_TIME_STAFF_INFO_CHECKSUM)
    if data_md5 == current_md5_property.value:
        gated_debug_logger.debug("Data md5 is same as last time. Will not sync anything.")
        return

    _sync_user_info_from_staff_data(staff_data)
    _save_current_user_data_md5(staff_data, current_md5_property, data_md5)


def BpConfig(data):
    config_data = copy.deepcopy(data)

    if 'frequency' not in data:
        config_data['frequency'] = 1
    if 'platform' in data:
        del config_data['platform']
        config_data['clienttype'] = data['platform']
        if config_data['clienttype'] == IOS and 'download_url' not in data:
            return BenchmarkAPIView.get_response_by_code(1, msg="缺少必要参数download_url")
    else:
        config_data['clienttype'] = Android
    if 'upgrade_type' in data:
        del config_data['upgrade_type']
        config_data['iscompatible'] = data['upgrade_type']
    else:
        config_data['iscompatible'] = 1
    if 'download_url' in data:
        del config_data['download_url']
        config_data['url'] = data['download_url']

    try:
        check = AppVersions.objects.using("bpmysql").filter(
            version=config_data['version'], app_id=config_data['app_id'])
        check_client = Clientversion.objects.using("bpmysql").filter(
            version=config_data['version'], app_id=config_data['app_id'],
            clienttype=config_data['clienttype'])
    except Exception as e:
        return BenchmarkAPIView.get_response_by_code(1, msg=str(e))
    config_data['version_id'] = config_data['version']
    del config_data['version']

    if config_data['clienttype'] == IOS:
        config_data['channel'] = "app store"
        config_data['size'] = 0
        if not check:
            app_data = {}
            app_data['version'] = config_data['version_id']
            app_data['app_id'] = config_data['app_id']
            app_data['allow_users'] = ""
            app_data['range_dates'] = ""
            app_data['city_enable'] = 0
            app_data['status'] = Offline
            app_data['created_at'] = datetime.datetime.now()
            app_data['updated_at'] = datetime.datetime.now()
            try:
                AppVersions.objects.using("bpmysql").create(**app_data)
                config_data['createtime'] = datetime.datetime.now()
                config_data['minimumversion'] = 0
                config_data['status'] = Offline
                Clientversion.objects.using("bpmysql").create(**config_data)
            except Exception as e:
                return BenchmarkAPIView.get_response_by_code(2, msg=str(e))
        else:
            try:
                if not check_client:
                    config_data['createtime'] = datetime.datetime.now()
                    config_data['minimumversion'] = 0
                    config_data['status'] = Offline
                    Clientversion.objects.using("bpmysql").create(**config_data)
                else:
                    Clientversion.objects.using("bpmysql").filter(
                        version=config_data['version_id'], app_id=config_data['app_id'],
                        clienttype=config_data['clienttype']).update(**config_data)

            except Exception as e:
                return BenchmarkAPIView.get_response_by_code(3, msg=str(e))
    else:
        if not check:
            return BenchmarkAPIView.get_response_by_code(1, msg="指定 app 的version不存在")
        try:
            if not check_client:
                return BenchmarkAPIView.get_response_by_code(1, msg="指定version的app文件不存在")
            else:
                Clientversion.objects.using("bpmysql").filter(
                    version=config_data['version_id'], app_id=config_data['app_id']
                ).all().update(**config_data)
        except Exception as e:
            return BenchmarkAPIView.get_response_by_code(4, msg=str(e))
    return BenchmarkAPIView.get_response_by_code(200, msg="配置成功")


def BpOnline(data):

    online_data = copy.deepcopy(data)
    '''
    用户 112,33,555,6666
    次数限额[开始时间]-[结束时间]-[次数限制]-[当前次数]
    [["2016-11-21 12:00","2016-11-21 11:59","3"],["2016-11-21 12:00","2016-11-21 11:59","5"],["2016-11-21 12:00","2016-11-21 11:59","6"]]
    城市  120100,130100,130400
    '''
    # 城市存在时
    if 'city_enable' in data and data["city_enable"] == 0:
        online_data["citys"] = ""

    if "citys" in data and data["citys"]:
        online_data["city_enable"] = 1

    if 'platform' in data:
        del online_data['platform']
        clienttype = data['platform']
    else:
        clienttype = Android

    if "allow_users" in data and data["allow_users"] and ("channel" not in data or not data["channel"]):
        online_data["channel"] = "all"

    if "citys" in data and data["citys"] and ("channel" not in data or not data["channel"]):
        online_data["channel"] = "all"

    try:
        check = AppVersions.objects.using("bpmysql").filter(
            version=online_data['version'], app_id=online_data['app_id'])
        check_client = Clientversion.objects.using("bpmysql").filter(
            version=online_data['version'], app_id=online_data['app_id'],
            clienttype=clienttype)
    except Exception as e:
        return BenchmarkAPIView.get_response_by_code(2001, msg=str(e))

    if not check_client:
        return BenchmarkAPIView.get_response_by_code(2002, msg="指定app的渠道配置不存在")

    if not check:
        app_data = {}
        app_data['version'] = online_data['version']
        app_data['app_id'] = online_data['app_id']
        app_data['allow_users'] = ""
        app_data['range_dates'] = ""
        app_data['city_enable'] = 0
        app_data['status'] = Offline
        app_data['created_at'] = datetime.datetime.now()
        app_data['updated_at'] = datetime.datetime.now()
        try:
            AppVersions.objects.using("bpmysql").create(**app_data)
        except Exception as e:
            return BenchmarkAPIView.get_response_by_code(1001, msg=str(e))

    if "channel" in online_data and online_data['channel']:
        online_data['status'] = Online
        filter_data = {}
        filter_data["version"] = online_data['version']
        filter_data["app_id"] = online_data['app_id']
        filter_data["clienttype"] = clienttype

        if online_data['channel'] != "all":
            channel_list = re.split('[,]', online_data['channel'])
            filter_data["channel__in"] = channel_list
        del online_data['channel']
        try:
            Clientversion.objects.using("bpmysql").filter(**filter_data).update(status=Online)
            Clientversion.objects.using("bpmysql").exclude(**filter_data).update(status=Offline)
            AppVersions.objects.using("bpmysql").filter(
                version=online_data['version'], app_id=online_data['app_id']).update(**online_data)
        except Exception as e:
            return BenchmarkAPIView.get_response_by_code(1002, msg=str(e))
        msg = "上线成功"
    else:
        if "channel" in online_data:
            del online_data['channel']
        online_data['status'] = Offline
        online_data["citys"] = ""
        online_data["allow_users"] = ""
        online_data["range_dates"] = ""
        try:
            Clientversion.objects.using("bpmysql").filter(
                version=online_data['version'], app_id=online_data['app_id'],
                clienttype=clienttype).update(status=Offline)
            AppVersions.objects.using("bpmysql").filter(
                version=online_data['version'], app_id=online_data['app_id']).update(**online_data)
        except Exception as e:
            return BenchmarkAPIView.get_response_by_code(1003, msg=str(e))
        msg = "下线成功"
    return BenchmarkAPIView.get_response_by_code(200, msg=msg)


def BpConfigOnline(strategyid, version):
    try:
        stragegy_data = SnapshotOuterStrategy.objects.filter(id=strategyid).get()
    except Exception as e:
        return BenchmarkAPIView.get_response_by_code(1003, msg=str(e))
    config_data = {}
    config_data['version'] = version
    config_data['app_id'] = stragegy_data.gray_task.app.bp_app_id
    if not config_data['app_id']:
        config_data['app_id'] = 1
    config_data['frequency'] = stragegy_data.frequency
    config_data['upgrade_type'] = stragegy_data.is_compatible
    config_data['changelog'] = stragegy_data.change_log
    config_data['changelogimg'] = stragegy_data.change_log_img
    restlt = BpConfig(config_data)

    if restlt["status"] != 200:
        return restlt

    online_data = {}
    online_data['version'] = version
    online_data['app_id'] = stragegy_data.gray_task.app.bp_app_id
    if not online_data['app_id']:
        online_data['app_id'] = 1
    online_data['allow_users'] = stragegy_data.allow_users
    online_data['range_dates'] = stragegy_data.range_dates
    online_data['citys'] = stragegy_data.cities
    if stragegy_data.city_enable:
        online_data['city_enable'] = 1
    else:
        online_data['city_enable'] = 0
    online_data['channel'] = stragegy_data.channels
    return BpOnline(online_data)


def owner_app_id(user_id=-1):
    if user_id > 0:
        app_filter = {"type__name": UserGroupType.OWNER, "members": user_id}
    else:
        app_filter = {"type__name": UserGroupType.OWNER}
    try:
        result = UserGroup.objects.filter(**app_filter)
    except Exception as e:
        gated_debug_logger.debug(str(e))

    return [app.app_id for app in result]


def zc_set_jira_status(jira_id, flag=None, comment=None):
    try:
        url = JIRA_STATUS + jira_id + '/'
        if flag:
            put_info = {
                "status": flag,
                "comment": comment
            }
        else:
            put_info = {
                "comment": comment
            }
        result = Session().put(url=url, json=put_info)
        gated_debug_logger.debug(msg=result.text)
        if result.status_code == status.HTTP_200_OK:
            zc_status = json.loads(result.text)['data']['status']
            change_log = json.loads(result.text)['data']['changeLog']
            return zc_status, change_log
    except Exception as e:
        gated_debug_logger.error(msg=e)
        res = "Jira server error!"
        raise JiraError(msg=res)
    raise JiraError(msg=result.text)


def is_issue_from_weixin(issue):
    if issue.report_source:
        return True
    return False


def gen_weixin_params(issue, image_str):
    component = ''
    operator = issue.operator.username if issue.operator else ''
    other = json.loads(issue.other)
    severity = ZC_SCORE_TO_JIRA_SEVERITY[issue.score]
    business_type = other['businessType']
    occur_time = other['occurrenceTime']
    area = other['area']
    report_source = issue.report_source.name
    priority_desc = issue.priority.desc if issue.priority else ""
    detail_info = '反馈人: {0} \n' \
                  '手机品牌: {1} \n' \
                  '手机型号: {2} \n' \
                  '账号(手机号): {3} \n' \
                  '订单号: {4} \n' \
                  '产品版本: {5} \n' \
                  '所属广场: {6} \n' \
                  '描述: {7} \n' \
                  '附件: {8} \n'
    detail_info = detail_info.format(issue.creator, other['phoneBrand'],
                                     other['phoneType'], other['phoneNumber'], other['order'], other['version'],
                                     other['square'], issue.detail, image_str)
    params = {'businessType': business_type, 'occurrenceTime': occur_time, 'description': detail_info,
              'summary': issue.title, 'labels': issue.task.task_name, 'area': area, 'severity': severity,
              'issueSource': report_source, 'priority': priority_desc, 'components': component, 'operator': operator}
    if 'subBusinessType' in other:
        params['subBusinessType'] = other['subBusinessType']

    return params


def gen_zc_params(issue, image_str):
    component = issue.app.component.name
    operator = issue.operator.username if issue.operator else ''

    severity = ZC_SCORE_TO_JIRA_SEVERITY[issue.score]
    business_type = ''

    priority_desc = issue.priority.desc if issue.priority else ""

    report_source = ZC_REPORT_SOURCE
    occur_time = ''
    area = ''
    detail_arr = ['反馈人: {} '.format(issue.creator)]
    if issue.app_module:
        detail_arr.append('问题模块: {} '.format(issue.app_module.module_name))
    detail_arr.extend(['复现步骤: {} '.format(issue.detail), '问题截图: {} '.format(image_str)])
    detail_info = "\n".join(detail_arr)
    params = {'businessType': business_type, 'occurrenceTime': occur_time, 'description': detail_info,
              'summary': issue.title, 'labels': issue.task.task_name, 'area': area, 'severity': severity,
              'issueSource': report_source, 'priority': priority_desc, 'components': component, 'operator': operator}
    return params


def gen_params(issue):

    images = issue.images.all()
    image_str = ''

    for image in images:
        image_str = image_str + IMAGES_URL.format(image) + '\n'

    if is_issue_from_weixin(issue):
        '''如果report_source不为空，则此issue是来自微信小程序的问题'''
        params = gen_weixin_params(issue, image_str)
    else:
        params = gen_zc_params(issue, image_str)
    return params


def rtx_verify(username, password):
    result = True
    timeout_seconds = 30
    try:
        rsp = requests.post(url=RTX_VERIFY_HOST, data={'name': username, 'password': password},
                            timeout=timeout_seconds)
        rsp.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ConnectionError):
        result = False
    return result


def get_task_event_count(task_id, event_type_name):
    event_type = EventType.objects.get(name=event_type_name)
    id_list = EventTracking.objects.values('id').filter(type=event_type)
    result = usageProperty.objects.values('event_id').filter(event__in=id_list).filter(key='taskId',
                                                                                       value=task_id).count()
    return result


def issue_update(jira_id, issue, params):
    """
    更新jira_id对应的众测问题
    """
    issue_id = issue.id
    score = settings.JIRA_SEVERITY_TO_ZC_SCORE.get(params.get('severity'), '严重')
    priority = params.get('priority', '一般')
    status_name = params.get('status', '处理中')
    prev_status = issue.status
    jira_operator = params.get('operator')
    operator_obj = get_user_model().objects.get_or_create(username=jira_operator)[0] if jira_operator \
        else issue.operator
    other = {
        "businessType": params.get('businessType'),
        "area": params.get('area'),
        "components": params.get('components'),
        "solveType": params.get('solveType'),
        "changeLog": params.get('changeLog'),
        "comments": params.get('comments'),
    }
    if "subBusinessType" in params:
        other["subBusinessType"] = params['subBusinessType']
    try:
        if issue.other:
            old_other = json.loads(issue.other)
            for k, v in other.items():
                old_other.update({k: v})
            new_other = json.dumps(old_other)
        else:
            new_other = json.dumps(other)
        new_priority = IssuePriority.objects.get(desc=priority)
        new_status = IssueStatus.objects.get(name=status_name)
        if is_issue_from_weixin(issue):
            # 更新微信issue
            update_model_obj(issue, priority=new_priority, status=new_status, kst_unread_flag=True,
                             score=score, other=new_other, operator=operator_obj)
        else:
            # 更新众测issue
            taskName = params.get('labels')
            new_task = GrayTask.objects.get(task_name=taskName, app=issue.app)
            update_model_obj(issue, task=new_task, priority=new_priority, operator=operator_obj,
                             status=new_status, score=score, other=new_other)
        # 有可能需要发送微信小程序提醒
        may_send_wechat_notification(prev_status, issue, operator_name=params.get('preOperator', ''))
        gated_debug_logger.debug("Update issue %s successfully! Jira is %s." % (issue_id, jira_id))
    except Exception as e:
        gated_debug_logger.error("Update issue %s failed! Jira is %s, error msg: %s" % (issue_id, jira_id, e))
    finally:
        res = {
            "jiraId": jira_id,
            "issueId": issue_id
        }
    return res


def update_jira_to_zc():
    queryset = Issue.objects.exclude(status__name=IssueStatus.CLOSE_STATUS)
    jira_id_list = [g.jira_link for g in queryset if g.jira_link]
    if not jira_id_list:
        msg = 'No issue need to be synced.'
        gated_debug_logger.info(msg)
        return
    gated_debug_logger.info('Jira Id list to be synced: {}'.format(jira_id_list))
    batch = 5
    for i in range(0, int(len(jira_id_list) / batch) + 1):
        if batch * (i + 1) >= len(jira_id_list):
            id_list = jira_id_list[i * batch: len(jira_id_list)]
        else:
            id_list = jira_id_list[i * batch: (i + 1) * batch]
        gated_debug_logger.info('Jira Id list in this loop: {}'.format(id_list))
        result = requests.post(url=JIRA_UPDATE_LIST, json={"issues": id_list})
        if result.status_code == 200:
            gated_debug_logger.info(json.loads(result.text))
            if not json.loads(result.text).get('data'):
                gated_debug_logger.error('No data for id list {}'.format(id_list))
                continue
            data = json.loads(result.text)['data']['results']
            for d in data:
                try:
                    issue = Issue.objects.filter(jira_link=d['id']).first()
                    if issue:
                        result = requests.get(url=(JIRA_API_URL + d['id'] + '/'))
                        if result.json().get('status') == status.HTTP_200_OK:
                            params = result.json().get('data')
                            res = issue_update(d['id'], issue, params)
                            gated_debug_logger.debug(msg="Jira update successfully! issueId=%s ,jiraId=%s" %
                                                         (res.get("issueId", ""), res.get("jiraId", "")))
                except Exception as e:
                    gated_debug_logger.error(msg="Jira update failed! issueId=%s ,jiraId=%s; error msg:%s" %
                                                 (res.get("issueId", ""), res.get("jiraId", ""), e))
                    continue
        else:
            msg = "Get jira update list error,please check server.jiraList=%s" % jira_id_list
            gated_debug_logger.error(msg)
    return


def _cache_key(prefix, obj_pk):
    return "{}_{}".format(prefix, obj_pk)


def get_model_object_from_cache(model_class, obj_pk):
    result = None
    try:
        result = cache.get(_cache_key(model_class._meta.verbose_name, obj_pk)) if settings.USE_CACHE else None
    except Exception as e:
        gated_debug_logger.error(traceback.format_exc())
    finally:
        return result


def set_model_object_to_cache(model_class, obj_pk, value):
    if settings.USE_CACHE:
        cache.set(_cache_key(model_class._meta.verbose_name, obj_pk), value)


def remove_model_object_from_cache(model_class, obj_pk):
    if settings.USE_CACHE:
        cache.delete(_cache_key(model_class._meta.verbose_name, obj_pk))


def set_issues_to_cache():
    """
    set all issues content to cache, key is combination of
    model verbose and pk, value is the corresponding to_presentation()
    result of each object
    """
    if not settings.USE_CACHE:
        return
    count = 0
    for issue_obj in Issue.objects.all():
        try:
            # in case it was updated/deleted during the loop
            issue_obj.refresh_from_db()
        except Issue.DoesNotExist:
            # it was deleted
            continue
        from apps.issue.views import IssueViewSet
        set_model_object_to_cache(Issue, issue_obj.pk, IssueViewSet.serializer_class(issue_obj).data)
        count += 1
    gated_debug_logger.info("set {} issues to cache".format(count))


def get_from_cache(key):
    return cache.get(key) if settings.USE_CACHE else None


def set_to_cache(key, value, timeout=None):
    return cache.set(key, value, timeout) if settings.USE_CACHE else None


def clear_cache_with_prefix(prefix):
    # this method works for redis cache backend specifically
    if settings.USE_CACHE:
        cache.delete_pattern(prefix + '*')


def update_model_obj(obj, **update_data):
    for key, value in update_data.items():
        setattr(obj, key, value)
    obj.save()


def update_with_emitting_save_signals(queryset, **update_data):
    """
    normal update will not emit post_save/pre_save signals.
    so loop the queryset and save one by one.
    :param queryset:
    :param update_data:
    :return:
    """
    for obj in queryset:
        update_model_obj(obj, **update_data)


APP_OWNERS_CACHE_COMMON_PREFIX = 'app_owners'


def _app_owners_cache_prefix(app_id):
    return "{}:{}".format(APP_OWNERS_CACHE_COMMON_PREFIX, app_id)


def cache_app_owners():
    if not settings.USE_CACHE:
        return
    try:
        for user_group in UserGroup.objects.filter(type__name=UserGroupType.OWNER):
            owners = [member for member in user_group.members.all()]
            if owners:
                cache.set(_app_owners_cache_prefix(user_group.app.id), owners,
                          2 * settings.APP_OWNER_CACHE_MINUTES * 60)
                gated_debug_logger.info("cached {} for app id {} ".format(str(owners), user_group.app.id))
    except Exception as e:
        gated_debug_logger.error(traceback.format_exc())


def get_cached_app_owners(app_id):
    result = []
    try:
        result = cache.get(_app_owners_cache_prefix(app_id), []) if settings.USE_CACHE else []
    except Exception as e:
        gated_debug_logger.error(traceback.format_exc())
    finally:
        return result


def is_app_owner(user, app_id):
    result = False
    if settings.USE_CACHE:
        try:
            owners = get_cached_app_owners(app_id)
            if owners:
                return user in owners
        except Exception as e:
            gated_debug_logger.error(traceback.format_exc())
    app = App.objects.filter(pk=app_id).first()
    if app:
        result = UserGroup.is_owner(user, app)
    return result


def get_task_detail_page_path(task):
    return settings.TASK_DETAIL_PAGE.format(app_id=task.app_id, task_id=task.id)


def get_task_file_issue_page_path(task):
    return settings.TASK_FILE_ISSUE_PAGE.format(app_id=task.app_id, task_id=task.id)


def get_model_field(model_name):
    """
    获取model 指定字段的 verbose_name属性值
    """
    field_dic = {}
    for field in model_name._meta.fields:
        field_dic[field.name] = field.verbose_name
    return field_dic


def _compare(oldstr, newstr, field):
    """
    生成操作日志详细记录
    :param oldstr: 原值
    :param newstr: 新值
    :param field: 目标字段
    :return: item
    """
    item = {}

    if isinstance(newstr, list):  # 将list转为str类型，list对象存储到数据库后，为str类型
        newstr = str(newstr)

    if oldstr != newstr:
        item = {
            "fromString": oldstr,
            "field": field,
            "toString": newstr
        }
    return item


def format_zc_change_log(user, content):
    """
    格式化操作日志
    :param user: 登陆用户
    :param content: 操作日志
    :return: new_zc_change_log
    """
    new_zc_change_log = {
        "wanxin": user.username,
        "author": user.full_name,
        "created": datetime.datetime.now().isoformat(),
        "items": content
    }
    return new_zc_change_log


def generate_change_log(old_model_object, update_fields_dict, user):
    """
    操作日志
    :param old_model_object: 旧的model对象实例
    :param update_fields_dict: 更新的字段键值对--字典格式
    :param user: 登陆用户
    :return:
    """
    content = []

    if old_model_object and update_fields_dict:
        field_dict = get_model_field(old_model_object)
        for key, val in update_fields_dict.items():
            rtn = None
            if key == 'extFields':
                old_value = dict((ext.field.name, ext.value) for ext in old_model_object.ext_values.all())
                rtn = _compare(str(old_value), val, key)
            elif isinstance(val, dict):  # 获取外键表的字段值
                _model = getattr(old_model_object, key)
                for _key, _val in val.items():  # _key->外键名
                    if _key != "id":
                        rtn = _compare(getattr(_model, _key), _val, field_dict[key])
            elif isinstance(val, IssueStatus):
                old_val = getattr(old_model_object, key)
                rtn = _compare(old_val.name, val.name, field_dict[key])
            elif isinstance(val, IssuePriority):
                old_val = getattr(old_model_object, key)
                rtn = _compare(old_val.desc, val.desc, field_dict[key])
            elif key == 'score':
                rtn = _compare(getattr(old_model_object, key), int(val), field_dict[key])
            elif key == 'images':
                old_images = []
                new_images = []
                for old_image in old_model_object.images.all():
                    old_images.append(old_image.image_id)
                for new_image in val:
                    new_images.append(new_image.image_id)
                rtn = _compare(str(old_images), new_images, "images")
            elif isinstance(val, get_user_model()):
                old_val = getattr(old_model_object, key)
                if old_val:
                    rtn = _compare(old_val.username, val.username, field_dict[key])
                else:
                    rtn = _compare("", val.username, field_dict[key])
            else:
                rtn = _compare(getattr(old_model_object, key), val, field_dict[key])
            if rtn:
                content.append(rtn)

    #  存储日志
    if content:
        if not old_model_object.zc_change_logs:
            # no logs currently
            jira_info_list = [format_zc_change_log(user, content)]
        else:
            jira_info_list = json.loads(old_model_object.zc_change_logs)
            if isinstance(jira_info_list, list):
                jira_info_list.insert(0, format_zc_change_log(user, content))
            else:
                raise ValueError('zcChangeLogs field has wrong format')
        old_model_object.zc_change_logs = json.dumps(jira_info_list)
        old_model_object.save()


def format_comment(user, comment):
    new_comment = {
        "wanxin": user.username,
        "startTime": datetime.datetime.now().isoformat(),
        "info": comment,
        "name": user.full_name,
        "endTime": datetime.datetime.now().isoformat(),
        "email": user.email
    }
    return new_comment


def update_issue_comment(issue, comment, kst):
        comments_field = 'comments'
        jira_info = issue.other
        if jira_info:
            jira_info_dict = json.loads(jira_info)
            # no comments currently
            if not jira_info_dict.get(comments_field):
                jira_info_dict[comments_field] = [comment]
            elif isinstance(jira_info_dict.get(comments_field), list):
                jira_info_dict[comments_field].insert(0, comment)
            # have 'comments' field but not a list
            else:
                raise ValueError('comments field has wrong format')
        # no jira info for this issue at all
        else:
            jira_info_dict = {comments_field: [comment]}
        if kst == KE_SU_TONG:
            # 当微信端添加comments，此时issue未转jira 且 plat_unread_flag为false，将plat_unread_flag置True
            if not issue.jira_link and not issue.plat_unread_flag:
                issue.plat_unread_flag = True
        else:
            # 当众测端添加comments，不管issue是否转jira，如果kst_unread_flag为false，将kst_unread_flag置True
            if not issue.kst_unread_flag:
                issue.kst_unread_flag = True

        issue.other = json.dumps(jira_info_dict)
        issue.save()
        result = jira_info_dict[comments_field]

        return result


def auto_close_issue():
    base_time = datetime.datetime.now() + datetime.timedelta(days=-10)
    queryset = Issue.objects.filter(Q(jira_link__exact="") | Q(jira_link__isnull=True), updated_time__lte=base_time,
                                    report_source__isnull=False, status=IssueStatus.objects.get(name="验证"))
    if not queryset:
        msg = 'No issue should be auto closed.'
        gated_debug_logger.debug(msg)
        return
    for issue in queryset:
        try:
            # 设置状态
            issue.status = IssueStatus.objects.get(name="关闭")
            issue.save()
            # 增加comment
            comment = "AutoClosed: True. \n关闭原因：自动关闭。\n 说 明：验证状态停留时间超过10天自动关闭。"
            new_comment = format_comment(issue.creator, comment)
            update_issue_comment(issue, new_comment, KE_SU_TONG)
            msg = "Auto close issue %s successfully!" % issue.id
            gated_debug_logger.info(msg)
        except Exception as e:
            msg = "Auto close issue %s failed! error msg = %s." % (issue.id, e)
            gated_debug_logger.error(msg)
            continue
    return


def _extract_business_module_info(issue):
    result = ''
    if issue and issue.other:
        try:
            other_dict = json.loads(issue.other)
            result = '业务模块: {}'.format(other_dict.get('businessType', '-'))
            result += '\r\n业务子模块: {}'.format(other_dict.get('subBusinessType', '-'))
        except json.JSONDecodeError as e:
            gated_debug_logger.error('_extract_business_module_info failed: {}, other is {}'.format(str(e)),
                                     issue.other)
    return result


def send_wechat_notification(issue, open_id, form_id, operator_obj, operator_name):
    try:
        response = requests.get(WEIXIN_AUTH_TOKEN_API_URL)
        if response.status_code != status.HTTP_200_OK:
            gated_debug_logger.error('request {} failed. response: {}'.format(WEIXIN_AUTH_TOKEN_API_URL, str(response)))
            return
        access_token = response.json().get('access_token')
        if not access_token:
            gated_debug_logger.error('get access_token failed, response: {}'.str(response))
            return
        if not operator_name and operator_obj:
            operator_name = operator_obj.username

        business_module_info = _extract_business_module_info(issue)
        notification_url = WEIXIN_NOTIFICATION_URL.format(access_token)
        post_data = {"touser": open_id,  # openid
                     "template_id": "81SRZ8SJppw7w5UPqkr9TmlvXNg9bHHQtegYesJl5xE",
                     "page": "pages/issue/detail/detail?id={}".format(issue.id),
                     "form_id": form_id,
                     "data": {
                         "keyword1": {
                             "value": issue.title,  # 摘要
                             "color": "#173177"
                         },
                         "keyword2": {
                             "value": operator_name,  # 解决人
                             "color": "#173177"
                         },
                         "keyword3": {
                             "value": '{}'.format(business_module_info),  # 模块与解决类别拼接
                             "color": "#173177"
                         }
                     }}
        response = requests.post(notification_url, json=post_data)
        if response.status_code != status.HTTP_200_OK:
            gated_debug_logger.error('sending notification of issue {} failed. response: {}'.format(
                issue.id, str(response)))
        else:
            gated_debug_logger.info('sending notification of issue {} returned OK, response is {}'.format(
                issue.id, str(response)))
    except requests.RequestException as e:
        gated_debug_logger.error('sending_wechat_notification failed with requests error {}'.format(str(e)))
    except Exception as e:
        gated_debug_logger.error('sending_wechat_notification failed {}'.format(str(e)))


def may_send_wechat_notification(prev_status, issue, operator_obj=None, operator_name=None):
    """
    :param prev_status: previous status. IssueStatus instance
    :param issue: Issue instance.
    :param operator_obj: issue's operator. User instance
    :param operator_name: user name of a issue's operator
    :return:
    """
    trigger_status = IssueStatus.VERIFYING_STATUS
    # assume form id is stored in issue ext filed 'form_id'
    form_id_field_name = 'formId'
    # 需要状态变为验证
    if issue.status == prev_status or issue.status.name != trigger_status or not is_issue_from_weixin(issue):
        return

    open_id = issue.creator.weixin_openid
    if open_id:
        form_id = issue.get_ext_field_value(form_id_field_name)
        if not form_id:
            gated_debug_logger.debug('issue {} does not have form id info'.format(issue.id))
            return

        send_wechat_notification(issue, open_id, form_id, operator_obj, operator_name)


def may_log_exception_to_sentry(message=None):
    """
    if USE_SENTRY is enabled, send exception to sentry and log it
    with logger anyway
    :param message: extra message
    :return:
    """
    if settings.USE_SENTRY:
        sentry_client.captureException()
    if message:
        gated_debug_logger.error(message)


def jira_issue_is_avaliable(jira_id):
    jira_detail_url = "{}{}/".format(JIRA_API_URL, jira_id)
    result = True
    try:
        rsp = requests.get(jira_detail_url).json()
        if rsp.get("status") != status.HTTP_200_OK:
            result = False
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ConnectionError) as e:
        may_log_exception_to_sentry(str(e))
        result = False
    return result


def try_delete_from_statplat(issue_id, jira_id):
    result = True
    delete_api_name = 'zhongceIssue'
    api = "{}{}/{}/".format(STATPLAT_API_URL, delete_api_name, issue_id)
    try:
        response = requests.delete(api, json={'jiraId': jira_id},
                                   headers={'Authorization': 'Token {}'.format(STATPLAT_TOKEN)})
        if response.status_code != status.HTTP_200_OK:
            raise requests.exceptions.HTTPError(
                'Return HTTP code {} when deleting issue {}'.format(response.status_code, issue_id))

        api_status = response.json().get("status")
        if api_status == status.HTTP_401_UNAUTHORIZED:
            raise requests.exceptions.HTTPError('Invalid token when deleting issue {}'.format(issue_id))

        # 也许已经被删除了或未来的及同步，合法情况
        if api_status != status.HTTP_200_OK:
            gated_debug_logger.info(response.json())
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ConnectionError) as e:
        may_log_exception_to_sentry(str(e))
        _record_issue_to_delete_in_statplat(issue_id, jira_id)
        result = False
    return result


STATPLAT_CACHE_KEY_PREFIX = 'STATPLAT'


def _record_issue_to_delete_in_statplat(issue_id, jira_id):
    if settings.USE_CACHE:
        cache.set(_cache_key(STATPLAT_CACHE_KEY_PREFIX, issue_id), (issue_id, jira_id))


def delete_issues_from_statplat():
    if settings.USE_CACHE:
        for key in cache.keys(_cache_key(STATPLAT_CACHE_KEY_PREFIX, '*')):
            if try_delete_from_statplat(*cache.get(key)):
                cache.delete(key)
                gated_debug_logger.info("delete key {} from local cache".format(key))


def get_jira_status(jira_id):
    jira_detail_url = "{}{}/".format(JIRA_API_URL, jira_id)
    result = None
    try:
        rsp = requests.get(jira_detail_url).json()
        if rsp.get("data", {}).get("status") == status.HTTP_200_OK:
            result = rsp.get("data", {}).get("data").get("status")
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout, ConnectionError) as e:
        may_log_exception_to_sentry(str(e))
    return result


def check_issue_status_with_jira():
    if CHECK_ISSUE_STATUS:
        jira_dict = dict()
        for issue in Issue.objects.all():
            try:
                # 检查issue状态和对应的jira状态是否一致
                if issue.jira_link:
                    issue_id = issue.id
                    issue_status = issue.status
                    jira_status = get_jira_status(issue.jira_link)
                    if issue_status != jira_status:
                        jira_dict[issue_id] = issue.jira_link
            except Exception as e:
                msg = "check issue %s status error msg = %s." % (issue.id, e)
                may_log_exception_to_sentry(msg)
                continue
        if jira_dict:
            subject = "issue和jira状态不一致"
            context = "亲爱管理员您好，" \
                      "以下issues和对应的jiras：%s状态不一致" \
                      "请及时进行处理\n" % str(jira_dict)
            send_email(ADMIN_EMAILS, subject=subject, context=context)
        else:
            gated_debug_logger.info("zhongce and jira issues is consistent")
    return
