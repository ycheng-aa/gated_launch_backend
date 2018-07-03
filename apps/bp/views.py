from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from .models import AppVersions, Clientversion
from apps.auth.models import Role
from apps.utils.utils import BpConfig, BpOnline
import subprocess
import sys

# Create your views here.

# 接口文档
#
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18521346#BP后台-版本管理接口-查询版本列表接口
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18521346#BP后台-版本管理接口-app版本配置接口
# http://wiki.ffan.biz/pages/viewpage.action?pageId=18521346#BP后台-版本管理接口-app版本上线接口


class BpVersionView(BenchmarkAPIView):
    '''
    查询版本列表接口
    '''
    access = {
        'get': 'user',
        'post': None,
        'put': None,
        'delete': None
    }
    primary_model = AppVersions
    using = 'bpmysql'

    def get_model(self):
        if 'version' in self.uri_params:  # 查询单个版本信息
            self.select_related = ['clientversion_set']
        self.params['order_by'] = '-updated_at'
        return super().get_model()


class BpVersionPlatform(BenchmarkAPIView):
    '''
    按平台查询版本信息
    '''
    access = {
        'get': 'user',
        'post': None,
        'put': None,
        'delete': None
    }
    primary_model = Clientversion
    using = 'bpmysql'

    def get_model(self):
        self.params['order_by'] = '-createtime'
        return super().get_model()


class BpVersionConfig(BenchmarkAPIView):
    '''
    app版本配置接口
    '''
    access = {
        'get': None,
        'post': (Role.APP_OWNER, Role.ADMIN),
        'put': None,
        'delete': None
    }

    def post_model(self):
        for i in ('version', 'app_id', 'changelog'):
            if i not in self.data:
                return self.get_response_by_code(1, msg="缺少必要参数%s" % i)
        return BpConfig(self.data)


class BpVersionOnline(BenchmarkAPIView):
    '''
    app版本上线接口
    '''
    access = {
        'get': None,
        'post': (Role.APP_OWNER, Role.ADMIN),
        'put': None,
        'delete': None
    }

    def post_model(self):
        for i in ('version', 'app_id'):
            if i not in self.data:
                return self.get_response_by_code(1, msg="缺少必要参数%s" % i)
        return BpOnline(self.data)


class BpVersionChannel(BenchmarkAPIView):
    '''
    app版本渠道接口
    '''
    access = {
        'get': 'user',
        'post': None,
        'put': None,
        'delete': None
    }

    methods_not_need_convert_keys_for_response = ['get']

    @staticmethod
    def qconf_cmd(cmd):
        res = {}
        qconf = "/usr/local/qconf/bin/qconf "
        result = subprocess.Popen(qconf + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (stdoutdata, stderrdata) = result.communicate()
        if result.returncode > 0:
            res['error_code'] = result.returncode
            res['cmd'] = qconf + cmd
            if sys.platform == "win32":
                res['error_msg'] = "Please check qconf . " + bytes.decode(stdoutdata, 'gbk')
            else:
                res['error_msg'] = "Please check qconf . " + bytes.decode(stdoutdata)
            return res
        return bytes.decode(stdoutdata)

    def get_model(self):
        channel_list = {}
        # 遍历渠道分类，目前有yunpos 和 ffan  两个分类
        app = self.qconf_cmd('get_batch_keys "/bp/app-upgrade/android_channels/"')
        if isinstance(app, dict):
            return self.get_response_by_code(1011, data=app)
        for line in app.split("\n"):
            if not line:
                continue
            channel_list.setdefault(line, {})
            # 遍历不同分类下的渠道名称，为英文名
            channel = self.qconf_cmd('get_batch_keys "/bp/app-upgrade/android_channels/' + line + '/"')
            if isinstance(channel, dict):
                return self.get_response_by_code(1011, data=channel)
            for line_name in channel.split("\n"):
                if not line_name:
                    continue
                # 获取渠道对应的中文名称
                channel_name = self.qconf_cmd('get_conf "/bp/app-upgrade/android_channels/' + line + '/' + line_name + '"')
                if isinstance(channel_name, dict):
                    return self.get_response_by_code(1011, data=channel_name)
                # 将配置信息赋值到对应 渠道名为key 的字典
                channel_list[line][line_name] = channel_name.split("\n")[0]
        return self.get_response_by_code(200, data=channel_list)
