from benchmark_django_rest_framework.benchmark_api_view import BenchmarkAPIView
from django.http import HttpResponse
from apps.common.jigsaw_trouserdrop.id_code import ValidationCode
import os


class IdCodeView(BenchmarkAPIView):
    '''
    获取验证码图片
    '''

    access = {'get': 'all', 'post': None, 'put': None, 'delete': None}

    def get_model(self):
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ttf = os.path.join(app_path, "common/jigsaw_trouserdrop/Arial_Black.ttf")
        code = ValidationCode()
        image, chars = code.create_validate_code(font_type=ttf, size=(125, 36), bg_color=(255, 255, 255),
                                                 fg_color=(51, 122, 183), font_size=25, draw_points=True,
                                                 draw_lines=True)
        self.request.session['valiation_code_image'] = chars.lower()
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response
