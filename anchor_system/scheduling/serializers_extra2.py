from rest_framework import serializers
from .models_extra2 import (
    StreamAlert, Asset, KnowledgeDocument, ExpenseClaim, CustomerComplaint,
    StreamPlan, GiftRecord, FanGroup, DataReport, Supplier,
)


class StreamAlertSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    room_name = serializers.CharField(source='room.name', default='', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.name', default='', read_only=True)

    class Meta:
        model = StreamAlert
        fields = '__all__'


class AssetSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.name', default='', read_only=True)
    room_name = serializers.CharField(source='room.name', default='', read_only=True)

    class Meta:
        model = Asset
        fields = '__all__'


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', default='', read_only=True)
    category_display = serializers.CharField(source='get_category_display', default='', read_only=True)

    class Meta:
        model = KnowledgeDocument
        fields = '__all__'


class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', default='', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.name', default='', read_only=True)
    category_display = serializers.CharField(source='get_category_display', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = ExpenseClaim
        fields = '__all__'


class CustomerComplaintSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    handler_name = serializers.CharField(source='handler.name', default='', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', default='', read_only=True)

    class Meta:
        model = CustomerComplaint
        fields = '__all__'


class StreamPlanSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    room_name = serializers.CharField(source='room.name', default='', read_only=True)
    anchor_name = serializers.CharField(source='anchor.name', default='', read_only=True)
    co_anchor_name = serializers.CharField(source='co_anchor.name', default='', read_only=True)
    status_display = serializers.CharField(source='get_status_display', default='', read_only=True)

    class Meta:
        model = StreamPlan
        fields = '__all__'


class GiftRecordSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source='session.__str__', default='', read_only=True)

    class Meta:
        model = GiftRecord
        fields = '__all__'


class FanGroupSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', default='', read_only=True)
    admin_name = serializers.CharField(source='admin.name', default='', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', default='', read_only=True)

    class Meta:
        model = FanGroup
        fields = '__all__'


class DataReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', default='', read_only=True)
    category_display = serializers.CharField(source='get_category_display', default='', read_only=True)

    class Meta:
        model = DataReport
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', default='', read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'
