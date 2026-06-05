from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from .models_extra3 import (
    ProductSelection, Sample, AdCampaign, ShortVideo, ComplianceReview,
    PublicOpinion, AfterSalesOrder, RevenueSharing, BrandProject, StreamScene,
)
from .serializers_extra3 import (
    ProductSelectionSerializer, SampleSerializer, AdCampaignSerializer,
    ShortVideoSerializer, ComplianceReviewSerializer, PublicOpinionSerializer,
    AfterSalesOrderSerializer, RevenueSharingSerializer, BrandProjectSerializer,
    StreamSceneSerializer,
)
from .services import invalidate_cache


# ============== 1. 选品管理 ==============

class ProductSelectionViewSet(viewsets.ModelViewSet):
    queryset = ProductSelection.objects.select_related('product', 'store', 'supplier', 'suggested_by')
    serializer_class = ProductSelectionSerializer
    filterset_fields = ['status', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('selections')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('selections')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'shortlisted': qs.filter(status='shortlisted').count(),
            'confirmed': qs.filter(status='confirmed').count(),
            'avg_score': round(qs.aggregate(s=Avg('total_score'))['s'] or 0, 1),
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
        })

    @action(detail=False)
    def top_scored(self, request):
        qs = self.get_queryset().filter(status__in=['pending', 'shortlisted']).order_by('-total_score')[:10]
        return Response(ProductSelectionSerializer(qs, many=True).data)


# ============== 2. 样品管理 ==============

class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.select_related('product', 'supplier', 'requested_by', 'assigned_to', 'store')
    serializer_class = SampleSerializer
    filterset_fields = ['status', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('samples')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('samples')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'in_transit': qs.filter(status__in=['requested', 'shipped']).count(),
            'testing': qs.filter(status='testing').count(),
            'overdue': qs.filter(return_deadline__lt=timezone.now(), status__in=['received', 'testing', 'in_stream']).count(),
        })

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        s = self.get_object()
        s.status = 'received'
        s.received_date = timezone.now().date()
        s.save()
        invalidate_cache('samples')
        return Response({'status': 'received'})

    @action(detail=True, methods=['post'])
    def return_sample(self, request, pk=None):
        s = self.get_object()
        s.status = 'returned'
        s.save()
        invalidate_cache('samples')
        return Response({'status': 'returned'})


# ============== 3. 流量投放 ==============

class AdCampaignViewSet(viewsets.ModelViewSet):
    queryset = AdCampaign.objects.select_related('store', 'session', 'operator')
    serializer_class = AdCampaignSerializer
    filterset_fields = ['status', 'platform', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('ad-campaigns')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('ad-campaigns')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'running': qs.filter(status='running').count(),
            'total_budget': qs.aggregate(s=Sum('budget'))['s'] or 0,
            'total_cost': qs.aggregate(s=Sum('actual_cost'))['s'] or 0,
            'total_revenue': qs.aggregate(s=Sum('revenue'))['s'] or 0,
            'overall_roi': self._calc_roi(qs),
        })

    @action(detail=False)
    def by_platform(self, request):
        data = AdCampaign.objects.values('platform').annotate(
            count=Count('id'), budget=Sum('budget'), cost=Sum('actual_cost'), revenue=Sum('revenue')
        )
        return Response(list(data))

    def _calc_roi(self, qs):
        total_cost = qs.aggregate(s=Sum('actual_cost'))['s'] or 0
        total_revenue = qs.aggregate(s=Sum('revenue'))['s'] or 0
        return round(total_revenue / total_cost, 2) if total_cost > 0 else 0


# ============== 4. 短视频管理 ==============

class ShortVideoViewSet(viewsets.ModelViewSet):
    queryset = ShortVideo.objects.select_related('store', 'anchor', 'creator', 'product')
    serializer_class = ShortVideoSerializer
    filterset_fields = ['status', 'platform', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('short-videos')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('short-videos')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'published': qs.filter(status='published').count(),
            'total_views': qs.aggregate(s=Sum('views'))['s'] or 0,
            'total_likes': qs.aggregate(s=Sum('likes'))['s'] or 0,
            'avg_engagement': round(qs.aggregate(a=Avg('views'))['a'] or 0, 0),
        })

    @action(detail=False)
    def top_performing(self, request):
        qs = self.get_queryset().filter(status='published').order_by('-views')[:10]
        return Response(ShortVideoSerializer(qs, many=True).data)


# ============== 5. 内容合规审核 ==============

class ComplianceReviewViewSet(viewsets.ModelViewSet):
    queryset = ComplianceReview.objects.select_related('reviewer', 'submitted_by', 'related_session', 'store')
    serializer_class = ComplianceReviewSerializer
    filterset_fields = ['status', 'review_type', 'risk_level']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('compliance')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('compliance')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'high_risk': qs.filter(risk_level__in=['high', 'forbidden']).count(),
            'pass_rate': self._pass_rate(qs),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        r = self.get_object()
        r.status = 'approved'
        r.reviewer_id = request.data.get('reviewer')
        r.reviewed_at = timezone.now()
        r.review_notes = request.data.get('notes', '')
        r.save()
        invalidate_cache('compliance')
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        r = self.get_object()
        r.status = 'rejected'
        r.reviewer_id = request.data.get('reviewer')
        r.reviewed_at = timezone.now()
        r.violations = request.data.get('violations', '')
        r.suggestions = request.data.get('suggestions', '')
        r.save()
        invalidate_cache('compliance')
        return Response({'status': 'rejected'})

    def _pass_rate(self, qs):
        total = qs.filter(status__in=['approved', 'rejected']).count()
        if total == 0:
            return 0
        return round(qs.filter(status='approved').count() / total * 100, 1)


