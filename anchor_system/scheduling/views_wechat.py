import logging
import requests as http_requests
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models_wechat import WeChatUser
from .models import Employee
from .serializers import EmployeeSerializer
from .serializers_wechat import WeChatLoginSerializer, WeChatPhoneSerializer

logger = logging.getLogger('api')

WECHAT_CFG = getattr(settings, 'WECHAT_MINI_PROGRAM', {})


class WeChatLoginView(APIView):
    """微信小程序登录: wx.login code -> JWT"""
    permission_classes = [AllowAny]

    def post(self, request):
        ser = WeChatLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data['code']

        appid = WECHAT_CFG.get('APPID', '')
        secret = WECHAT_CFG.get('SECRET', '')

        if not appid or not secret:
            # 开发模式: 用 code 当做 openid 直接登录
            openid = code
        else:
            try:
                resp = http_requests.get(
                    'https://api.weixin.qq.com/sns/jscode2session',
                    params={
                        'appid': appid,
                        'secret': secret,
                        'js_code': code,
                        'grant_type': 'authorization_code',
                    },
                    timeout=5,
                )
                data = resp.json()
                if 'errcode' in data and data['errcode'] != 0:
                    return Response(
                        {'detail': f"微信登录失败: {data.get('errmsg', 'unknown')}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                openid = data['openid']
                session_key = data.get('session_key', '')
                unionid = data.get('unionid', '')
            except Exception as e:
                logger.error('WeChat jscode2session error: %s', e)
                return Response(
                    {'detail': '微信服务异常，请重试'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        is_new = False
        wx_user = WeChatUser.objects.filter(openid=openid).first()

        if wx_user:
            wx_user.session_key = session_key if not appid else wx_user.session_key
            if unionid:
                wx_user.unionid = unionid
            wx_user.save(update_fields=['session_key', 'unionid', 'last_login'])
            user = wx_user.user
        else:
            user = User.objects.create_user(username=f'wx_{openid[:12]}')
            wx_user = WeChatUser.objects.create(
                openid=openid,
                unionid=unionid,
                session_key=session_key if not appid else '',
                user=user,
            )
            is_new = True

        refresh = RefreshToken.for_user(user)
        employee_data = None
        if wx_user.employee:
            employee_data = EmployeeSerializer(wx_user.employee).data

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'employee': employee_data,
            'is_new': is_new,
        })


class WeChatPhoneView(APIView):
    """绑定手机号: 解密微信手机号并关联员工"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = WeChatPhoneSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        wx_user = WeChatUser.objects.filter(user=request.user).first()
        if not wx_user:
            return Response({'detail': '未找到微信用户'}, status=status.HTTP_404_NOT_FOUND)

        # 开发模式: 直接使用传入的 phone 字段
        phone = request.data.get('phone', '')
        if not phone:
            return Response({'detail': '缺少手机号'}, status=status.HTTP_400_BAD_REQUEST)

        wx_user.phone = phone

        employee = Employee.objects.filter(phone=phone).first()
        if employee:
            wx_user.employee = employee
            if employee.user is None:
                employee.user = request.user
                employee.save(update_fields=['user'])

        wx_user.save(update_fields=['phone', 'employee'])

        return Response({
            'phone': phone,
            'linked': wx_user.employee is not None,
            'employee': EmployeeSerializer(wx_user.employee).data if wx_user.employee else None,
        })
