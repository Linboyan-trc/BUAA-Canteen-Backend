# 作者: toryn
# 时间: 2024/11/25
from django.urls import path

from .api import *
from .api.cafeteria import get_dishes_no_posts

urlpatterns = [
    ################################################################################
    #################### 1. 获取所有食堂，食堂/所有柜台，柜台/所有菜品的管理员帖子，柜台/所有菜品 ####################
    path('get-all-cafeterias', get_all_cafeterias, name='get_all_cafeterias'),
    path('get-counters', get_counters, name='get_counters'),
    path('counter/get-dishes', get_dishes, name='get_dishes'),
    path('counter/get-dishes-no-posts', get_dishes_no_posts, name='get_dishes_no_posts'),

    ################################################################################
    path('get-cafeteria', get_cafeteria, name='get_cafeteria'),
    path('get-counter', get_counter, name='get_counter'),
]
