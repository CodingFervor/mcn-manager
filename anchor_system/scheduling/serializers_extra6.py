from rest_framework import serializers
from .models_extra6 import (
    RealtimeAnalytics, AudienceInsight, ConversionFunnel, ROIAnalysis, BenchmarkReport,
    CustomDashboard, DataImport, SalaryManagement, Recruitment, Onboarding,
    LeaveBalance, TeamCommunication, OKRManagement, BudgetManagement, ProfitAnalysis,
    InvoiceManagement, PaymentRecord, InsuranceRecord, LegalCase, QualityCheck,
    WorkflowAutomation, VendorRating, StockAlert, SLAManagement, FeedbackSystem,
)


# ============== 数据分析类 ==============

class RealtimeAnalyticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RealtimeAnalytics
        fields = '__all__'


class AudienceInsightSerializer(serializers.ModelSerializer):

    class Meta:
        model = AudienceInsight
        fields = '__all__'


class ConversionFunnelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConversionFunnel
        fields = '__all__'


class ROIAnalysisSerializer(serializers.ModelSerializer):
    roi = serializers.SerializerMethodField()

    class Meta:
        model = ROIAnalysis
        fields = '__all__'

    def get_roi(self, obj):
        if obj.investment and obj.investment > 0:
            return round(obj.revenue / obj.investment * 100, 2)
        return 0


class BenchmarkReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = BenchmarkReport
        fields = '__all__'


class CustomDashboardSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomDashboard
        fields = '__all__'


class DataImportSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataImport
        fields = '__all__'


# ============== 团队管理类 ==============

class SalaryManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryManagement
        fields = '__all__'


class RecruitmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recruitment
        fields = '__all__'


class OnboardingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Onboarding
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveBalance
        fields = '__all__'


class TeamCommunicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamCommunication
        fields = '__all__'


class OKRManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = OKRManagement
        fields = '__all__'


# ============== 财务法务类 ==============

class BudgetManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = BudgetManagement
        fields = '__all__'


class ProfitAnalysisSerializer(serializers.ModelSerializer):
    margin = serializers.SerializerMethodField()
    gross_profit = serializers.SerializerMethodField()
    net_profit = serializers.SerializerMethodField()

    class Meta:
        model = ProfitAnalysis
        fields = '__all__'

    def get_margin(self, obj):
        if obj.revenue and obj.revenue > 0:
            return round(float(obj.net_profit) / float(obj.revenue) * 100, 2)
        return 0

    def get_gross_profit(self, obj):
        return obj.revenue - obj.cost

    def get_net_profit(self, obj):
        return obj.revenue - obj.cost - obj.operating_cost


class InvoiceManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceManagement
        fields = '__all__'


class PaymentRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentRecord
        fields = '__all__'


class InsuranceRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = InsuranceRecord
        fields = '__all__'


class LegalCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LegalCase
        fields = '__all__'


# ============== 运营质控类 ==============

class QualityCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualityCheck
        fields = '__all__'


class WorkflowAutomationSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowAutomation
        fields = '__all__'


class VendorRatingSerializer(serializers.ModelSerializer):
    overall_rating = serializers.SerializerMethodField()

    class Meta:
        model = VendorRating
        fields = '__all__'

    def get_overall_rating(self, obj):
        return round((obj.quality_score + obj.delivery_score + obj.service_score + obj.price_score) / 4, 2)


class StockAlertSerializer(serializers.ModelSerializer):
    is_low = serializers.SerializerMethodField()

    class Meta:
        model = StockAlert
        fields = '__all__'

    def get_is_low(self, obj):
        return obj.current_stock <= obj.threshold


class SLAManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = SLAManagement
        fields = '__all__'


class FeedbackSystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeedbackSystem
        fields = '__all__'
