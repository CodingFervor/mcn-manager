from django.db import models
from django.contrib.auth.models import User


class WeChatUser(models.Model):
    """微信小程序用户"""
    openid = models.CharField('OpenID', max_length=64, unique=True, db_index=True)
    unionid = models.CharField('UnionID', max_length=64, blank=True, db_index=True)
    session_key = models.CharField('会话密钥', max_length=128, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='系统用户')
    employee = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联员工')
    nickname = models.CharField('昵称', max_length=100, blank=True)
    avatar_url = models.URLField('头像', blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    last_login = models.DateTimeField('最后登录', auto_now=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '微信用户'
        verbose_name_plural = verbose_name
        ordering = ['-last_login']

    def __str__(self):
        return f'{self.nickname or self.openid[:12]}'
