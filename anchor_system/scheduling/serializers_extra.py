from rest_framework import serializers
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


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')

    class Meta:
        model = Product
        fields = '__all__'


class InventoryAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryAlert
        fields = '__all__'


class ScriptSegmentSerializer(serializers.ModelSerializer):
    segment_type_display = serializers.CharField(source='get_segment_type_display', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True, default='')

    class Meta:
        model = ScriptSegment
        fields = '__all__'


class StreamScriptSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    creator_name = serializers.CharField(source='creator.name', read_only=True, default='')
    store_name = serializers.CharField(source='store.name', read_only=True, default='')
    segments = ScriptSegmentSerializer(many=True, read_only=True)
    segment_count = serializers.SerializerMethodField()

    class Meta:
        model = StreamScript
        fields = '__all__'

    def get_segment_count(self, obj):
        return obj.segments.count()


class SalesScriptSerializer(serializers.ModelSerializer):
    scene_display = serializers.CharField(source='get_scene_display', read_only=True)
    creator_name = serializers.CharField(source='creator.name', read_only=True, default='')

    class Meta:
        model = SalesScript
        fields = '__all__'


class StreamReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.name', read_only=True, default='')

    class Meta:
        model = StreamReview
        fields = '__all__'


class TaskCardSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assignee_name = serializers.CharField(source='assignee.name', read_only=True, default='')

    class Meta:
        model = TaskCard
        fields = '__all__'


class TaskBoardSerializer(serializers.ModelSerializer):
    cards = TaskCardSerializer(many=True, read_only=True)
    card_count = serializers.SerializerMethodField()

    class Meta:
        model = TaskBoard
        fields = '__all__'

    def get_card_count(self, obj):
        return obj.cards.count()


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    target_name = serializers.CharField(source='target.name', read_only=True, default='')

    class Meta:
        model = Notification
        fields = '__all__'


class FinanceRecordSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True, default='')
    employee_name = serializers.CharField(source='employee.name', read_only=True, default='')

    class Meta:
        model = FinanceRecord
        fields = '__all__'


class CommissionRuleSerializer(serializers.ModelSerializer):
    calc_type_display = serializers.CharField(source='get_calc_type_display', read_only=True)

    class Meta:
        model = CommissionRule
        fields = '__all__'


class CommissionRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CommissionRecord
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Contract
        fields = '__all__'


class TrainingRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = TrainingRecord
        fields = '__all__'


class TrainingCourseSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trainer_name = serializers.CharField(source='trainer.name', read_only=True, default='')
    records = TrainingRecordSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingCourse
        fields = '__all__'


class CompetitorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorData
        fields = '__all__'


class CompetitorSerializer(serializers.ModelSerializer):
    data = CompetitorDataSerializer(many=True, read_only=True)

    class Meta:
        model = Competitor
        fields = '__all__'


class FanAnalysisSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = FanAnalysis
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    campaign_type_display = serializers.CharField(source='get_campaign_type_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True, default='')
    creator_name = serializers.CharField(source='creator.name', read_only=True, default='')
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'

    def get_completion_rate(self, obj):
        if obj.target_gmv:
            return round(float(obj.actual_gmv) / float(obj.target_gmv) * 100, 2)
        return 0


class GoalSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    period_type_display = serializers.CharField(source='get_period_type_display', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True, default='')
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = '__all__'

    def get_completion_rate(self, obj):
        if obj.target_value:
            return round(float(obj.actual_value) / float(obj.target_value) * 100, 2)
        return 0


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = '__all__'


class BillboardConfigSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True, default='')

    class Meta:
        model = BillboardConfig
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = '__all__'

    def get_member_count(self, obj):
        return obj.members.count()


class UserRoleSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = UserRole
        fields = '__all__'


class KOLContactSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    our_contact_name = serializers.CharField(source='our_contact.name', read_only=True, default='')

    class Meta:
        model = KOLContact
        fields = '__all__'


class ExportTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExportTask
        fields = '__all__'
