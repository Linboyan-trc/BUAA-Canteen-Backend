# 作者: toryn
# 时间: 2024/11/25
import json
import uuid
import oss2
from django.http import HttpRequest
from django.conf import settings


####################################################################################################
# 1. 将请求解析为字典
# 1.1 GET请求将Query String解析为字典
# 1.2 POST请求将request body解析为字典
def parse_request_data(request: HttpRequest) -> dict:
    if request.method == 'GET':
        return request.GET.dict()
    elif request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    else:
        return {}


####################################################################################################
# 1. 文件分类:avatar, cafeteria, dish, post, default
UPLOAD_FOLDER_MAPPING = {
    'avatar': 'avatar/',
    'cafeteria': 'cafeteria/',
    'counter': 'counter/',
    'dish': 'dish/',
    'post': 'post/',
    'default': 'default/',
}


# 2. 上传图片，返回图片的图床:img_url
def upload_img_file(image, folder='default'):
    # 1. 生成一个uuid
    number = uuid.uuid4()

    # 2. 拼接成 'media/<folder>/<number>.jpg'
    img_path = 'media/' + UPLOAD_FOLDER_MAPPING[folder] + str(number) + '.jpg'

    # 3. 得到图床的url: 'https://buaaxiaolanshu.oss-cn-beijing.aliyuncs.com/media/<folder>/<number>.jpg'
    img_url = settings.OSS_MEDIA_URL + UPLOAD_FOLDER_MAPPING[folder] + str(number) + '.jpg'

    # 4. 使用KEY_ID, KEY_SECRET验证身份
    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)

    # 5. 获取桶: 'https://buaaxiaolanshu.oss-cn-beijing.aliyuncs.com/'
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)

    # 6. 上传图片
    try:
        bucket.put_object(img_path, image.read())

        # 7. 返回图床的img_url
        return img_url
    except oss2.exceptions.OssError as e:
        print(f"上传图片失败: {e}")
        return ''

