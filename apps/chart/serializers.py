from apps.app.models import App
from apps.auth.models import User
from apps.issue.models import Issue
from apps.task_manager.models import GrayTask
from apps.common.serializers import AuthedSerializer
from apps.utils.utils import get_task_event_count


class UserChartSerializer(AuthedSerializer):
    def to_representation(self, value):
        result = dict()
        result['scoreSum'] = value['score_sum']
        user = User.objects.get(id=value['creator_id'])
        result['index'] = self.context['index'][value['score_sum']]
        result['userId'] = user.id
        result['userName'] = user.username
        result['chineseName'] = user.full_name
        result['departmentLevel1'] = user.level_one_dep.name if user.level_one_dep else None
        result['departmentLevel2'] = user.level_two_dep.name if user.level_two_dep else None
        result['issuesCount'] = Issue.objects.filter(creator=value['creator_id']).count()
        result['departments'] = [dep.name for dep in user.departments]
        return result

    class Meta:
        model = Issue


class TaskChartSerializer(AuthedSerializer):

    def to_representation(self, value):
        result = dict()
        result['index'] = self.context['index'][value['score_sum']]
        task = GrayTask.objects.get(id=value['task_id'])
        result['taskId'] = value['task_id']
        result['appId'] = task.app_id
        result['taskName'] = task.task_name
        result['taskDesc'] = task.version_desc
        result['userCount'] = Issue.objects.filter(task_id=value['task_id']).values('creator').distinct().count()
        result['appName'] = App.objects.get(id=task.app_id).name
        result['scoreSum'] = value['score_sum']
        result['issuesCount'] = Issue.objects.filter(task_id=value['task_id']).count()
        result['appDownload'] = get_task_event_count(value['task_id'], 'appDownload')
        result['startDate'] = task.start_date
        result['endDate'] = task.end_date
        return result

    class Meta:
        model = Issue


class TaskDetailChartSerializer(AuthedSerializer):
    def to_representation(self, value):
        result = dict()
        user = User.objects.get(id=value['creator_id'])
        result['index'] = self.context['index'][value['score_sum']]
        result['taskId'] = value['task_id']
        result['taskName'] = GrayTask.objects.get(id=value['task_id']).task_name
        result['appName'] = App.objects.get(id=value['app_id']).name
        result['appId'] = value['app_id']
        result['userId'] = user.id
        result['userName'] = user.username
        result['chineseName'] = user.full_name
        result['departmentLevel1'] = user.level_one_dep.name if user.level_one_dep else None
        result['departmentLevel2'] = user.level_two_dep.name if user.level_two_dep else None
        result['departments'] = [dep.name for dep in user.departments]
        result['issuesCount'] = Issue.objects.filter(creator=value['creator_id'], task=value['task_id']).count()
        result['scoreSum'] = value['score_sum']
        return result

    class Meta:
        model = Issue
