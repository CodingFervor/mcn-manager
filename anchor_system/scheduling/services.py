from django.db.models import Sum, Avg, Count, Q, F, DecimalField
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, date
from decimal import Decimal
from functools import wraps
import hashlib
import json

from .models import (
    Store, Employee, Schedule, Attendance, LeaveRequest,
    LiveSession, ProductSales, KPIConfig, PerformanceReview
)


def cached_result(timeout=60, key_prefix=''):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            raw = json.dumps(kwargs, sort_keys=True, default=str)
            key = f'{key_prefix}:{hashlib.md5(raw.encode()).hexdigest()}'
            result = cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache(*prefixes):
    for prefix in prefixes:
        keys = cache.keys(f'{prefix}:*') if hasattr(cache, 'keys') else []
        for k in keys:
            cache.delete(k)


class DashboardService:
    @staticmethod
    @cached_result(timeout=60, key_prefix='dashboard')
    def get_overview(today=None):
        today = today or date.today()
        start_30 = today - timedelta(days=30)
        start_7 = today - timedelta(days=7)

        store_total = Store.objects.filter(status='active').count()
        anchor_total = Employee.objects.filter(role='anchor', is_active=True).count()
        operator_total = Employee.objects.filter(role__in=['operator', 'manager'], is_active=True).count()

        agg_30 = LiveSession.objects.filter(date__gte=start_30).aggregate(
            gmv=Sum('gmv'), orders=Sum('orders'), sessions=Count('id')
        )
        agg_today = LiveSession.objects.filter(date=today).aggregate(
            gmv=Sum('gmv'), orders=Sum('orders')
        )

        trend_7d = [
            {'d': r['date'].isoformat(), 'gmv': float(r['gmv'] or 0), 'orders': r['orders'] or 0}
            for r in LiveSession.objects.filter(date__gte=start_7).values('date').annotate(
                gmv=Sum('gmv'), orders=Sum('orders')
            ).order_by('date')
        ]

        today_scheds = Schedule.objects.filter(date=today).count()
        today_attended = Schedule.objects.filter(date=today, status__in=['checked_in', 'completed']).count()

        platform_dist = [
            {'platform': r['store__platform'], 'gmv': float(r['gmv'] or 0), 'sessions': r['sessions']}
            for r in LiveSession.objects.filter(date__gte=start_30).values('store__platform').annotate(
                gmv=Sum('gmv'), sessions=Count('id')
            ).order_by('-gmv')
        ]

        top_anchors = list(LiveSession.objects.filter(date__gte=start_7).values(
            'employee_id', 'employee__name'
        ).annotate(
            gmv=Sum('gmv'), sessions=Count('id')
        ).order_by('-gmv')[:8])

        return {
            'store_total': store_total,
            'anchor_total': anchor_total,
            'operator_total': operator_total,
            'monthly_gmv': float(agg_30['gmv'] or 0),
            'monthly_orders': int(agg_30['orders'] or 0),
            'monthly_sessions': int(agg_30['sessions'] or 0),
            'today_gmv': float(agg_today['gmv'] or 0),
            'today_orders': int(agg_today['orders'] or 0),
            'today_schedules': today_scheds,
            'today_attended': today_attended,
            'attendance_rate': round(today_attended / today_scheds * 100, 2) if today_scheds else 0,
            'pending_leave': LeaveRequest.objects.filter(status='pending').count(),
            'trend_7d': trend_7d,
            'platform_dist': platform_dist,
            'top_anchors': top_anchors,
        }


