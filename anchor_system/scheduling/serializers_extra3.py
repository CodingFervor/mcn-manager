from rest_framework import serializers
from .models_extra3 import (
    ProductSelection, Sample, AdCampaign, ShortVideo, ComplianceReview,
    PublicOpinion, AfterSalesOrder, RevenueSharing, BrandProject, StreamScene,
)


class ProductSelectionSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    suggested_by_name = serializers.CharField(source='suggested_by.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = ProductSelection
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.name', default='', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.name', default='', read_only=True)
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = Sample
        fields = '__all__'


class AdCampaignSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    operator_name = serializers.CharField(source='operator.name', default='', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)
    roi = serializers.SerializerMethodField()

    class Meta:
        model = AdCampaign
        fields = '__all__'

    def get_roi(self, obj):
        if obj.actual_cost and obj.actual_cost > 0:
            return round(float(obj.revenue) / float(obj.actual_cost), 2)
        return 0


class ShortVideoSerializer(serializers.ModelSerializer):
    anchor_name = serializers.CharField(source='anchor.name', default='', read_only=True)
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    creator_name = serializers.CharField(source='creator.name', default='', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)
    engagement_rate = serializers.SerializerMethodField()

    class Meta:
        model = ShortVideo
        fields = '__all__'

    def get_engagement_rate(self, obj):
        if obj.views and obj.views > 0:
            return round((obj.likes + obj.comments + obj.shares) / obj.views * 100, 2)
        return 0


class ComplianceReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.name', default='', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.name', default='', read_only=True)
    review_type_display = serializers.CharField(source='get_review_type_display', default='', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', default='', read_only=True)

    class Meta:
        model = ComplianceReview
        fields = '__all__'


class PublicOpinionSerializer(serializers.ModelSerializer):
    related_store_name = serializers.CharField(source='related_store.name', default='', read_only=True)
    related_anchor_name = serializers.CharField(source='related_anchor.name', default='', read_only=True)
    source_display = serializers.CharField(source='get_source_display', default='', read_only=True)
    sentiment_display = serializers.CharField(source='get_sentiment_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = PublicOpinion
        fields = '__all__'


class AfterSalesOrderSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    handler_name = serializers.CharField(source='handler.name', default='', read_only=True)
    type_display = serializers.CharField(source='get_type_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = AfterSalesOrder
        fields = '__all__'


class RevenueSharingSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    anchor_name = serializers.CharField(source='anchor.name', default='', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = RevenueSharing
        fields = '__all__'


class BrandProjectSerializer(serializers.ModelSerializer):
    pm_name = serializers.CharField(source='pm.name', default='', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)
    anchor_names = serializers.SerializerMethodField()
    store_names = serializers.SerializerMethodField()

    class Meta:
        model = BrandProject
        fields = '__all__'

    def get_anchor_names(self, obj):
        return ', '.join(a.name for a in obj.anchors.all()[:5])

    def get_store_names(self, obj):
        return ', '.join(s.name for s in obj.stores.all()[:5])


class StreamSceneSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', default='', read_only=True)
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    scene_type_display = serializers.CharField(source='get_scene_type_display', default='', read_only=True)

    class Meta:
        model = StreamScene
        fields = '__all__'
