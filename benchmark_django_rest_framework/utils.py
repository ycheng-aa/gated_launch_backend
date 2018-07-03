# 以下两个配置, 如果都不配置, 代表只识别是否 app owner 权限, 而不去识别是否操作 app 对应的 owner.

# put 或 delete 请求修改或删除的数据前, 需要先判断当前的数据, 是否对应的 app owner
# 在下面这个配置中填写 view 和 App id 在 view 的 primary_model 中的字段名, 若没有, 则填 None 或不填 (注意, 这样就不会进行校验了)
APP_FIELD_NAMES_IN_MODEL = {
    'AppModuleView': 'app',
    'AwardView': 'app',
}

# post 或 put 请求, 请求参数中的新增或修改后的数据, 含有 App id 的话, 需要先判断用户是否该 App 对应的 app owner
# 配置每个 view 的请求参数中, App id 的参数名
APP_FIELD_NAMES_IN_REQUEST = {
    'AppModuleView': 'app',
    'AwardView': 'app',
}

# 请求参数中含有 app owner 所要操作的用户群组, 参数值可以是群组 id, 也可以是群组 id 的数组
USER_GROUP_IN_REQUEST = {
    'SmsView': 'groups',
    'EmailView': 'groups',
}


# 使用用户 role 识别用户权限
def right_authenticate(view_instance, role):
    if view_instance.user.role is None:
        return False
    from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
    from apps.auth.models import Role
    from apps.app.models import App
    from apps.user_group.models import UserGroup
    if isinstance(role, str):
        role = [role]
    if Role.APP_OWNER in role and view_instance.user.role.name == Role.APP_OWNER:
        # get 请求的 app owner 的权限验证, 需要对验证后面的查询结果进行过滤, 去掉无权限的结果, 需要每个 view 具体实现.
        # 这里只验证到 role 是否 app owner.
        if view_instance.method in ('put', 'delete'):
            primary_model = getattr(view_instance, 'primary_model', None)
            app_field_name = APP_FIELD_NAMES_IN_MODEL.get(view_instance.__class__.__name__)
            if primary_model is not None and app_field_name is not None:
                if 'pk' in view_instance.uri_params.keys():
                    pk = view_instance.uri_params['pk']
                else:
                    pk = view_instance.data.get('pk')
                if pk is None:
                    return True
                if isinstance(pk, list):    # 批量删除, data 里面的 pk 是个数组
                    pks = pk
                else:
                    pks = [pk]
                error_pks = []
                for pk in pks:
                    m = primary_model.objects.filter(pk=pk).first()
                    app = getattr(m, app_field_name, None)
                    if isinstance(app, int):
                        app = App.objects.filter(pk=app).first()
                    # 如果不存在该 app, 要么是新建, 要么是在后面插入时候返回错误信息
                    if app is not None and not UserGroup.is_owner(view_instance.user, app):
                        error_pks.append((pk, app.pk))
                if len(error_pks) > 0:
                    return BenchmarkAPIView.get_response_by_code(1007, msg_append=str(error_pks))
        if view_instance.method in ('post', 'put'):
            if isinstance(view_instance.data, dict):
                post_data = [view_instance.data]
            else:    # 批量添加, view_instance.data 是个 list , 数组里面是 dict
                post_data = view_instance.data
            app_field_name = APP_FIELD_NAMES_IN_REQUEST.get(view_instance.__class__.__name__)
            if app_field_name is not None:
                error_pks = []
                for data in post_data:
                    app_id = data.get(app_field_name)
                    if app_id is None:
                        continue
                    app = App.objects.filter(pk=app_id).first()
                    # 如果不存在该 app, 要么是新建, 要么是在后面插入时候返回错误信息
                    if app is not None and not UserGroup.is_owner(view_instance.user, app):
                        error_pks.append(app.pk)
                if len(error_pks) > 0:
                    return BenchmarkAPIView.get_response_by_code(1008, msg_append=str(error_pks))
            user_group_field_name = USER_GROUP_IN_REQUEST.get(view_instance.__class__.__name__)
            if user_group_field_name is not None:
                error_pks = []
                for data in post_data:
                    group_id = data.get(user_group_field_name)
                    if isinstance(group_id, list):
                        group_ids = group_id
                    else:
                        group_ids = [group_id]
                    try:
                        groups = UserGroup.objects.filter(pk__in=group_ids).select_related('app')
                    except:
                        return BenchmarkAPIView.get_response_by_code(1012)

                    for group in groups:
                        app = group.app
                        if app is not None and not UserGroup.is_owner(view_instance.user, app):
                            error_pks.append(group.pk)
                if len(error_pks) > 0:
                    return BenchmarkAPIView.get_response_by_code(1013, msg_append=str(error_pks))
        return True
    # 目前只有 admin 权限是灰度平台特殊的权限, 会进这个分支
    return view_instance.user.role.name in role
