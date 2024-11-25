# 作者: toryn
# 时间: 2024/11/25
"""
用户的收藏模型，作为收藏食堂、窗口、帖子、吃过的食物等的中间表
"""

from django.db import models


class CafeteriaCollection(models.Model):
    collector = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='cafeteria_collector'
    )
    cafeteria = models.ForeignKey(
        'cafeteria.Cafeteria', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='cafeteria_collections'
    )
    created_at = models.DateTimeField(blank=False, null=False, auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户食堂收藏'
        verbose_name_plural = '用户食堂收藏'

    def __str__(self):
        return f'{self.collector.username} 收藏了 {self.collections.name}'


class CounterCollection(models.Model):
    collector = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='counter_collector'
    )
    counter = models.ForeignKey(
        'cafeteria.Counter', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='counter_collections'
    )
    created_at = models.DateTimeField(blank=False, null=False, auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户窗口收藏'
        verbose_name_plural = '用户窗口收藏'

    def __str__(self):
        return f'{self.collector.username} 收藏了 {self.collections.name}'


class PostCollection(models.Model):
    collector = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='post_collector'
    )
    post = models.ForeignKey(
        'post.Post', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='post_collections'
    )
    created_at = models.DateTimeField(blank=False, null=False, auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户帖子收藏'
        verbose_name_plural = '用户帖子收藏'

    def __str__(self):
        return f'{self.collector.username} 收藏了 {self.collections.title}'


class EatCollection(models.Model):
    collector = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='eat_collector'
    )
    post = models.ForeignKey(
        'post.Post', on_delete=models.CASCADE, null=False, db_index=True,
        related_name='eat_collections'
    )
    created_at = models.DateTimeField(blank=False, null=False, auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户吃过收藏'
        verbose_name_plural = '用户吃过收藏'

    def __str__(self):
        return f'{self.collector.username} 吃过了 {self.post.title}'