class StoreService:
    @staticmethod
    @cached_result(timeout=120, key_prefix='store_overview')
    def get_overview(start=None, end=None):
        today = date.today()
        start = start or today - timedelta(days=30)
        end = end or today

        stores = list(Store.objects.values('id', 'name', 'platform', 'status', 'brand_id', 'monthly_target'))
        store_ids = [s['id'] for s in stores]
        if not store_ids:
            return []

        gmv_by_store = dict(LiveSession.objects.filter(
            store_id__in=store_ids, date__gte=start, date__lte=end
        ).values('store_id').annotate(
            total_gmv=Sum('gmv'), session_count=Count('id')
        ).values_list('store_id', 'total_gmv'))

        count_by_store = dict(LiveSession.objects.filter(
            store_id__in=store_ids, date__gte=start, date__lte=end
        ).values('store_id').annotate(c=Count('id')).values_list('store_id', 'c'))

        anchor_by_store = dict(Employee.objects.filter(
            role='anchor', stores__id__in=store_ids
        ).values('stores').annotate(c=Count('id', distinct=True)).values_list('stores', 'c'))

        result = []
        for s in stores:
            gmv = float(gmv_by_store.get(s['id']) or 0)
            target = float(s['monthly_target'] or 0) * 10000
            result.append({
                'id': s['id'], 'name': s['name'], 'platform': s['platform'],
                'status': s['status'], 'brand': s['brand_id'],
                'monthly_target': s['monthly_target'],
                'monthly_gmv': gmv, 'sessions_count': count_by_store.get(s['id'], 0),
                'anchor_count': anchor_by_store.get(s['id'], 0),
                'target_rate': round(gmv / target * 100, 2) if target else 0,
            })
        result.sort(key=lambda x: x['monthly_gmv'], reverse=True)
        return result


class EmployeeService:
    @staticmethod
    @cached_result(timeout=300, key_prefix='emp_stats')
    def get_stats():
        total = Employee.objects.count()
        active = Employee.objects.filter(is_active=True).count()
        by_role = dict(Employee.objects.values_list('role').annotate(c=Count('id')).values_list('role', 'c'))
        return {'total': total, 'active': active, 'by_role': by_role}


class ScheduleService:
    @staticmethod
    def create_with_validation(data):
        employee_id = data.get('employee')
        date_v = data.get('date')
        shift_id = data.get('shift')
        if not (employee_id and date_v and shift_id):
            return None, '缺少必要参数'
        from .models import Shift
        if Schedule.objects.filter(employee_id=employee_id, date=date_v, shift_id=shift_id).exists():
            return None, '该员工在此班次已存在排班'
        shift = Shift.objects.get(id=shift_id)
        if Schedule.objects.filter(
            employee_id=employee_id, date=date_v
        ).filter(
            Q(shift__start_time__lt=shift.end_time) & Q(shift__end_time__gt=shift.start_time)
        ).exists():
            return None, '该员工在此时间段已有其他排班，时间冲突'
        return data, None

    @staticmethod
    def batch_create(items):
        from .serializers import ScheduleSerializer
        created, errors = [], []
        for idx, item in enumerate(items):
            serializer = ScheduleSerializer(data=item)
            if serializer.is_valid():
                try:
                    serializer.save()
                    created.append(serializer.data)
                except Exception as e:
                    errors.append({'index': idx, 'error': str(e)})
            else:
                errors.append({'index': idx, 'error': serializer.errors})
        return created, errors


class AttendanceService:
    @staticmethod
    def clock_in(employee_id=None, schedule_id=None, location='', photo=''):
        check_time = timezone.now()
        from .models import Shift
        if schedule_id:
            sched = Schedule.objects.select_related('shift').get(id=schedule_id)
            employee_id = sched.employee_id
        elif employee_id:
            sched = Schedule.objects.select_related('shift').filter(
                employee_id=employee_id, date=check_time.date()
            ).first()
        else:
            return None, '缺少参数'
        if not sched:
            return None, '今天没有找到对应排班'

        shift_start = timezone.datetime.combine(check_time.date(), sched.shift.start_time)
        late = (check_time - shift_start).total_seconds() / 60
        result = 'late' if late > sched.shift.late_minutes else 'normal'
        late_minutes = int(late) if result == 'late' else 0

        att = Attendance.objects.create(
            schedule=sched, employee_id=employee_id,
            check_type='clock_in', check_time=check_time,
            result=result, late_minutes=late_minutes,
            location=location, photo=photo,
        )
        Schedule.objects.filter(id=sched.id).update(status='checked_in')
        invalidate_cache('dashboard', 'store_overview')
        return att, None

    @staticmethod
    def clock_out(employee_id, location='', photo=''):
        check_time = timezone.now()
        sched = Schedule.objects.select_related('shift').filter(
            employee_id=employee_id, date=check_time.date()
        ).first()
        if not sched:
            return None, '今天没有排班'
        shift_end = timezone.datetime.combine(check_time.date(), sched.shift.end_time)
        result = 'overtime' if (shift_end - check_time).total_seconds() < 0 else 'normal'

        att = Attendance.objects.create(
            schedule=sched, employee_id=employee_id,
            check_type='clock_out', check_time=check_time,
            result=result, location=location, photo=photo,
        )
        Schedule.objects.filter(id=sched.id).update(status='completed')
        invalidate_cache('dashboard', 'store_overview')
        return att, None


