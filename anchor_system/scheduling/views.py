from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta, date

from .models import (
    Brand, Store, Team, StreamRoom, Employee,
    Shift, Schedule, Attendance, LeaveRequest,
    LiveSession, ProductSales, KPIConfig, PerformanceReview
)
from .serializers import (
    BrandSerializer, StoreSerializer, TeamSerializer, StreamRoomSerializer,
    EmployeeSerializer, ShiftSerializer, ScheduleSerializer,
    AttendanceSerializer, LeaveRequestSerializer,
    LiveSessionSerializer, ProductSalesSerializer,
    KPIConfigSerializer, PerformanceReviewSerializer
)
from .services import (
    DashboardService, StoreService, EmployeeService,
    ScheduleService, AttendanceService, PerformanceService,
    LiveSessionService, invalidate_cache,
)


def parse_date(s, default=None):
    if not s:
        return default
    try:
        return timezone.datetime.fromisoformat(s).date()
    except Exception:
        return default


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class StreamRoomViewSet(viewsets.ModelViewSet):
    queryset = StreamRoom.objects.select_related('store').all()
    serializer_class = StreamRoomSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        store_id = self.request.query_params.get('store_id')
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.select_related('brand').annotate(
        _room_count=Count('rooms', distinct=True),
        _employee_count=Count('employees', distinct=True),
    ).all()
    serializer_class = StoreSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('platform'): qs = qs.filter(platform=p['platform'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('brand_id'): qs = qs.filter(brand_id=p['brand_id'])
        if p.get('kw'): qs = qs.filter(name__icontains=p['kw'])
        return qs

    @action(detail=False, methods=['get'])
    def overview(self, request):
        data = StoreService.get_overview(
            start=parse_date(request.query_params.get('start')),
            end=parse_date(request.query_params.get('end')),
        )
        return Response(data)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_cache('store_overview', 'dashboard')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_cache('store_overview', 'dashboard')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_cache('store_overview', 'dashboard')


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.annotate(_member_count=Count('members', distinct=True)).all()
    serializer_class = TeamSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('team', 'user').prefetch_related('stores', 'anchor_profile').all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('role'): qs = qs.filter(role=p['role'])
        if p.get('store_id'): qs = qs.filter(stores__id=p['store_id'])
        if p.get('team_id'): qs = qs.filter(team_id=p['team_id'])
        if p.get('is_active') is not None: qs = qs.filter(is_active=p['is_active'] == 'true')
        if p.get('kw'): qs = qs.filter(Q(name__icontains=p['kw']) | Q(phone__icontains=p['kw']))
        return qs.distinct()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        return Response(EmployeeService.get_stats())

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_cache('emp_stats', 'dashboard')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_cache('emp_stats', 'dashboard')


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related('employee', 'shift', 'store', 'room').all()
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('start'): qs = qs.filter(date__gte=p['start'])
        if p.get('end'): qs = qs.filter(date__lte=p['end'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('role'): qs = qs.filter(employee__role=p['role'])
        if p.get('status'): qs = qs.filter(status=p['status'])
        return qs

    def create(self, request, *args, **kwargs):
        data, err = ScheduleService.create_with_validation(request.data)
        if err:
            return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        start = parse_date(request.query_params.get('start'), date.today())
        end = start + timedelta(days=6)
        qs = self.get_queryset().filter(date__gte=start, date__lte=end)
        return Response({'start': start, 'end': end, 'items': ScheduleSerializer(qs, many=True).data})

    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        created, errors = ScheduleService.batch_create(request.data)
        return Response({'created': created, 'errors': errors})

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_cache('dashboard')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_cache('dashboard')


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee', 'schedule__shift').all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('start'): qs = qs.filter(check_time__date__gte=p['start'])
        if p.get('end'): qs = qs.filter(check_time__date__lte=p['end'])
        if p.get('result'): qs = qs.filter(result=p['result'])
        return qs

    @action(detail=False, methods=['post'])
    def clock_in(self, request):
        att, err = AttendanceService.clock_in(
            employee_id=request.data.get('employee_id'),
            schedule_id=request.data.get('schedule_id'),
            location=request.data.get('location', ''),
            photo=request.data.get('photo', ''),
        )
        if err:
            return Response({'detail': err}, status=400)
        return Response(AttendanceSerializer(att).data)

    @action(detail=False, methods=['post'])
    def clock_out(self, request):
        att, err = AttendanceService.clock_out(
            employee_id=request.data.get('employee_id'),
            location=request.data.get('location', ''),
            photo=request.data.get('photo', ''),
        )
        if err:
            return Response({'detail': err}, status=400)
        return Response(AttendanceSerializer(att).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        start = parse_date(request.query_params.get('start'), date.today() - timedelta(days=30))
        end = parse_date(request.query_params.get('end'), date.today())
        qs = Attendance.objects.filter(check_time__date__gte=start, check_time__date__lte=end)
        total = qs.count()
        by_result = dict(qs.values_list('result').annotate(c=Count('id')).values_list('result', 'c'))
        by_employee = qs.values('employee_id', 'employee__name').annotate(
            late=Count('id', filter=Q(result='late')),
            normal=Count('id', filter=Q(result='normal')),
        ).order_by('-late')[:20]
        return Response({
            'total': total, 'by_result': by_result,
            'top_late': list(by_employee), 'start': start, 'end': end,
        })


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee').all()
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('status'): qs = qs.filter(status=p['status'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        return qs

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.approver = request.data.get('approver', 'admin')
        leave.approve_remark = request.data.get('remark', '')
        leave.approve_time = timezone.now()
        leave.save()
        invalidate_cache('dashboard')
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.approver = request.data.get('approver', 'admin')
        leave.approve_remark = request.data.get('remark', '')
        leave.approve_time = timezone.now()
        leave.save()
        invalidate_cache('dashboard')
        return Response(LeaveRequestSerializer(leave).data)


class LiveSessionViewSet(viewsets.ModelViewSet):
    queryset = LiveSession.objects.select_related('employee', 'store', 'room').prefetch_related('products').all()
    serializer_class = LiveSessionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('store_id'): qs = qs.filter(store_id=p['store_id'])
        if p.get('start'): qs = qs.filter(date__gte=p['start'])
        if p.get('end'): qs = qs.filter(date__lte=p['end'])
        return qs

    @action(detail=False, methods=['get'])
    def daily_gmv(self, request):
        data = LiveSessionService.get_daily_gmv(
            start=parse_date(request.query_params.get('start')),
            end=parse_date(request.query_params.get('end')),
            store_id=request.query_params.get('store_id'),
        )
        return Response(data)

    @action(detail=False, methods=['get'])
    def top_anchors(self, request):
        data = LiveSessionService.get_top_anchors(
            start=parse_date(request.query_params.get('start')),
            end=parse_date(request.query_params.get('end')),
            limit=int(request.query_params.get('limit', 10)),
        )
        return Response(data)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_cache('daily_gmv', 'store_overview', 'dashboard')

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_cache('daily_gmv', 'store_overview', 'dashboard')

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_cache('daily_gmv', 'store_overview', 'dashboard')


class ProductSalesViewSet(viewsets.ModelViewSet):
    queryset = ProductSales.objects.select_related('session').all()
    serializer_class = ProductSalesSerializer


class KPIConfigViewSet(viewsets.ModelViewSet):
    queryset = KPIConfig.objects.all()
    serializer_class = KPIConfigSerializer


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.select_related('employee').all()
    serializer_class = PerformanceReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('period'): qs = qs.filter(period=p['period'])
        if p.get('employee_id'): qs = qs.filter(employee_id=p['employee_id'])
        if p.get('role'): qs = qs.filter(employee__role=p['role'])
        if p.get('level'): qs = qs.filter(level=p['level'])
        return qs

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        review, err = PerformanceService.calculate(
            employee_id=request.data.get('employee_id'),
            period=request.data.get('period'),
        )
        if err:
            return Response({'detail': err}, status=400)
        return Response(PerformanceReviewSerializer(review).data)


class DashboardView(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def overview(self, request):
        return Response(DashboardService.get_overview())
