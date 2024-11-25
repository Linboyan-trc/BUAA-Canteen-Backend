# 作者: toryn
# 时间: 2024/11/25
from django.db import models


class Dish(models.Model):
    # 1. dish:(pk=id) (counter_id) 
    counter = models.ForeignKey('cafeteria.Counter', on_delete=models.CASCADE, related_name='所属窗口')

    # 2. (name description price image)
    # 2.1 max_digits=5表示最多有5位数字，decimal_places=2表示小数部分最多有2位数字
    # 2.2 菜品图片的默认地址为/<项目>/media/dish, 默认使用/<项目>/media/dish/default.png
    name = models.CharField(max_length=50, verbose_name='菜品名称')
    description = models.TextField(max_length=200, blank=True, default='这个菜很懒，什么都没有留下……', verbose_name='菜品描述')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='菜品价格')
    image = models.ImageField(upload_to='dish/', default='dish/default.png', verbose_name='菜品图片')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '菜品'
        verbose_name_plural = verbose_name

