from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q, F
from .models_extra4 import (
    LiveInteraction, Coupon, FlashSale, RoomDecoration, ScriptTag,
    SignContract, BusinessNegotiation, Investment, ContractLedger, Authorization,
    CompetitorRoom, TrafficAnalysis, UserPersona, ABTest, DataWarning,
    Settlement, Logistics, Inventory, ReturnAnalysis, TaxRecord,
)
from .serializers_extra4 import (
    LiveInteractionSerializer, CouponSerializer, FlashSaleSerializer,
    RoomDecorationSerializer, ScriptTagSerializer,
    SignContractSerializer, BusinessNegotiationSerializer, InvestmentSerializer,
    ContractLedgerSerializer, AuthorizationSerializer,
    CompetitorRoomSerializer, TrafficAnalysisSerializer, UserPersonaSerializer,
    ABTestSerializer, DataWarningSerializer,
    SettlementSerializer, LogisticsSerializer, InventorySerializer,
    ReturnAnalysisSerializer, TaxRecordSerializer,
)
from .services import invalidate_cache


# ============== 运营管理类 ==============

class LiveInteractionViewSet(viewsets.ModelViewSet):
    queryset = LiveInteraction.objects.all()
    serializer_class = LiveInteractionSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_type': dict(qs.values_list('interaction_type').annotate(c=Count('id'))),
            'positive': qs.filter(sentiment='positive').count(),
            'negative': qs.filter(sentiment='negative').count(),
        })

    @action(detail=False, methods=['get'])
    def by_session(self, request):
        sid = request.query_params.get('session_id')
        if not sid:
            return Response({'error': 'session_id required'}, status=400)
        qs = qs = self.get_queryset().filter(session_id=sid)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'total_issued': qs.aggregate(s=Sum('total_count'))['s'] or 0,
            'total_used': qs.aggregate(s=Sum('used_count'))['s'] or 0,
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'active'
        obj.save()
        invalidate_cache()
        return Response({'status': 'activated'})


class FlashSaleViewSet(viewsets.ModelViewSet):
    queryset = FlashSale.objects.all()
    serializer_class = FlashSaleSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'ongoing': qs.filter(status='ongoing').count(),
            'total_sold': qs.aggregate(s=Sum('sold_count'))['s'] or 0,
            'total_revenue': sum(
                o.sale_price * o.sold_count for o in qs
            ),
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        qs = self.get_queryset().filter(status='pending').order_by('start_time')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class RoomDecorationViewSet(viewsets.ModelViewSet):
    queryset = RoomDecoration.objects.all()
    serializer_class = RoomDecorationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'by_type': dict(qs.values_list('deco_type').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save()
        invalidate_cache()
        return Response({'is_active': obj.is_active})


class ScriptTagViewSet(viewsets.ModelViewSet):
    queryset = ScriptTag.objects.all()
    serializer_class = ScriptTagSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_type': dict(qs.values_list('tag_type').annotate(c=Count('id'))),
            'total_usage': qs.aggregate(s=Sum('usage_count'))['s'] or 0,
        })

    @action(detail=False, methods=['get'])
    def tree(self, request):
        roots = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


# ============== 商务拓展类 ==============

