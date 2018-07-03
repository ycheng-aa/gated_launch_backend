import numbers
import re
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
import xlrd
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from apps.user_group.models import UserGroup

from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from .models import Award, Awardee
from apps.auth.models import Role
from apps.utils.utils import owner_app_id, may_create_user_and_depts


# 格式化queryset，将'__'替换为'_'
def queryset_format(queryset):
    sub_data = queryset['data']
    for item in sub_data:
        for k in item.keys():
            replace_dict = dict()
            if '__' in k:
                replace_dict[k.replace('__', '_')] = item[k]
                item.pop(k)
                item.update(replace_dict)
    return queryset


class AwardView(BenchmarkAPIView):
    """
    激励管理-获奖信息接口
    """
    access = {
        'get': 'user',
        'post': (Role.APP_OWNER, Role.ADMIN),
        'put': (Role.APP_OWNER, Role.ADMIN),
        'delete': (Role.APP_OWNER, Role.ADMIN),
    }
    primary_model = Award
    select_related = ['app', 'image']
    values_white_list = False
    values = ['app__id', 'app__desc']

    def get_model(self):
        if 'pk' in self.uri_params:  # 查询单个版本信息
            self.select_related.append('awardee_set__user')
            self.values.append('awardee_set.id')
            self.values.append('awardee_set.username')
            self.values.append('awardee_set.phone')
            self.values.append('awardee_set.desc')
            return queryset_format(super().get_model())
        elif self.params.get("app"):
            if not self.params.get("_source") or self.params.get("_source") not in ["bpplat", "userplat"]:
                # app参数存在但无_source 参数时 且不是bpplat或userplat时, 返回无此权限
                return self.get_response_by_code(1016)
            if self.params.get("_source") == "bpplat" and \
                    (not self.request.user.is_owner() or
                        int(self.params["app"]) not in owner_app_id(self.request.user.id)):
                # _source 为"bpplat" 身份非owner时,不能访问非自己的app下激励信息
                return self.get_response_by_code(1016)
            del self.params["_source"]
            return queryset_format(super().get_model())
        else:
            # 必须要有 'app' 参数，否则不能访问
            return self.get_response_by_code(1016)


class AwardeeView(BenchmarkAPIView):
    """
    激励管理-获奖人信息接口
    """
    access = {
        'get': 'user',
        'post': (Role.APP_OWNER, Role.ADMIN),
        'put': (Role.APP_OWNER, Role.ADMIN),
        'delete': (Role.APP_OWNER, Role.ADMIN),
    }

    primary_model = Awardee
    select_related = ['user', 'award__app', 'award__image']
    values_white_list = False
    values = ['password', 'is_superuser', 'is_staff']

    def get_model(self):
        if 'user' in self.uri_params:
            if self.request.user.id == int(self.uri_params["user"]):
                return queryset_format(super().get_model())
            else:
                return self.get_response_by_code(1016)
        else:
            return queryset_format(super().get_model())


class IsAppOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return UserGroup.is_owner(request.user, view.find_award().app)


class ImportAwardeesView(GenericViewSet):
    AWARD_DESC_LIMIT = 10
    permission_classes = (IsAuthenticated, IsAppOwner)

    def _insert_awardee_info(self, award, ctx, phone, desc):
        if not desc or len(desc) > self.AWARD_DESC_LIMIT:
            raise ValueError('奖励描述需要不为空并字数不超过{}'.format(self.AWARD_DESC_LIMIT))

        awardee = None
        if ctx:
            try:
                awardee = get_object_or_404(get_user_model(), username=ctx)
            except Http404:
                awardee = may_create_user_and_depts(ctx)
        elif phone:
            awardee = get_user_model().objects.filter(phone=phone).first()
        if not awardee:
            raise ValueError('对应用户无法找到')
        if Awardee.objects.filter(award=award, user=awardee).count() > 0:
            raise ValueError('对应用户已经被加入此次奖励')
        Awardee.objects.create(award=award, user=awardee, desc=desc)

    def find_award(self):
        return get_object_or_404(Award, id=self.kwargs.get('award_id'))

    def create(self, request, *args, **kwargs):
        """
        接受一个上传的excel文件，文件中每一行的格式为三列，依次为万信名，电话，奖励描述。
        如果万信名不存在则通过电话查找用户。
        如果万信名存在于上传文件中但不存在于数据库中，则会尝试根据北斗信息即时创建于数据库。
        使用命令可以类似于：
        curl --form upload=@info.xlsx http://localhost:8000/api/v1/award/1/import-awardees/

        Response:

            {
                "status":200,
                "msg":"成功",
                "data":{
                            "totalCount":3,
                            "success":2,
                            "fail":1,
                            "failed_detail":["第4行 aaa: 对应用户无法找到"]
                    }
            }
        """
        award = self.find_award()
        if 'upload' not in request.FILES:
            raise ValidationError({
                'msg': "'upload' element don't have any file"
            })
        book = xlrd.open_workbook(file_contents=request.FILES['upload'].read())
        sh = book.sheet_by_index(0)
        # input excel line format
        col_num = len(['ctx_name', 'phone', 'desc'])
        ctx_name_index = 0
        phone_index = 1
        desc_index = 2

        total_count = success_count = fail_count = 0
        failed_message_list = []
        for rx in range(sh.nrows):
            row = sh.row(rx)
            phone = row[phone_index].value
            ctx_name = str(row[ctx_name_index].value).strip()
            desc = str(row[desc_index].value).strip()

            # first line may be titles
            if rx == 0 and phone != '' and not isinstance(phone, numbers.Real):
                phone = str(phone).strip()
                if re.search('[^\d|+|\s]', phone):
                    continue

            if len(row) != col_num or (not ctx_name and not phone):
                continue

            total_count += 1
            # for the case that phone number is converted to float number by excel
            if isinstance(phone, numbers.Real):
                phone = int(phone)
            phone = str(phone).strip()
            try:
                self._insert_awardee_info(award, ctx_name, phone, desc)
            except ValueError as e:
                fail_count += 1
                user = ctx_name if ctx_name else phone
                failed_message_list.append("第{0}行 {1}: {2}".format(rx + 1, user, str(e)))
                continue
            success_count += 1

        return Response({'totalCount': total_count, 'success': success_count,
                         'fail': fail_count, 'failed_detail': failed_message_list})
