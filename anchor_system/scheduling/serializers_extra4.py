from rest_framework import serializers
from .models_extra4 import (
    LiveInteraction, Coupon, FlashSale, RoomDecoration, ScriptTag,
    SignContract, BusinessNegotiation, Investment, ContractLedger, Authorization,
    CompetitorRoom, TrafficAnalysis, UserPersona, ABTest, DataWarning,
    Settlement, Logistics, Inventory, ReturnAnalysis, TaxRecord,
)


# ============== 运营管理类 ==============

class LiveInteractionSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source='session.title', read_only=True)

    class Meta:
        model = LiveInteraction
        fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Coupon
        fields = '__all__'


class FlashSaleSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    session_title = serializers.CharField(source='session.title', read_only=True)
    sell_rate = serializers.SerializerMethodField()

    class Meta:
        model = FlashSale
        fields = '__all__'

    def get_sell_rate(self, obj):
        if obj.total_stock > 0:
            return round(obj.sold_count / obj.total_stock * 100, 2)
        return 0


class RoomDecorationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = RoomDecoration
        fields = '__all__'


class ScriptTagSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = ScriptTag
        fields = '__all__'

    def get_child_count(self, obj):
        return obj.children.count()


# ============== 商务拓展类 ==============

class SignContractSerializer(serializers.ModelSerializer):
    anchor_name = serializers.CharField(source='anchor.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = SignContract
        fields = '__all__'

    def get_days_remaining(self, obj):
        from datetime import date
        if obj.end_date and obj.status == 'active':
            delta = (obj.end_date - date.today()).days
            return max(delta, 0)
        return None


class BusinessNegotiationSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    anchor_name = serializers.CharField(source='anchor.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = BusinessNegotiation
        fields = '__all__'


class InvestmentSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Investment
        fields = '__all__'


class ContractLedgerSerializer(serializers.ModelSerializer):
    days_to_expire = serializers.SerializerMethodField()

    class Meta:
        model = ContractLedger
        fields = '__all__'

    def get_days_to_expire(self, obj):
        from datetime import date
        if obj.end_date:
            delta = (obj.end_date - date.today()).days
            return delta
        return None


class AuthorizationSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    anchor_name = serializers.CharField(source='anchor.name', read_only=True)

    class Meta:
        model = Authorization
        fields = '__all__'


# ============== 数据与策略类 ==============

class CompetitorRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitorRoom
        fields = '__all__'


class TrafficAnalysisSerializer(serializers.ModelSerializer):
    session_title = serializers.CharField(source='session.title', read_only=True)

    class Meta:
        model = TrafficAnalysis
        fields = '__all__'


class UserPersonaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPersona
        fields = '__all__'


class ABTestSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    lift = serializers.SerializerMethodField()

    class Meta:
        model = ABTest
        fields = '__all__'

    def get_lift(self, obj):
        if obj.control_metric and obj.control_metric > 0:
            return round((obj.test_metric - obj.control_metric) / obj.control_metric * 100, 2)
        return None


class DataWarningSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataWarning
        fields = '__all__'


# ============== 财务与供应链类 ==============

class SettlementSerializer(serializers.ModelSerializer):
    anchor_name = serializers.CharField(source='anchor.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Settlement
        fields = '__all__'


class LogisticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logistics
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    available = serializers.SerializerMethodField()
    is_low = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = '__all__'

    def get_available(self, obj):
        return obj.quantity - obj.locked_quantity

    def get_is_low(self, obj):
        return (obj.quantity - obj.locked_quantity) <= obj.safety_stock


class ReturnAnalysisSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    anchor_name = serializers.CharField(source='anchor.name', read_only=True)

    class Meta:
        model = ReturnAnalysis
        fields = '__all__'


class TaxRecordSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = TaxRecord
        fields = '__all__'
