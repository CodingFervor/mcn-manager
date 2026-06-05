from rest_framework import serializers
from .models_extra5 import (
    StreamChecklist, StreamReplay, StreamBackup, StreamQuality, LiveTimeline,
    ProductLink, StreamTemplate, StreamOverlay, Order, Refund,
    PriceMonitor, CommissionConfig, ProductTag, ProductReview, SalesTarget,
    PromoCode, ContentCalendar, InfluencerCollab, SocialMedia, EmailCampaign,
    ReferralProgram, LoyaltyProgram, EventManagement, SEOOptimization, LivePoll,
)


# ============== 直播运营类 ==============

class StreamChecklistSerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamChecklist
        fields = '__all__'


class StreamReplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamReplay
        fields = '__all__'


class StreamBackupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamBackup
        fields = '__all__'

class StreamQualitySerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamQuality
        fields = '__all__'

class LiveTimelineSerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveTimeline
        fields = '__all__'

class ProductLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductLink
        fields = '__all__'

class StreamTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamTemplate
        fields = '__all__'

class StreamOverlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = StreamOverlay
        fields = '__all__'


# ============== 电商销售类 ==============

class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display()


class RefundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Refund
        fields = '__all__'

class PriceMonitorSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceMonitor
        fields = '__all__'

class CommissionConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommissionConfig
        fields = '__all__'

class ProductTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductTag
        fields = '__all__'

class ProductReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        fields = '__all__'

class SalesTargetSerializer(serializers.ModelSerializer):
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = SalesTarget
        fields = '__all__'

    def get_completion_rate(self, obj):
        if obj.target_amount and obj.target_amount > 0:
            return round(obj.actual_amount / obj.target_amount * 100, 2)
        return 0


class PromoCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        fields = '__all__'


# ============== 营销推广类 ==============

class ContentCalendarSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentCalendar
        fields = '__all__'

class InfluencerCollabSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfluencerCollab
        fields = '__all__'

class SocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMedia
        fields = '__all__'

class EmailCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailCampaign
        fields = '__all__'

class ReferralProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReferralProgram
        fields = '__all__'

class LoyaltyProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoyaltyProgram
        fields = '__all__'

class EventManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventManagement
        fields = '__all__'

class SEOOptimizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SEOOptimization
        fields = '__all__'

class LivePollSerializer(serializers.ModelSerializer):

    class Meta:
        model = LivePoll
        fields = '__all__'
