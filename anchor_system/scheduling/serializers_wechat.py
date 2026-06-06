from rest_framework import serializers
from .models_wechat import WeChatUser


class WeChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChatUser
        fields = '__all__'
        read_only_fields = ['openid', 'unionid', 'last_login', 'created_at']


class WeChatLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=128)


class WeChatPhoneSerializer(serializers.Serializer):
    encrypted_data = serializers.CharField(required=True)
    iv = serializers.CharField(required=True)
