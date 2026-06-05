from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta, date
import csv
import io
import json

from .models_extra import (
    ProductCategory, Product, InventoryAlert,
    StreamScript, ScriptSegment, SalesScript, StreamReview,
    TaskBoard, TaskCard, Notification,
    FinanceRecord, CommissionRule, CommissionRecord,
    Contract, TrainingCourse, TrainingRecord,
    Competitor, CompetitorData, FanAnalysis,
    Campaign, Goal, OperationLog, BillboardConfig,
    Role, UserRole, KOLContact, ExportTask,
)
from .serializers_extra import (
    ProductCategorySerializer, ProductSerializer, InventoryAlertSerializer,
    StreamScriptSerializer, ScriptSegmentSerializer, SalesScriptSerializer, StreamReviewSerializer,
    TaskBoardSerializer, TaskCardSerializer, NotificationSerializer,
    FinanceRecordSerializer, CommissionRuleSerializer, CommissionRecordSerializer,
    ContractSerializer, TrainingCourseSerializer, TrainingRecordSerializer,
    CompetitorSerializer, CompetitorDataSerializer, FanAnalysisSerializer,
    CampaignSerializer, GoalSerializer, OperationLogSerializer, BillboardConfigSerializer,
    RoleSerializer, UserRoleSerializer, KOLContactSerializer, ExportTaskSerializer,
)


# ============== 1-2. 商品 + 库存 ==============

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('category_id'): qs = qs.filter(category_id=p['category_id'])
        if p.get('kw'): qs = qs.filter(Q(name__icontains=p['kw']) | Q(sku__icontains=p['kw']))
        return qs

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        products = Product.objects.filter(stock__lte=10, status='active')
        return Response(ProductSerializer(products, many=True).data)


class InventoryAlertViewSet(viewsets.ModelViewSet):
    queryset = InventoryAlert.objects.select_related('product').all()
    serializer_class = InventoryAlertSerializer

    @action(detail=False, methods=['get'])
    def triggered(self, request):
        alerts = InventoryAlert.objects.filter(is_active=True)
        triggered = []
        for a in alerts:
            if a.product.stock <= a.threshold:
                triggered.append({
                    'id': a.id, 'product_id': a.product.id,
                    'product_name': a.product.name,
                    'stock': a.product.stock, 'threshold': a.threshold,
                })
        return Response(triggered)


# ============== 3-4. 脚本 + 话术 ==============

class StreamScriptViewSet(viewsets.ModelViewSet):
    queryset = StreamScript.objects.select_related('store', 'creator').prefetch_related('segments').all()
    serializer_class = StreamScriptSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        return qs


class ScriptSegmentViewSet(viewsets.ModelViewSet):
    queryset = ScriptSegment.objects.select_related('product').all()
    serializer_class = ScriptSegmentSerializer


class SalesScriptViewSet(viewsets.ModelViewSet):
    queryset = SalesScript.objects.select_related('creator').all()
    serializer_class = SalesScriptSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('scene'): qs = qs.filter(scene=p['scene'])
        if p.get('kw'): qs = qs.filter(Q(title__icontains=p['kw']) | Q(content__icontains=p['kw']))
        return qs


# ============== 5. 直播复盘 ==============

class StreamReviewViewSet(viewsets.ModelViewSet):
    queryset = StreamReview.objects.select_related('session', 'reviewer').all()
    serializer_class = StreamReviewSerializer


# ============== 6. 任务看板 ==============

class TaskBoardViewSet(viewsets.ModelViewSet):
    queryset = TaskBoard.objects.prefetch_related('cards__assignee').all()
    serializer_class = TaskBoardSerializer


class TaskCardViewSet(viewsets.ModelViewSet):
    queryset = TaskCard.objects.select_related('assignee', 'board').all()
    serializer_class = TaskCardSerializer

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        card = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(TaskCard.STATUS).keys():
            card.status = new_status
            card.save()
            return Response(TaskCardSerializer(card).data)
        return Response({'detail': '无效状态'}, status=400)


# ============== 7. 消息中心 ==============

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('target').all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('target_id'): qs = qs.filter(target_id=p['target_id'])
        if p.get('is_read') is not None: qs = qs.filter(is_read=p['is_read'] == 'true')
        if p.get('type'): qs = qs.filter(type=p['type'])
        return qs

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        target_id = request.data.get('target_id')
        qs = Notification.objects.all()
        if target_id:
            qs = qs.filter(target_id=target_id)
        qs.filter(is_read=False).update(is_read=True)
        return Response({'updated': qs.count()})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        target_id = request.query_params.get('target_id')
        qs = Notification.objects.filter(is_read=False)
        if target_id:
            qs = qs.filter(target_id=target_id)
        return Response({'count': qs.count()})


