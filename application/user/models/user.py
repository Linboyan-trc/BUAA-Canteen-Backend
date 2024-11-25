# 作者: toryn
# 时间: 2024/11/25
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 1. (pk=id username email password)
    # 1.1 verbose_name的作用是在后端管理中，user表中的字段username显示为"用户名"
    # 1.2 unique和error_messages配合使用，在不满足unique条件的时候会有error_messages的报错信息
    username = models.CharField(max_length=20, unique=True, error_messages={'unique': '用户名已存在'}, verbose_name='用户名')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.EmailField(max_length=255, unique=True, error_messages={'unique': '邮箱已存在'}, verbose_name='邮箱')

    # 2. (first_name last_name)
    # 3. (is_superuser is_staff is_active)
    # 4. (last_login date_joined)
    # 5. + (gender) (introduction) (avatar) (isDelete)
    # 5.1 gender.CharField(choices=gender_choices)限制user的gender字段只能是给定的三个选择之一，'null', 'male', 'female'用于在数据库中存储，中文用于在后台管理中显示，此字段默认值为'null'
    # 5.2 avatar字段实际存储的是图片的路径
    # 5.2 upload_to表示图片的路径在/<项目>/media/avatar/下，默认使用/<项目>/media/avatar/default.png
    gender_choices = (
        ('null', '沃尔玛购物袋'),
        ('male', '男'),
        ('female', '女')
    )
    gender = models.CharField(max_length=6, choices=gender_choices, default='null', verbose_name='性别')
    introduction = models.TextField(max_length=200, default='这个人很懒，什么都没有留下', verbose_name='个人简介')
    avatar = models.ImageField(upload_to='avatar/', default='avatar/default.png', verbose_name='头像')
    isDelete = models.BooleanField(default=False)

    # 6.1 对多对:收藏的食堂 - auth_user_cafeteria:(pk=id) (user_id cafeteria_id) (created_at)
    # 6.2 对多对:收藏的柜台 - auth_user_counter:(pk=id) (user_id counter_id) (created_at)
    # 6.3 对多对:吃过的菜品 - auth_user_post_eat:(pk=id) (user_id post_id) (created_at)
    # 6.4 对多对:发布的帖子 - auth_user_post:(pk=id) (user_id post_id) (created_at)
    cafeteria_collections = models.ManyToManyField('cafeteria.Cafeteria', related_name='收藏食堂列表', blank=True,through='CafeteriaCollection')
    counter_collections = models.ManyToManyField('cafeteria.Counter', related_name='收藏窗口列表', blank=True,through='CounterCollection')
    eat_collections = models.ManyToManyField('post.Post', related_name='eaten_by', blank=True, through='EatCollection')
    post_collections = models.ManyToManyField('post.Post', related_name='collected_by', blank=True,through='PostCollection')

    # 7.1 普通用户登录使用:email + password
    USERNAME_FIELD = 'email'

    # 8.1 超级用户创建必填:email + username
    REQUIRED_FIELDS = ['username']

    # 9.1 指定对查询结果的默认按照注册时间降序排序
    # 9.2 指定了此模型在数据库中的表名
    # 9.3 指定了模型名称在后台管理系统中为'用户'，指定多条数据同时显示也为'用户'
    class Meta:
        ordering = ['-date_joined']
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username