class SignContractViewSet(viewsets.ModelViewSet):
    queryset = SignContract.objects.all()
    serializer_class = SignContractSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        from datetime import date, timedelta
        qs = self.get_queryset()
        soon = date.today() + timedelta(days=30)
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'expiring_soon': qs.filter(status='active', end_date__lte=soon, end_date__gte=date.today()).count(),
            'by_type': dict(qs.values_list('contract_type').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'active'
        obj.reviewed_by = request.user
        obj.save()
        invalidate_cache()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'terminated'
        obj.reviewed_by = request.user
        obj.save()
        invalidate_cache()
        return Response({'status': 'terminated'})


class BusinessNegotiationViewSet(viewsets.ModelViewSet):
    queryset = BusinessNegotiation.objects.all()
    serializer_class = BusinessNegotiationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_stage': dict(qs.values_list('stage').annotate(c=Count('id'))),
            'avg_probability': qs.aggregate(a=Avg('probability'))['a'] or 0,
            'total_budget': qs.aggregate(s=Sum('budget'))['s'] or 0,
        })

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        stages = ['initial', 'negotiating', 'proposal', 'contract', 'closed', 'lost']
        result = {}
        for s in stages:
            qs = self.get_queryset().filter(stage=s)
            result[s] = {
                'count': qs.count(),
                'total_budget': qs.aggregate(s=Sum('budget'))['s'] or 0,
            }
        return Response(result)


class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_stage': dict(qs.values_list('stage').annotate(c=Count('id'))),
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
        })

    @action(detail=False, methods=['get'])
    def top_prospects(self, request):
        qs = self.get_queryset().exclude(stage__in=['formal', 'paused']).order_by('-score')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ContractLedgerViewSet(viewsets.ModelViewSet):
    queryset = ContractLedger.objects.all()
    serializer_class = ContractLedgerSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_type': dict(qs.values_list('contract_type').annotate(c=Count('id'))),
            'total_amount': qs.aggregate(s=Sum('amount'))['s'] or 0,
        })

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        from datetime import date, timedelta
        days = int(request.query_params.get('days', 30))
        deadline = date.today() + timedelta(days=days)
        qs = self.get_queryset().filter(
            status='active', end_date__lte=deadline, end_date__gte=date.today()
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AuthorizationViewSet(viewsets.ModelViewSet):
    queryset = Authorization.objects.all()
    serializer_class = AuthorizationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'by_type': dict(qs.values_list('auth_type').annotate(c=Count('id'))),
        })

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        from datetime import date, timedelta
        days = int(request.query_params.get('days', 30))
        deadline = date.today() + timedelta(days=days)
        qs = self.get_queryset().filter(
            status='active', end_date__lte=deadline, end_date__gte=date.today()
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ============== 数据与策略类 ==============

class CompetitorRoomViewSet(viewsets.ModelViewSet):
    queryset = CompetitorRoom.objects.all()
    serializer_class = CompetitorRoomSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'avg_viewers': qs.aggregate(a=Avg('avg_viewers'))['a'] or 0,
            'avg_gmv': qs.aggregate(a=Avg('avg_gmv'))['a'] or 0,
            'by_platform': dict(qs.values_list('platform').annotate(c=Count('id'))),
        })

    @action(detail=False, methods=['get'])
    def ranking(self, request):
        qs = self.get_queryset().order_by('-avg_gmv')[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TrafficAnalysisViewSet(viewsets.ModelViewSet):
    queryset = TrafficAnalysis.objects.all()
    serializer_class = TrafficAnalysisSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_impressions': qs.aggregate(s=Sum('impressions'))['s'] or 0,
            'total_clicks': qs.aggregate(s=Sum('clicks'))['s'] or 0,
            'total_cost': qs.aggregate(s=Sum('cost'))['s'] or 0,
            'total_conversions': qs.aggregate(s=Sum('conversions'))['s'] or 0,
        })

    @action(detail=False, methods=['get'])
    def by_source(self, request):
        qs = self.get_queryset()
        result = qs.values('source').annotate(
            impressions=Sum('impressions'),
            clicks=Sum('clicks'),
            cost=Sum('cost'),
            conversions=Sum('conversions'),
        )
        return Response(list(result))


