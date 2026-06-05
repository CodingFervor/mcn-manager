from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg

from .models_extra5 import (
    StreamChecklist, StreamReplay, StreamBackup, StreamQuality, LiveTimeline,
    ProductLink, StreamTemplate, StreamOverlay,
    Order, Refund, PriceMonitor, CommissionConfig, ProductTag,
    ProductReview, SalesTarget, PromoCode,
    ContentCalendar, InfluencerCollab, SocialMedia, EmailCampaign,
    ReferralProgram, LoyaltyProgram, EventManagement, SEOOptimization, LivePoll,
)
from .serializers_extra5 import (
    StreamChecklistSerializer, StreamReplaySerializer, StreamBackupSerializer,
    StreamQualitySerializer, LiveTimelineSerializer,
    ProductLinkSerializer, StreamTemplateSerializer, StreamOverlaySerializer,
    OrderSerializer, RefundSerializer, PriceMonitorSerializer,
    CommissionConfigSerializer, ProductTagSerializer,
    ProductReviewSerializer, SalesTargetSerializer, PromoCodeSerializer,
    ContentCalendarSerializer, InfluencerCollabSerializer, SocialMediaSerializer,
    EmailCampaignSerializer, ReferralProgramSerializer, LoyaltyProgramSerializer,
    EventManagementSerializer, SEOOptimizationSerializer, LivePollSerializer,
)


# ============== 直播运营类 ==============

class StreamChecklistViewSet(viewsets.ModelViewSet):
    queryset = StreamChecklist.objects.all()
    serializer_class = StreamChecklistSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'completed': qs.filter(status='done').count(),
            'pending': qs.filter(status='pending').count(),
        })


class StreamReplayViewSet(viewsets.ModelViewSet):
    queryset = StreamReplay.objects.all()
    serializer_class = StreamReplaySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_views': qs.aggregate(s=Sum('views'))['s'] or 0,
            'total_duration': qs.aggregate(s=Sum('duration'))['s'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class StreamBackupViewSet(viewsets.ModelViewSet):
    queryset = StreamBackup.objects.all()
    serializer_class = StreamBackupSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_backup_type': dict(qs.values_list('backup_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'standby': qs.filter(status='standby').count(),
        })


class StreamQualityViewSet(viewsets.ModelViewSet):
    queryset = StreamQuality.objects.all()
    serializer_class = StreamQualitySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
            'avg_fps': qs.aggregate(a=Avg('fps'))['a'] or 0,
            'avg_bitrate': qs.aggregate(a=Avg('bitrate'))['a'] or 0,
        })


class LiveTimelineViewSet(viewsets.ModelViewSet):
    queryset = LiveTimeline.objects.all()
    serializer_class = LiveTimelineSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_event_type': dict(qs.values_list('event_type').annotate(c=Count('id'))),
            'total_gmv': float(qs.aggregate(s=Sum('gmv_at_point'))['s'] or 0),
            'total_viewers': qs.aggregate(s=Sum('viewers_at_point'))['s'] or 0,
        })


class ProductLinkViewSet(viewsets.ModelViewSet):
    queryset = ProductLink.objects.all()
    serializer_class = ProductLinkSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_clicks': qs.aggregate(s=Sum('click_count'))['s'] or 0,
            'total_conversions': qs.aggregate(s=Sum('conversion_count'))['s'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class StreamTemplateViewSet(viewsets.ModelViewSet):
    queryset = StreamTemplate.objects.all()
    serializer_class = StreamTemplateSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_category': dict(qs.values_list('category').annotate(c=Count('id'))),
            'total_usage': qs.aggregate(s=Sum('usage_count'))['s'] or 0,
            'public_count': qs.filter(is_public=True).count(),
        })


class StreamOverlayViewSet(viewsets.ModelViewSet):
    queryset = StreamOverlay.objects.all()
    serializer_class = StreamOverlaySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'by_overlay_type': dict(qs.values_list('overlay_type').annotate(c=Count('id'))),
        })


# ============== 电商销售类 ==============

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_amount': float(qs.aggregate(s=Sum('total_amount'))['s'] or 0),
            'by_source': dict(qs.values_list('source').annotate(c=Count('id'))),
        })


class RefundViewSet(viewsets.ModelViewSet):
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_amount': float(qs.aggregate(s=Sum('amount'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'pending': qs.filter(status='pending').count(),
        })


class PriceMonitorViewSet(viewsets.ModelViewSet):
    queryset = PriceMonitor.objects.all()
    serializer_class = PriceMonitorSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'alerts_triggered': qs.filter(alert_triggered=True).count(),
            'by_platform': dict(qs.values_list('platform').annotate(c=Count('id'))),
            'avg_price_change': qs.aggregate(a=Avg('price_change'))['a'] or 0,
        })


