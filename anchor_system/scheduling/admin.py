from django.contrib import admin
from .models import (
    Brand, Store, Team, StreamRoom, Employee, AnchorProfile,
    Shift, Schedule, Attendance, LeaveRequest,
    LiveSession, ProductSales, KPIConfig, PerformanceReview
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'industry', 'contact', 'phone')
    search_fields = ('name', 'contact')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'platform', 'brand', 'status', 'monthly_target')
    list_filter = ('platform', 'status', 'brand')
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'leader')


@admin.register(StreamRoom)
class StreamRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'store', 'room_id', 'is_active')
    list_filter = ('store', 'is_active')


class AnchorProfileInline(admin.StackedInline):
    model = AnchorProfile
    can_delete = False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'role', 'team', 'phone', 'is_active', 'join_date')
    list_filter = ('role', 'team', 'is_active')
    search_fields = ('name', 'phone')
    inlines = [AnchorProfileInline]


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'start_time', 'end_time', 'color')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'shift', 'store', 'room', 'date', 'status')
    list_filter = ('date', 'status', 'store')
    search_fields = ('employee__name',)
    date_hierarchy = 'date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'check_type', 'check_time', 'result', 'late_minutes')
    list_filter = ('result', 'check_type')
    date_hierarchy = 'check_time'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'store', 'date', 'duration_minutes', 'gmv', 'orders')
    list_filter = ('date', 'store')
    date_hierarchy = 'date'


@admin.register(ProductSales)
class ProductSalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'product_name', 'quantity', 'gmv')


@admin.register(KPIConfig)
class KPIConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'metric', 'target_value', 'weight', 'period', 'is_active')


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'period', 'gmv', 'gmv_rate', 'score', 'level', 'bonus')
    list_filter = ('level', 'period')
