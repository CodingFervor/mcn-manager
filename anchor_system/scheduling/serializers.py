from rest_framework import serializers
from .models import (
    Brand, Store, Team, StreamRoom, Employee, AnchorProfile,
    Shift, Schedule, Attendance, LeaveRequest,
    LiveSession, ProductSales, KPIConfig, PerformanceReview
)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class StreamRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamRoom
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    room_count = serializers.IntegerField(read_only=True, default=0)
    employee_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Store
        fields = '__all__'

    def get_room_count(self, obj):
        return getattr(obj, '_room_count', 0) or 0

    def get_employee_count(self, obj):
        return getattr(obj, '_employee_count', 0) or 0


class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Team
        fields = '__all__'

    def get_member_count(self, obj):
        return getattr(obj, '_member_count', 0) or 0


class AnchorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnchorProfile
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    store_names = serializers.SerializerMethodField()
    anchor_profile = AnchorProfileSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def get_store_names(self, obj):
        return [s.name for s in obj.stores.all()]


class ShiftSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    time_range = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = '__all__'

    def get_time_range(self, obj):
        return f'{obj.start_time.strftime("%H:%M")} - {obj.end_time.strftime("%H:%M")}'


class ScheduleSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_role = serializers.CharField(source='employee.role', read_only=True)
    shift_name = serializers.CharField(source='shift.name', read_only=True)
    shift_color = serializers.CharField(source='shift.color', read_only=True)
    start_time = serializers.TimeField(source='shift.start_time', read_only=True)
    end_time = serializers.TimeField(source='shift.end_time', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    check_type_display = serializers.CharField(source='get_check_type_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = '__all__'


class ProductSalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSales
        fields = '__all__'


class LiveSessionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    products = ProductSalesSerializer(many=True, read_only=True)

    class Meta:
        model = LiveSession
        fields = '__all__'


class KPIConfigSerializer(serializers.ModelSerializer):
    metric_display = serializers.CharField(source='get_metric_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = KPIConfig
        fields = '__all__'


class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_role = serializers.CharField(source='employee.role', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = PerformanceReview
        fields = '__all__'
