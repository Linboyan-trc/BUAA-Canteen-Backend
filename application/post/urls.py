# 作者: toryn
# 时间: 2024/11/25
from django.urls import path

from .api import *
# Create your views here.

urlpatterns = [
    ################################################################################
    #################### 1. 帖子 ####################
    path('detail', get_detail, name='get_detail'),
    path('upload/info', upload_info, name='upload_info'),
    path('upload/images', upload_image, name='upload_image'),
    path('delete', delete_post, name='delete_post'),
    path('all', get_all_posts, name='get_all_posts'),

    #################### 2. 推荐 ####################
    path('recommend', get_recommend, name='get_recommend'),
    path('search', search, name='search'),

    ################################################################################
    #################### 1. 评论 ####################
    path('main', comment_main, name='comment_main'),
    path('reply', comment_reply, name='comment_reply'),
    path('get-main', get_main_comments, name='get_main_comments'),
    path('get-reply', get_reply_comments, name='get_reply_comments'),
]