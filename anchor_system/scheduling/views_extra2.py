from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from .models_extra2 import (
    StreamAlert, Asset, KnowledgeDocument, ExpenseClaim, CustomerComplaint,
    StreamPlan, GiftRecord, FanGroup, DataReport, Supplier,
)
from .serializers_extra2 import (
    StreamAlertSerializer, AssetSerializer, KnowledgeDocumentSerializer,
    ExpenseClaimSerializer, CustomerComplaintSerializer, StreamPlanSerializer,
    GiftRecordSerializer, FanGroupSerializer, DataReportSerializer, SupplierSerializer,
)
from .services import invalidate_cache


# ============== 1. 直播监控告警 ==============

class StreamAlertViewSet(viewsets.ModelViewSet):
    queryset = StreamAlert.objects.select_related('store', 'room', 'session', 'resolved_by')
    serializer_class = StreamAlertSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('stream-alerts')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('stream-alerts')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        pending = qs.filter(status='pending').count()
        today = qs.filter(created_at__date=timezone.now().date())
        return Response({
            'total': qs.count(),
            'pending': pending,
            'critical': qs.filter(severity='critical').count(),
            'today': today.count(),
            'today_resolved': today.filter(status='resolved').count(),
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_by_id = request.data.get('resolved_by')
        alert.resolved_at = timezone.now()
        alert.save()
        invalidate_cache('stream-alerts')
        return Response({'status': 'resolved'})


# ============== 2. 设备资产 ==============

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('assigned_to', 'room')
    serializer_class = AssetSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('assets')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('assets')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'available': qs.filter(status='available').count(),
            'in_use': qs.filter(status='in_use').count(),
            'maintenance': qs.filter(status='maintenance').count(),
            'total_value': qs.aggregate(v=Sum('purchase_price'))['v'] or 0,
        })

    @action(detail=False)
    def by_category(self, request):
        data = Asset.objects.values('category').annotate(
            count=Count('id'), value=Sum('purchase_price')
        ).order_by('-count')
        return Response(list(data))


# ============== 3. 知识库 ==============

class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeDocument.objects.select_related('author')
    serializer_class = KnowledgeDocumentSerializer
    filterset_fields = ['category', 'status']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('knowledge')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('knowledge')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        doc = self.get_object()
        doc.status = 'published'
        doc.save()
        invalidate_cache('knowledge')
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        doc = self.get_object()
        doc.view_count += 1
        doc.save(update_fields=['view_count'])
        return Response({'view_count': doc.view_count})

    @action(detail=False)
    def popular(self, request):
        qs = self.get_queryset().filter(status='published').order_by('-view_count')[:10]
        return Response(KnowledgeDocumentSerializer(qs, many=True).data)


# ============== 4. 费用报销 ==============

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.select_related('employee', 'approved_by')
    serializer_class = ExpenseClaimSerializer
    filterset_fields = ['status', 'category', 'employee']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('expenses')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('expenses')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'approved': qs.filter(status='approved').count(),
            'total_amount': qs.aggregate(s=Sum('amount'))['s'] or 0,
            'pending_amount': qs.filter(status='pending').aggregate(s=Sum('amount'))['s'] or 0,
            'by_category': list(qs.values('category').annotate(
                count=Count('id'), total=Sum('amount')
            )),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        claim = self.get_object()
        claim.status = 'approved'
        claim.approved_by_id = request.data.get('approved_by')
        claim.approved_at = timezone.now()
        claim.save()
        invalidate_cache('expenses')
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        claim = self.get_object()
        claim.status = 'rejected'
        claim.reject_reason = request.data.get('reason', '')
        claim.approved_by_id = request.data.get('approved_by')
        claim.approved_at = timezone.now()
        claim.save()
        invalidate_cache('expenses')
        return Response({'status': 'rejected'})


# ============== 5. 客户投诉 ==============