class UserPersonaViewSet(viewsets.ModelViewSet):
    queryset = UserPersona.objects.all()
    serializer_class = UserPersonaSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_fan_level': dict(qs.values_list('fan_level').annotate(c=Count('id'))),
            'avg_spent': qs.aggregate(a=Avg('total_spent'))['a'] or 0,
            'total_spent': qs.aggregate(s=Sum('total_spent'))['s'] or 0,
        })

    @action(detail=False, methods=['get'])
    def vips(self, request):
        qs = self.get_queryset().filter(fan_level='vip').order_by('-total_spent')[:50]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ABTestViewSet(viewsets.ModelViewSet):
    queryset = ABTest.objects.all()
    serializer_class = ABTestSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'running': qs.filter(status='running').count(),
            'completed': qs.filter(status='completed').count(),
            'by_type': dict(qs.values_list('test_type').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'completed'
        obj.save()
        invalidate_cache()
        return Response({'status': 'completed'})


class DataWarningViewSet(viewsets.ModelViewSet):
    queryset = DataWarning.objects.all()
    serializer_class = DataWarningSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'by_severity': dict(qs.values_list('severity').annotate(c=Count('id'))),
            'total_triggers': qs.aggregate(s=Sum('trigger_count'))['s'] or 0,
        })

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save()
        invalidate_cache()
        return Response({'is_active': obj.is_active})


# ============== 财务与供应链类 ==============

class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_gmv': qs.aggregate(s=Sum('total_gmv'))['s'] or 0,
            'total_commission': qs.aggregate(s=Sum('commission'))['s'] or 0,
            'total_final': qs.aggregate(s=Sum('final_amount'))['s'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'approved'
        obj.save()
        invalidate_cache()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'paid'
        obj.save()
        invalidate_cache()
        return Response({'status': 'paid'})


class LogisticsViewSet(viewsets.ModelViewSet):
    queryset = Logistics.objects.all()
    serializer_class = LogisticsSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'by_type': dict(qs.values_list('logistics_type').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        from django.utils import timezone
        obj = self.get_object()
        obj.status = 'shipped'
        obj.shipped_at = timezone.now()
        obj.save()
        invalidate_cache()
        return Response({'status': 'shipped'})

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        from django.utils import timezone
        obj = self.get_object()
        obj.status = 'delivered'
        obj.delivered_at = timezone.now()
        obj.save()
        invalidate_cache()
        return Response({'status': 'delivered'})


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_quantity': qs.aggregate(s=Sum('quantity'))['s'] or 0,
            'total_locked': qs.aggregate(s=Sum('locked_quantity'))['s'] or 0,
            'low_stock_count': sum(
                1 for i in qs.all() if (i.quantity - i.locked_quantity) <= i.safety_stock
            ),
        })

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        items = [i for i in self.get_queryset().all()
                 if (i.quantity - i.locked_quantity) <= i.safety_stock]
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        qty = request.data.get('quantity', 0)
        obj = self.get_object()
        obj.quantity += qty
        from django.utils import timezone
        obj.last_restock = timezone.now()
        obj.save()
        invalidate_cache()
        return Response({'quantity': obj.quantity})


class ReturnAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ReturnAnalysis.objects.all()
    serializer_class = ReturnAnalysisSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_amount': qs.aggregate(s=Sum('amount'))['s'] or 0,
            'by_reason': dict(qs.values_list('reason').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        obj = self.get_object()
        obj.status = 'resolved'
        obj.improvement = request.data.get('improvement', '')
        obj.save()
        invalidate_cache()
        return Response({'status': 'resolved'})


class TaxRecordViewSet(viewsets.ModelViewSet):
    queryset = TaxRecord.objects.all()
    serializer_class = TaxRecordSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_amount': qs.aggregate(s=Sum('amount'))['s'] or 0,
            'total_tax': qs.aggregate(s=Sum('tax_amount'))['s'] or 0,
            'by_type': dict(qs.values_list('tax_type').annotate(c=Count('id'))),
        })

    @action(detail=False, methods=['get'])
    def by_period(self, request):
        period = request.query_params.get('period')
        if not period:
            return Response({'error': 'period required'}, status=400)
        qs = self.get_queryset().filter(period=period)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
