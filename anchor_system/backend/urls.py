from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from scheduling.views_wechat import WeChatLoginView, WeChatPhoneView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/wechat-login/', WeChatLoginView.as_view(), name='wechat-login'),
    path('api/auth/wechat-phone/', WeChatPhoneView.as_view(), name='wechat-phone'),
    path('api/', include('scheduling.urls')),
]
