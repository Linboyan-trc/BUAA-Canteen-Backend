import os.path
from pathlib import Path
import pymysql
import yaml
from openai import OpenAI
import django
from django.utils.encoding import force_str

####################################################################################################
# 1. 当前路径是/<项目>/<项目模块>/settings.py
# 1. BASE_DIR为/<项目>
BASE_DIR = Path(__file__).resolve().parent.parent

# 1.1 配置STATIC_ROOT为/<项目>/static
# 1.2 配置MEIDA_ROOT为/<项目>/media
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 2. 读取配置文件
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 2.1 将文件存储在云上
# 2.2 路径为https://buaaxiaolanshu.oss-cn-beijing.aliyuncs.com/media/
DEFAULT_FILE_STORAGE = 'django_oss_storage.backends.OssMediaStorage'
OSS_ACCESS_KEY_ID = config['oss']['oss_access_key_id']
OSS_ACCESS_KEY_SECRET = config['oss']['oss_access_key_secret']
OSS_ENDPOINT = config['oss']['oss_end_point']
OSS_PREFIX_URL = config['oss']['oss_prefix_url']
OSS_BUCKET_NAME = config['oss']['oss_bucket_name']
OSS_BUCKET_ACL_TYPE = config['oss']['oss_bucket_alc_type']  # private, public-read, public-read-write

OSS_MEDIA_URL = OSS_PREFIX_URL + OSS_BUCKET_NAME + '.' + OSS_ENDPOINT + '/' + MEDIA_URL

####################################################################################################
# 解决force_text被弃用而图床上传图片失败的问题
django.utils.encoding.force_text = force_str

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['django_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',

    'corsheaders',
    # 自定义应用
    'application.user',
    'application.cafeteria',
    'application.post',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BUAACanteen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BUAACanteen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': config['database']['engine'],
        'NAME': config['database']['name'],
        'USER': config['database']['user'],
        'PASSWORD': config['database']['password'],
        'HOST': config['database']['host'],
        'PORT': config['database']['port'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user.User'


# simpleui配置
SIMPLEUI_DEFAULT_ICON = False

SIMPLEUI_ICON = {
    '食堂': 'fa-solid fa-bowl-food',
    '窗口': 'fa-solid fa-cookie-bite',
    '菜品': 'fa-solid fa-carrot',
    '帖子': 'fa-solid fa-file',
    '用户': 'fa-solid fa-user',
    '评论': 'fa-solid fa-comment',
}

SIMPLEUI_CONFIG = {
    'system_keep': True,
    'dynamic': False,
    'menu_display': ['用户', '食堂', '窗口', '菜品', '帖子'],
}

SIMPLEUI_INDEX = 'http://localhost:5173/'

SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False

SIMPLEUI_LOGO = ('https://buaaxiaolanshu.oss-cn-beijing.aliyuncs.com/media/avatar/BUAA-Canteen_20241123024650.png')


# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'POST', 'PUT']
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
    'Access-Control-Allow-Origin',
)


# search engine

# whoosh

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}

# elasticsearch

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack',
#     },
# }

