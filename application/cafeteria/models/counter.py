# 作者: toryn
# 时间: 2024/11/25
from django.db import models


class Counter(models.Model):
    # 1. counter:(pk=id) (cafeteria_id)
    cafeteria = models.ForeignKey('cafeteria.Cafeteria', on_delete=models.CASCADE, related_name='所属食堂')

    # 2. (name description floor image)
    # 2.1 柜台图片的默认地址为/<项目>/media/counter, 默认使用/<项目>/media/counter/default.png
    name = models.CharField(max_length=50, unique=True, verbose_name='窗口名称')
    description = models.TextField(max_length=200, blank=True, default='这个窗口很懒，什么都没有留下……', verbose_name='窗口描述')
    floor = models.IntegerField(default=1, verbose_name='楼层')
    image = models.ImageField(upload_to='counter/', default='counter/default.png', verbose_name='窗口图片')
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '窗口'
        verbose_name_plural = verbose_name