class CommissionConfigViewSet(viewsets.ModelViewSet):
    queryset = CommissionConfig.objects.all()
    serializer_class = CommissionConfigSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'avg_rate': qs.aggregate(a=Avg('rate'))['a'] or 0,
            'avg_anchor_rate': qs.aggregate(a=Avg('anchor_rate'))['a'] or 0,
        })


class ProductTagViewSet(viewsets.ModelViewSet):
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'total_products': qs.aggregate(s=Sum('product_count'))['s'] or 0,
        })


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_sentiment': dict(qs.values_list('sentiment').annotate(c=Count('id'))),
            'avg_rating': qs.aggregate(a=Avg('rating'))['a'] or 0,
            'replied': qs.filter(is_replied=True).count(),
        })


class SalesTargetViewSet(viewsets.ModelViewSet):
    queryset = SalesTarget.objects.all()
    serializer_class = SalesTargetSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_target': float(qs.aggregate(s=Sum('target_amount'))['s'] or 0),
            'total_actual': float(qs.aggregate(s=Sum('actual_amount'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_completion': qs.aggregate(a=Avg('completion_rate'))['a'] or 0,
        })


class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'total_used': qs.aggregate(s=Sum('used_count'))['s'] or 0,
            'total_max_uses': qs.aggregate(s=Sum('max_uses'))['s'] or 0,
        })


# ============== 营销推广类 ==============

class ContentCalendarViewSet(viewsets.ModelViewSet):
    queryset = ContentCalendar.objects.all()
    serializer_class = ContentCalendarSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'by_content_type': dict(qs.values_list('content_type').annotate(c=Count('id'))),
            'by_platform': dict(qs.values_list('platform').annotate(c=Count('id'))),
        })


class InfluencerCollabViewSet(viewsets.ModelViewSet):
    queryset = InfluencerCollab.objects.all()
    serializer_class = InfluencerCollabSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_expected_gmv': float(qs.aggregate(s=Sum('expected_gmv'))['s'] or 0),
            'total_actual_gmv': float(qs.aggregate(s=Sum('actual_gmv'))['s'] or 0),
        })


class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_followers': qs.aggregate(s=Sum('followers'))['s'] or 0,
            'avg_engagement_rate': qs.aggregate(a=Avg('engagement_rate'))['a'] or 0,
            'by_platform': dict(qs.values_list('platform').annotate(c=Count('id'))),
        })


class EmailCampaignViewSet(viewsets.ModelViewSet):
    queryset = EmailCampaign.objects.all()
    serializer_class = EmailCampaignSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_recipients': qs.aggregate(s=Sum('recipients_count'))['s'] or 0,
            'total_opens': qs.aggregate(s=Sum('open_count'))['s'] or 0,
            'total_clicks': qs.aggregate(s=Sum('click_count'))['s'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class ReferralProgramViewSet(viewsets.ModelViewSet):
    queryset = ReferralProgram.objects.all()
    serializer_class = ReferralProgramSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_referrals': qs.aggregate(s=Sum('total_referrals'))['s'] or 0,
            'total_conversions': qs.aggregate(s=Sum('total_conversions'))['s'] or 0,
            'total_budget': float(qs.aggregate(s=Sum('budget'))['s'] or 0),
            'total_spent': float(qs.aggregate(s=Sum('spent'))['s'] or 0),
        })


class LoyaltyProgramViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'total_members': qs.aggregate(s=Sum('total_members'))['s'] or 0,
            'total_active_members': qs.aggregate(s=Sum('active_members'))['s'] or 0,
        })


class EventManagementViewSet(viewsets.ModelViewSet):
    queryset = EventManagement.objects.all()
    serializer_class = EventManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_budget': float(qs.aggregate(s=Sum('budget'))['s'] or 0),
            'total_actual_cost': float(qs.aggregate(s=Sum('actual_cost'))['s'] or 0),
        })


class SEOOptimizationViewSet(viewsets.ModelViewSet):
    queryset = SEOOptimization.objects.all()
    serializer_class = SEOOptimizationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
            'avg_page_speed': qs.aggregate(a=Avg('page_speed'))['a'] or 0,
            'avg_mobile_score': qs.aggregate(a=Avg('mobile_score'))['a'] or 0,
        })


class LivePollViewSet(viewsets.ModelViewSet):
    queryset = LivePoll.objects.all()
    serializer_class = LivePollSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_votes': qs.aggregate(s=Sum('total_votes'))['s'] or 0,
            'active': qs.filter(status='active').count(),
        })
