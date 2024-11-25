from django.db import models


class Cafeteria(models.Model):
    # 1. cafeteria:(pk=id) (name description address image)
    # 1.1 blank=True表示允许字段为空
    # 1.2 食堂图片的默认地址为/<项目>/media/cafeteria, 默认使用/<项目>/media/cafeteria/default.png
    name = models.CharField(max_length=50, unique=True, verbose_name='食堂名称')
    description = models.TextField(max_length=200, blank=True, default='这个食堂很懒，什么都没有留下……', verbose_name='食堂描述')
    address = models.CharField(max_length=255, blank=True, verbose_name='食堂地址')
    image = models.ImageField(upload_to='cafeteria/', default='cafeteria/default.png', verbose_name='食堂图片')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '食堂'
        verbose_name_plural = verbose_name

