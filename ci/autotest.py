#!/usr/bin/python
# -*-coding:utf-8-*-
import sys
import requests
import json
sys.path.append("./")
from gated_launch_backend.settings_test import ZHONGCE_SIT_URL, JIRA_SIT_URL


def get_reponse_res(response):
    if response.status_code == 200:
        res = json.loads(response.text)
    else:
        res = ""
    return res


def login():
    # 测试登录是否成功
    try:
        url = "%sapi/v1/login/" % ZHONGCE_SIT_URL
        print(url)
        data = json.dumps(
            {"username": "root",
             "password": "123456aa",
             "idCode": "bmapp"})
        response = requests.post(url, data=data, headers={"Content-Type": "application/json"})
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200:
                print("login successful")
                print(res['data'])
                token = res['data']['token']
                return token
            else:
                msg = res['msg']
                print("login failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("login exception：%s" % e)
        sys.exit(1)


def create_app():
    # 新建app;
    try:
        url = "%sapi/v1/apps/" % ZHONGCE_SIT_URL
        print(url)
        data = json.dumps(
            {"name": "autotest_app1",
             "desc": "test for autotest app",
             "image": "T1NUhvB5C_1RCvBVdK",
             "types": [1]})
        response = requests.post(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['name'] == "autotest_app1":
                print("create app successful")
                print(res['data'])
                app_id = res['data']['id']
                app_name = res['data']['name']
                return app_id, app_name
            else:
                msg = res['msg']
                print("create app failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("create app exception：%s" % e)
        sys.exit(1)


def get_app_detail(app_id, app_name):
    # 查询新建app的详情;
    try:
        url = "%sapi/v1/apps/%s/" % (ZHONGCE_SIT_URL, app_id)
        print(url)
        response = requests.get(url, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['name'] == app_name:
                print("get app detail successful")
                print(res['data'])
            else:
                msg = res['msg']
                print("get app detail failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("get app detail exception：%s" % e)
        sys.exit(1)


def get_app_owner_group_id(app_id, app_name):
    # 获取app的owner组的id;
    try:
        url = "%sapi/v1/userGroups/" % ZHONGCE_SIT_URL
        print(url)
        params = {"appId": app_id, "type": "owner"}
        response = requests.get(url, params=params, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['results'][0]['appName'] == app_name:
                print("get app owner group id successful")
                print(res['data'])
                app_owner_group_id = res['data']['results'][0]['id']
                return app_owner_group_id
            else:
                msg = res['msg']
                print("get app owner group id failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("get app owner group id exception：%s" % e)
        sys.exit(1)


def add_auto_test_user_to_app_owner(app_owner_group_id):
    # 将自动化测试用户增加到测试app的owner;
    try:
        url = "%sapi/v1/userGroups/%s/members/" % (ZHONGCE_SIT_URL, app_owner_group_id)
        print(url)
        data = json.dumps({"account": "root"})
        response = requests.post(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['account'] == "root":
                print("add auto test user to app owner group successful")
                print(res['data'])
            else:
                msg = res['msg']
                print("add auto test user to app owner group failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("add auto test user to app owner group exception：%s" % e)
        sys.exit(1)


def create_task(app_id):
    # 在app下新建task;
    try:
        url = "%sapi/v1/tasks/" % ZHONGCE_SIT_URL
        print(url)
        data = json.dumps(
            {"name": "任务管理自动化测试",
             "appId": app_id,
             "startDate": "2017-10-31",
             "endDate": "2017-11-08",
             "innerStrategyList": [{"id": 1, "pushContent": "innerStrategy1"},
                                   {"id": 1, "pushContent": "innerStrategy2"},
                                   {"id": 1, "pushContent": "innerStrategy3"},
                                   {"id": 1, "pushContent": "innerStrategy4"}],
             "outerStrategyList": [1, 2],
             "imageId": "T1NUhvB5C_1RCvBVdK",
             "versionDesc": "自动化测试任务",
             "awardRule": "autotest",
             "contact": "autotest"
             })
        response = requests.post(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['name'] == "任务管理自动化测试":
                print("create task successful")
                print(res['data'])
                task_id = res['data']['id']
                task_name = res['data']['name']
                return task_id, task_name
            else:
                msg = res['msg']
                print("create task failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("create task exception：%s" % e)
        sys.exit(1)


def get_task_detail(task_id, task_name):
    # 查询新建任务的详情;
    try:
        url = "%sapi/v1/tasks/%s/" % (ZHONGCE_SIT_URL, task_id)
        print(url)
        response = requests.get(url, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['name'] == task_name:
                print("get task detail successful")
                print(res['data'])
            else:
                msg = res['msg']
                print("get task detail failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("get task detail exception: %s" % (e))
        sys.exit(1)


def update_task(task_id):
    # 更新任务详情;
    try:
        url = "%sapi/v1/tasks/%s/" % (ZHONGCE_SIT_URL, task_id)
        print(url)
        data = json.dumps(
            {"name": "任务管理自动化测试",
             "appId": app_id,
             "startDate": "2017-10-31",
             "endDate": "2017-11-08",
             "innerStrategyList": [{"id": 1, "pushContent": "innerStrategy1"},
                                   {"id": 1, "pushContent": "innerStrategy2"},
                                   {"id": 1, "pushContent": "innerStrategy3"},
                                   {"id": 1, "pushContent": "innerStrategy4"}],
             "outerStrategyList": [1, 2],
             "imageId": "T1NUhvB5C_1RCvBVdK",
             "versionDesc": "test for put request",
             "awardRule": "autotest",
             "contact": "autotest"
             })
        response = requests.put(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['versionDesc'] == "test for put request":
                print("update task successful")
                print(res['data'])
            else:
                msg = res['msg']
                print("update task failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("update task exception: %s" % e)
        sys.exit(1)


def create_issue_zhongce(app_id, task_id):
    # 新建普通众测平台issue;
    try:
        url = "%sapi/v1/issues/" % ZHONGCE_SIT_URL
        print(url)
        data = json.dumps(
            {"appId": app_id,
             "taskId": task_id,
             "title": "autotest",
             "detail": "test for autotest"
             })
        response = requests.post(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['title'] == "autotest":
                print("create issue successful")
                print(res['data'])
                issue_id_zhongce = res['data']['id']
                return issue_id_zhongce
            else:
                msg = res['msg']
                print("create issue failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("create issue exception: %s" % e)
        sys.exit(1)


def get_issue_detail(issue_id):
    # 查询issue;
    try:
        url = "%sapi/v1/issues/%s/" % (ZHONGCE_SIT_URL, issue_id)
        print(url)
        response = requests.get(url, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['title'] == "autotest":
                print("get issue detail successful")
                print(res['data'])
                return res['data']
            else:
                msg = res['msg']
                print("get issue detail failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("get issue detail exception: %s" % e)
        sys.exit(1)


def update_issue_detail(issue_id, app_id, task_id):
    # 更新issue;
    try:
        url = "%sapi/v1/issues/%s/" % (ZHONGCE_SIT_URL, issue_id)
        print(url)
        data = json.dumps(
            {"appId": app_id,
             "taskId": task_id,
             "title": "autotest",
             "detail": "test for autotest update issue api"
             })
        response = requests.put(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['detail'] == "test for autotest update issue api":
                print("update issue successful")
                print(res['data'])
            else:
                msg = res['msg']
                print("update issue failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("update issue exception: %s" % (e))
        sys.exit(1)


def issue_to_jira(issue_id):
    # issue转jira;
    try:
        url = "%sapi/v1/issueToJira/?issueId=%s" % (ZHONGCE_SIT_URL, issue_id)
        print(url)
        response = requests.get(url, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['issueId'] == issue_id:
                print("issue to jira successful")
                print(res['data'])
                jira_id = res['data']['jiraId']
                return jira_id
            else:
                msg = res['msg']
                print("issue to jira failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("issue to jira exception: %s" % e)
        sys.exit(1)


def create_issue_weixin(app_id, task_id):
    # 新建微信小程序转来的issue;
    try:
        url = "%sapi/v1/issues/" % ZHONGCE_SIT_URL
        print(url)
        data = json.dumps(
            {"appId": app_id,
             "taskId": task_id,
             "title": "autotest",
             "detail": "test for autotest create weixin issue",
             "reportSource": "四大区运营",
             "score": "非常严重",
             "other": "{\"phoneNumber\":\"15921372876\",\"order\":\"1234568\",\"phoneType\":\"find v5\",\"version\":\"0928gray\",\"square\":\"通州万达\",\"occurrenceTime\":\"2017-09-01T09:01:00.000+0800\",\"area\":\"ALL\",\"phoneBrand\":\"Vivo\",\"severity\":\"非常严重\",\"businessType\":\"停车\"}",
             "images": ["T1ZQYvB5xT1RCvBVdK"]
             })
        response = requests.post(url, data=data, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200 and res['data']['title'] == "autotest":
                print("create weixin issue successful")
                print(res['data'])
                issue_id_weixin = res['data']['id']
                return issue_id_weixin
            else:
                msg = res['msg']
                print("create weixin issue failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("create weixin issue exception: %s" % (e))
        sys.exit(1)


def update_jira_status(jira_id):
    # 更新测试环境jira信息;
    try:
        url = "%sapi/v1/CcStatus/%s/" % (JIRA_SIT_URL, jira_id)
        print(url)
        data = json.dumps({"status": "处理中"})
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, data=data, headers=headers)
        res = json.loads(response.text)
        status = response.status_code
        if status == 200 and res['data']['status'] == "处理中":
            print("update jira status successful")
            print(res['data'])
        else:
            response.raise_for_status()
    except Exception as e:
        print("update jira status exception: %s" % (e))
        sys.exit(1)


def delete_app(app_id):
    # 删除创建的app,即可自动删除相关联的tasks和issues;
    try:
        url = "%sapi/v1/apps/%s/" % (ZHONGCE_SIT_URL, app_id)
        print(url)
        response = requests.delete(url, headers=HEADERS)
        res = get_reponse_res(response)
        if res:
            if res['status'] == 200:
                print("delete app successful")
            else:
                msg = res['msg']
                print("delete app failed :%s" % msg)
                sys.exit(1)
        else:
            response.raise_for_status()
    except Exception as e:
        print("delete app exception: %s" % (e))
        sys.exit(1)


if __name__ == "__main__":
    print("----------------start zhongce autotest---------------------")
    token = login()
    HEADERS = {"Content-Type": "application/json", "Authorization": "token %s" % token}
    app_id, app_name = create_app()
    print("1.创建app成功")
    get_app_detail(app_id, app_name)
    print("2.查询app详情成功")
    app_owner_group_id = get_app_owner_group_id(app_id, app_name)
    print("3.获取app的owner组id成功")
    add_auto_test_user_to_app_owner(app_owner_group_id)
    print("4.将自动化测试的用户加入app的owner组成功")
    task_id, task_name = create_task(app_id)
    print("5.创建任务成功")
    get_task_detail(task_id, task_name)
    print("6.查询任务详情成功")
    update_task(task_id)
    print("7.更新任务成功")
    # 关于众测平台本身问题的测试
    print("---------------8.开始关于众测平台本身问题的测试-------------")
    issue_id_zhongce = create_issue_zhongce(app_id, task_id)
    print("8.1模拟创建众测平台本身的issue成功")
    get_issue_detail(issue_id_zhongce)
    print("8.2查询众测平台issue详情成功")
    update_issue_detail(issue_id_zhongce, app_id, task_id)
    print("8.3更新众测平台issue详情成功")
    jira_id_zhongce = issue_to_jira(issue_id_zhongce)
    print("8.4众测平台的issue转成jira成功")
    # 关于从微信小程序转过来的问题的相关测试
    print("--------------9.开始关于从微信小程序转过来的问题的测试-------------")
    issue_id_weixin = create_issue_weixin(app_id, task_id)
    print("9.1模拟创建微信转众测的issue成功")
    issue_weixin_detail = get_issue_detail(issue_id_weixin)
    print("9.2查询微信转众测的issue的详情成功")
    jira_id_weixin = issue_to_jira(issue_id_weixin)
    print("9.3将微信转众测的issue转成jira成功")
    update_jira_status(jira_id_weixin)
    print("9.4更新jira中问题的状态成功！")
    delete_app(app_id)
    print("10.清除相关数据成功")
