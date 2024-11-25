# 作者: toryn
# 时间: 2024/11/25
from django.db import models
from django.contrib.auth import get_user_model


class Auth(models.Model):
    # 1. auth:(pk=id) (user_id)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='auth_info')

    # 2. (login_at expires_at)
    login_at = models.DateTimeField(auto_now=True, verbose_name='登录时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.user.username + '的认证信息'