# ============== 6. 舆情监控 ==============

class PublicOpinionViewSet(viewsets.ModelViewSet):
    queryset = PublicOpinion.objects.select_related('related_store', 'related_anchor', 'handler')
    serializer_class = PublicOpinionSerializer
    filterset_fields = ['status', 'sentiment', 'source']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('opinions')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('opinions')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'negative': qs.filter(sentiment='negative').count(),
            'escalated': qs.filter(status='escalated').count(),
            'avg_heat': round(qs.aggregate(a=Avg('heat'))['a'] or 0, 1),
            'by_sentiment': list(qs.values('sentiment').annotate(count=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        o = self.get_object()
        o.status = 'resolved'
        o.handler_id = request.data.get('handler')
        o.resolution = request.data.get('resolution', '')
        o.resolved_at = timezone.now()
        o.save()
        invalidate_cache('opinions')
        return Response({'status': 'resolved'})


# ============== 7. 售后工单 ==============

class AfterSalesOrderViewSet(viewsets.ModelViewSet):
    queryset = AfterSalesOrder.objects.select_related('store', 'handler', 'related_session')
    serializer_class = AfterSalesOrderSerializer
    filterset_fields = ['status', 'type', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('after-sales')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('after-sales')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status__in=['submitted', 'reviewing']).count(),
            'total_amount': qs.aggregate(s=Sum('amount'))['s'] or 0,
            'by_type': list(qs.values('type').annotate(count=Count('id'), total=Sum('amount'))),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        o = self.get_object()
        o.status = 'approved'
        o.handler_id = request.data.get('handler')
        o.resolution = request.data.get('resolution', '')
        o.save()
        invalidate_cache('after-sales')
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        o = self.get_object()
        o.status = 'completed'
        o.completed_at = timezone.now()
        o.resolution = request.data.get('resolution', o.resolution)
        o.save()
        invalidate_cache('after-sales')
        return Response({'status': 'completed'})


# ============== 8. MCN 分成 ==============

class RevenueSharingViewSet(viewsets.ModelViewSet):
    queryset = RevenueSharing.objects.select_related('store', 'anchor')
    serializer_class = RevenueSharingSerializer
    filterset_fields = ['status', 'period_type', 'store', 'anchor']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('revenue-sharing')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('revenue-sharing')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total_records': qs.count(),
            'total_revenue': qs.aggregate(s=Sum('total_revenue'))['s'] or 0,
            'total_mcn_share': qs.aggregate(s=Sum('mcn_share'))['s'] or 0,
            'total_anchor_share': qs.aggregate(s=Sum('anchor_share'))['s'] or 0,
            'pending': qs.filter(status='pending').count(),
        })

    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        r = self.get_object()
        r.status = 'settled'
        r.settled_at = timezone.now()
        r.save()
        invalidate_cache('revenue-sharing')
        return Response({'status': 'settled'})


# ============== 9. 品牌合作项目 ==============

class BrandProjectViewSet(viewsets.ModelViewSet):
    queryset = BrandProject.objects.prefetch_related('stores', 'anchors').select_related('pm')
    serializer_class = BrandProjectSerializer
    filterset_fields = ['status', 'priority']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('brand-projects')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('brand-projects')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'executing': qs.filter(status='executing').count(),
            'total_budget': qs.aggregate(s=Sum('total_budget'))['s'] or 0,
            'total_revenue': qs.aggregate(s=Sum('actual_revenue'))['s'] or 0,
            'by_status': list(qs.values('status').annotate(count=Count('id'))),
        })

    @action(detail=False)
    def active(self, request):
        qs = self.get_queryset().filter(status__in=['contracted', 'executing', 'delivering'])
        return Response(BrandProjectSerializer(qs, many=True).data)


# ============== 10. 直播间场景 ==============

class StreamSceneViewSet(viewsets.ModelViewSet):
    queryset = StreamScene.objects.select_related('room', 'store')
    serializer_class = StreamSceneSerializer
    filterset_fields = ['scene_type', 'status', 'room']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('scenes')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('scenes')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'total_usage': qs.aggregate(s=Sum('usage_count'))['s'] or 0,
            'total_cost': qs.aggregate(s=Sum('cost'))['s'] or 0,
            'by_type': list(qs.values('scene_type').annotate(count=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        s = self.get_object()
        s.status = 'active'
        s.usage_count += 1
        s.last_used_at = timezone.now()
        s.save()
        invalidate_cache('scenes')
        return Response({'status': 'activated', 'usage_count': s.usage_count})