class PerformanceService:
    @staticmethod
    def calculate(employee_id, period):
        if not employee_id or not period:
            return None, '缺少参数'
        year, month = period.split('-')
        start = date(int(year), int(month), 1)
        end = date(int(year), int(month) + 1, 1) - timedelta(days=1) if int(month) < 12 else date(int(year) + 1, 1, 1) - timedelta(days=1)

        employee = Employee.objects.get(id=employee_id)
        agg = LiveSession.objects.filter(employee=employee, date__gte=start, date__lte=end).aggregate(
            gmv=Sum('gmv'), orders=Sum('orders'), hours=Sum('duration_minutes'),
        )
        gmv = agg['gmv'] or 0
        orders = agg['orders'] or 0
        hours = (agg['hours'] or 0) / 60.0

        scheds = Schedule.objects.filter(employee=employee, date__gte=start, date__lte=end)
        total_scheds = scheds.count()
        attended = scheds.filter(status__in=['checked_in', 'completed']).count()
        att_rate = round(attended / total_scheds * 100, 2) if total_scheds else 100.0

        gmv_target = Decimal('0')
        kpi_gmv = KPIConfig.objects.filter(role=employee.role, metric='gmv', is_active=True).first()
        if kpi_gmv:
            gmv_target = kpi_gmv.target_value
        gmv_rate = round(float(gmv) / float(gmv_target) * 100, 2) if gmv_target else 0.0

        score = (
            min(gmv_rate, 150) / 150 * 60 +
            min(float(att_rate), 100) / 100 * 20 +
            min(hours / 60, 1) * 10 +
            min(orders / 100, 1) * 10
        )
        score = round(score, 2)

        if score >= 90: level = 'S'
        elif score >= 80: level = 'A'
        elif score >= 60: level = 'B'
        elif score >= 40: level = 'C'
        else: level = 'D'

        bonus = round(max(0, (score - 60) / 40) * float(employee.base_salary), 2) if score > 60 else 0

        review, _ = PerformanceReview.objects.update_or_create(
            employee=employee, period=period,
            defaults={
                'gmv': gmv, 'gmv_target': gmv_target, 'gmv_rate': gmv_rate,
                'orders': orders, 'live_hours': hours, 'attendance_rate': att_rate,
                'score': score, 'level': level, 'bonus': bonus,
            }
        )
        invalidate_cache('dashboard')
        return review, None


class LiveSessionService:
    @staticmethod
    @cached_result(timeout=120, key_prefix='daily_gmv')
    def get_daily_gmv(start=None, end=None, store_id=None):
        today = date.today()
        start = start or today - timedelta(days=30)
        end = end or today
        qs = LiveSession.objects.filter(date__gte=start, date__lte=end)
        if store_id:
            qs = qs.filter(store_id=store_id)
        return [
            {'d': r['date'].isoformat(), 'gmv': float(r['gmv'] or 0), 'orders': r['orders'] or 0, 'sessions': r['sessions']}
            for r in qs.values('date').annotate(
                gmv=Sum('gmv'), orders=Sum('orders'), sessions=Count('id')
            ).order_by('date')
        ]

    @staticmethod
    def get_top_anchors(start=None, end=None, limit=10):
        today = date.today()
        start = start or today - timedelta(days=30)
        end = end or today
        return list(LiveSession.objects.filter(date__gte=start, date__lte=end).values(
            'employee_id', 'employee__name'
        ).annotate(
            gmv=Sum('gmv'), orders=Sum('orders'),
            hours=Sum('duration_minutes'), sessions=Count('id'),
        ).order_by('-gmv')[:limit])