# ============== 8-9. 财务 + 佣金 ==============

class FinanceRecordViewSet(viewsets.ModelViewSet):
    queryset = FinanceRecord.objects.select_related('store', 'employee').all()
    serializer_class = FinanceRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('start'): qs = qs.filter(date__gte=p['start'])
        if p.get('end'): qs = qs.filter(date__lte=p['end'])
        if p.get('type'): qs = qs.filter(type=p['type'])
        if p.get('category'): qs = qs.filter(category=p['category'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        return qs

    @action(detail=False, methods=['get'])
    def summary(self, request):
        p = request.query_params
        qs = FinanceRecord.objects.all()
        if p.get('start'): qs = qs.filter(date__gte=p['start'])
        if p.get('end'): qs = qs.filter(date__lte=p['end'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        income = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        by_category = list(qs.values('type', 'category').annotate(total=Sum('amount')).order_by('-total'))
        return Response({
            'income': float(income), 'expense': float(expense),
            'profit': float(income - expense),
            'by_category': by_category,
        })


class CommissionRuleViewSet(viewsets.ModelViewSet):
    queryset = CommissionRule.objects.all()
    serializer_class = CommissionRuleSerializer


class CommissionRecordViewSet(viewsets.ModelViewSet):
    queryset = CommissionRecord.objects.select_related('employee', 'rule').all()
    serializer_class = CommissionRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('period'): qs = qs.filter(period=p['period'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        return qs

    @action(detail=True, methods=['post'])
    def settle(self, request, pk=None):
        rec = self.get_object()
        rec.status = 'settled'
        rec.settled_at = timezone.now()
        rec.save()
        return Response(CommissionRecordSerializer(rec).data)


# ============== 10. 合同 ==============

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related('employee').all()
    serializer_class = ContractSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('contract_type'): qs = qs.filter(contract_type=p['contract_type'])
        return qs

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        days = int(request.query_params.get('days', 30))
        today = date.today()
        cutoff = today + timedelta(days=days)
        contracts = Contract.objects.filter(
            status='active', end_date__gte=today, end_date__lte=cutoff
        )
        return Response(ContractSerializer(contracts, many=True).data)


# ============== 11. 培训 ==============

class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.select_related('trainer').prefetch_related('records').all()
    serializer_class = TrainingCourseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('category'): qs = qs.filter(category=p['category'])
        return qs


class TrainingRecordViewSet(viewsets.ModelViewSet):
    queryset = TrainingRecord.objects.select_related('course', 'employee').all()
    serializer_class = TrainingRecordSerializer


# ============== 12. 竞品 ==============

class CompetitorViewSet(viewsets.ModelViewSet):
    queryset = Competitor.objects.prefetch_related('data').all()
    serializer_class = CompetitorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('platform'): qs = qs.filter(platform=p['platform'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        return qs


class CompetitorDataViewSet(viewsets.ModelViewSet):
    queryset = CompetitorData.objects.select_related('competitor').all()
    serializer_class = CompetitorDataSerializer


# ============== 13. 粉丝 ==============

class FanAnalysisViewSet(viewsets.ModelViewSet):
    queryset = FanAnalysis.objects.select_related('store').all()
    serializer_class = FanAnalysisSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        if p.get('start'): qs = qs.filter(date__gte=p['start'])
        if p.get('end'): qs = qs.filter(date__lte=p['end'])
        return qs

    @action(detail=False, methods=['get'])
    def trend(self, request):
        store_id = request.query_params.get('store_id')
        days = int(request.query_params.get('days', 30))
        qs = FanAnalysis.objects.filter(date__gte=date.today() - timedelta(days=days))
        if store_id:
            qs = qs.filter(store_id=store_id)
        data = list(qs.values('date', 'total_fans', 'new_fans', 'lost_fans', 'engagement_rate').order_by('date'))
        return Response(data)


# ============== 14. 营销活动 ==============

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related('store', 'creator').prefetch_related('products').all()
    serializer_class = CampaignSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        if p.get('campaign_type'): qs = qs.filter(campaign_type=p['campaign_type'])
        return qs


# ============== 15. 目标 ==============

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('employee', 'store').all()
    serializer_class = GoalSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('period'): qs = qs.filter(period=p['period'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        return qs

    @action(detail=False, methods=['get'])
    def board(self, request):
        period = request.query_params.get('period')
        if not period:
            return Response({'detail': '请提供period参数'}, status=400)
        goals = Goal.objects.filter(period=period).select_related('employee', 'store')
        data = GoalSerializer(goals, many=True).data
        summary = goals.aggregate(
            total_target=Sum('target_value'), total_actual=Sum('actual_value'),
            count=Count('id'), completed=Count('id', filter=Q(status='completed')),
        )
        return Response({'goals': data, 'summary': summary})


# ============== 16. 操作日志 ==============

class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.all()[:500]
    serializer_class = OperationLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('user'): qs = qs.filter(user=p['user'])
        if p.get('action'): qs = qs.filter(action=p['action'])
        if p.get('model_name'): qs = qs.filter(model_name=p['model_name'])
        return qs[:200]


# ============== 17. 实时大屏 ==============

class BillboardConfigViewSet(viewsets.ModelViewSet):
    queryset = BillboardConfig.objects.select_related('store').all()
    serializer_class = BillboardConfigSerializer

    @action(detail=False, methods=['get'])
    def data(self, request):
        from .services import DashboardService
        overview = DashboardService.get_overview()
        return Response(overview)


# ============== 18. 权限 ==============

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('members').all()
    serializer_class = RoleSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.select_related('employee', 'role').all()
    serializer_class = UserRoleSerializer


# ============== 19. 达人 ==============

class KOLContactViewSet(viewsets.ModelViewSet):
    queryset = KOLContact.objects.select_related('our_contact').all()
    serializer_class = KOLContactSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('platform'): qs = qs.filter(platform=p['platform'])
        if p.get('kw'): qs = qs.filter(Q(name__icontains=p['kw']) | Q(category__icontains=p['kw']))
        return qs


# ============== 20. 导出 ==============

class ExportTaskViewSet(viewsets.ModelViewSet):
    queryset = ExportTask.objects.all()
    serializer_class = ExportTaskSerializer

    @action(detail=False, methods=['post'])
    def create_export(self, request):
        export_type = request.data.get('export_type', 'sessions')
        params = json.dumps(request.data.get('params', {}))
        task = ExportTask.objects.create(
            name=f'{export_type}导出_{timezone.now().strftime("%Y%m%d%H%M%S")}',
            export_type=export_type,
            params=params,
            creator=request.data.get('creator', 'admin'),
        )
        try:
            csv_content = ExportTaskViewSet._generate_csv(export_type, request.data.get('params', {}))
            task.file_url = f'/media/exports/{task.id}.csv'
            task.file_size = len(csv_content.encode('utf-8-sig'))
            task.row_count = csv_content.count('\n') - 1
            task.status = 'done'
            task.completed_at = timezone.now()
            task.save()
            from django.http import HttpResponse
            response_data = ExportTaskSerializer(task).data
            response_data['csv_content'] = csv_content
            return Response(response_data)
        except Exception as e:
            task.status = 'failed'
            task.error_msg = str(e)
            task.save()
            return Response({'detail': str(e)}, status=500)

    @staticmethod
    def _generate_csv(export_type, params):
        from .models import LiveSession, Attendance as AttModel
        output = io.StringIO()
        writer = csv.writer(output)
        if export_type == 'sessions':
            writer.writerow(['日期', '主播', '店铺', 'GMV', '订单数', '时长(分)', '峰值观看', '转化率'])
            qs = LiveSession.objects.select_related('employee', 'store').order_by('-date')
            if params.get('start'): qs = qs.filter(date__gte=params['start'])
            if params.get('end'): qs = qs.filter(date__lte=params['end'])
            for s in qs[:5000]:
                writer.writerow([s.date, s.employee.name, s.store.name if s.store else '',
                                 s.gmv, s.orders, s.duration_minutes, s.peak_viewers, s.conversion_rate])
        elif export_type == 'attendance':
            writer.writerow(['员工', '打卡类型', '打卡时间', '结果', '迟到分钟'])
            qs = AttModel.objects.select_related('employee').order_by('-check_time')
            if params.get('start'): qs = qs.filter(check_time__date__gte=params['start'])
            if params.get('end'): qs = qs.filter(check_time__date__lte=params['end'])
            for a in qs[:5000]:
                writer.writerow([a.employee.name, a.get_check_type_display(), a.check_time,
                                 a.get_result_display(), a.late_minutes])
        elif export_type == 'finance':
            writer.writerow(['日期', '类型', '类目', '金额', '店铺', '备注'])
            qs = FinanceRecord.objects.select_related('store').order_by('-date')
            if params.get('start'): qs = qs.filter(date__gte=params['start'])
            if params.get('end'): qs = qs.filter(date__lte=params['end'])
            for f in qs[:5000]:
                writer.writerow([f.date, f.get_type_display(), f.get_category_display(),
                                 f.amount, f.store.name if f.store else '', f.remark])
        else:
            writer.writerow(['暂不支持该导出类型'])
        return output.getvalue()
