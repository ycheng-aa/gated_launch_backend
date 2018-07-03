from apps.issue.models import Issue
from django.db.models import Sum
from apps.task_manager.models import GrayTask
from apps.common.serializers import AuthedSerializer


class MyTasksSerializer(AuthedSerializer):

    def to_representation(self, value):
        user = self.current_user()
        task_info = dict()
        task_info['taskId'] = value.id
        task_info['taskName'] = value.task_name
        task_info['startDate'] = value.start_date
        task_info['endDate'] = value.end_date
        task_info['taskCreator'] = value.creator.username
        task_info['taskStatus'] = value.current_status.description
        task_info['app'] = value.app.name
        task_info['imageId'] = value.app.image_id
        task_info['taskDesc'] = value.version_desc
        task_info['appId'] = value.app.id
        task_info['createdTime'] = value.created_time

        issues = Issue.objects.values('task_id').annotate(total_score=Sum('score')).filter(creator=user, task=value)
        if issues:
            task_info['taskTotalScore'] = issues[0]['total_score']
        else:
            task_info['taskTotalScore'] = 0
        return task_info

    class Meta:
        model = GrayTask