class CustomerComplaintViewSet(viewsets.ModelViewSet):
    queryset = CustomerComplaint.objects.select_related('store', 'handler')
    serializer_class = CustomerComplaintSerializer
    filterset_fields = ['status', 'priority', 'complaint_type', 'store']

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('complaints')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('complaints')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'urgent': qs.filter(priority='urgent').count(),
            'avg_resolve_hours': 0,
            'by_type': list(qs.values('complaint_type').annotate(count=Count('id'))),
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        complaint.status = 'resolved'
        complaint.handler_id = request.data.get('handler')
        complaint.resolution = request.data.get('resolution', '')
        complaint.resolved_at = timezone.now()
        complaint.save()
        invalidate_cache('complaints')
        return Response({'status': 'resolved'})


# ============== 6. 直播预告 ==============

class StreamPlanViewSet(viewsets.ModelViewSet):
    queryset = StreamPlan.objects.select_related('store', 'room', 'anchor', 'co_anchor')
    serializer_class = StreamPlanSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('stream-plans')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('stream-plans')

    @action(detail=False)
    def upcoming(self, request):
        qs = self.get_queryset().filter(
            planned_start__gte=timezone.now(), status__in=['planned', 'confirmed']
        ).order_by('planned_start')[:10]
        return Response(StreamPlanSerializer(qs, many=True).data)

    @action(detail=False)
    def calendar(self, request):
        from datetime import datetime
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        qs = self.get_queryset()
        if start:
            qs = qs.filter(planned_start__gte=start)
        if end:
            qs = qs.filter(planned_end__lte=end)
        return Response(StreamPlanSerializer(qs, many=True).data)


# ============== 7. 打赏/礼物统计 ==============

class GiftRecordViewSet(viewsets.ModelViewSet):
    queryset = GiftRecord.objects.select_related('session')
    serializer_class = GiftRecordSerializer

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total_count': qs.count(),
            'total_value': qs.aggregate(v=Sum('total_value'))['v'] or 0,
            'by_type': list(qs.values('gift_type').annotate(
                count=Count('id'), value=Sum('total_value')
            )),
            'top_gifts': list(qs.values('gift_name').annotate(
                count=Sum('quantity'), value=Sum('total_value')
            ).order_by('-value')[:10]),
        })

    @action(detail=False)
    def by_session(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=400)
        qs = self.get_queryset().filter(session_id=session_id)
        return Response({
            'total_value': qs.aggregate(v=Sum('total_value'))['v'] or 0,
            'total_count': qs.count(),
            'gifts': GiftRecordSerializer(qs, many=True).data,
        })


# ============== 8. 粉丝群 ==============

class FanGroupViewSet(viewsets.ModelViewSet):
    queryset = FanGroup.objects.select_related('store', 'admin')
    serializer_class = FanGroupSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('fan-groups')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('fan-groups')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'total_members': qs.aggregate(m=Sum('member_count'))['m'] or 0,
            'by_platform': list(qs.values('platform').annotate(
                count=Count('id'), members=Sum('member_count')
            )),
        })


# ============== 9. 数据报表 ==============

class DataReportViewSet(viewsets.ModelViewSet):
    queryset = DataReport.objects.select_related('created_by')
    serializer_class = DataReportSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('reports')

    @action(detail=False)
    def recent(self, request):
        qs = self.get_queryset().order_by('-created_at')[:5]
        return Response(DataReportSerializer(qs, many=True).data)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        import csv, io, os
        report = self.get_object()
        report.status = 'generating'
        report.save()

        try:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['报表名称', report.title])
            writer.writerow(['类型', report.get_report_type_display()])
            writer.writerow(['日期范围', f'{report.date_start} ~ {report.date_end}'])
            writer.writerow([])
            writer.writerow(['生成时间', str(timezone.now())])
            writer.writerow(['状态', '已生成'])

            filename = f'report_{report.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}.csv'
            report.file_url = f'/media/reports/{filename}'
            report.status = 'completed'
            report.save()
            invalidate_cache('reports')
            return Response({'status': 'completed', 'file_url': report.file_url})
        except Exception as e:
            report.status = 'failed'
            report.save()
            return Response({'status': 'failed', 'error': str(e)}, status=500)


# ============== 10. 供应商管理 ==============

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def perform_create(self, serializer):
        serializer.save()
        invalidate_cache('suppliers')

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache('suppliers')

    @action(detail=False)
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'avg_rating': round(qs.aggregate(r=Avg('rating'))['r'] or 0, 1),
            'by_category': list(qs.values('category').annotate(count=Count('id'))),
        })
