from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView, SETTINGS
from apps.common.models import Image
from apps.common.serializers import UploadImageSerializer
import imghdr
import json
import requests


class UploadImageView(BenchmarkAPIView):
    '''
    上传图片到图床
    '''
    primary_model = Image
    access = {'get': None, 'post': 'user', 'put': None, 'delete': None}
    serializer_class = UploadImageSerializer

    def post_model(self, data=None):
        if not self.file:
            return self.get_response_by_code(1002)
        if imghdr.what(self.file) is None:
            return self.get_response_by_code(1003)
        try:
            # 实际 filename 参数没有用, 'filename': file.name
            # 如果是中文名, 图床会返回错误的 image id, 所以这里一律把文件名修改一下
            self.file.name = 'pic'
            res = requests.post('http://timg.ffan.com/upload/file', files={'files[]': self.file})
            if res.status_code != 200:
                return self.get_response_by_code(1001, msg_append='http status code 错误, 为 %d' % res.status_code)
            dict_res = json.loads(res.text)
            image_id = dict_res['files'][0]['tfs_key']
        except Exception as e:
            return self.get_response_by_code(1001, msg_append=str(e))
        data = {
            'image_id': image_id,
            'image_name': self.data.get('image_name'),
            'image_desc': self.data.get('image_desc')
        }
        return self.primary_model.post_model(data=data)


class ImageView(BenchmarkAPIView):
    primary_model = Image
    image_url = 'http://timg.ffan.com/convert/resize/tfs/width_0/height_0/url_%s/xx.auto'
    access = {'get': 'user', 'post': None, 'put': None, 'delete': None}

    def get_model(self):
        res = super().get_model()
        if res[SETTINGS.CODE] != SETTINGS.SUCCESS_CODE:
            return res
        for dict_item in res[SETTINGS.DATA]:
            dict_item['image_url'] = self.image_url % dict_item['image_id']
        return res
