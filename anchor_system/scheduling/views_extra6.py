from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg

from .models_extra6 import (
    RealtimeAnalytics, AudienceInsight, ConversionFunnel, ROIAnalysis,
    BenchmarkReport, CustomDashboard, DataImport,
    SalaryManagement, Recruitment, Onboarding, LeaveBalance,
    TeamCommunication, OKRManagement,
    BudgetManagement, ProfitAnalysis, InvoiceManagement,
    PaymentRecord, InsuranceRecord, LegalCase,
    QualityCheck, WorkflowAutomation, VendorRating,
    StockAlert, SLAManagement, FeedbackSystem,
)
from .serializers_extra6 import (
    RealtimeAnalyticsSerializer, AudienceInsightSerializer,
    ConversionFunnelSerializer, ROIAnalysisSerializer,
    BenchmarkReportSerializer, CustomDashboardSerializer,
    DataImportSerializer,
    SalaryManagementSerializer, RecruitmentSerializer,
    OnboardingSerializer, LeaveBalanceSerializer,
    TeamCommunicationSerializer, OKRManagementSerializer,
    BudgetManagementSerializer, ProfitAnalysisSerializer,
    InvoiceManagementSerializer,
    PaymentRecordSerializer, InsuranceRecordSerializer,
    LegalCaseSerializer,
    QualityCheckSerializer, WorkflowAutomationSerializer,
    VendorRatingSerializer,
    StockAlertSerializer, SLAManagementSerializer,
    FeedbackSystemSerializer,
)


# ============== 数据分析类 ==============

class RealtimeAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = RealtimeAnalytics.objects.all()
    serializer_class = RealtimeAnalyticsSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_metric_type': dict(qs.values_list('metric_type').annotate(c=Count('id'))),
            'by_source': dict(qs.values_list('source').annotate(c=Count('id'))),
        })


class AudienceInsightViewSet(viewsets.ModelViewSet):
    queryset = AudienceInsight.objects.all()
    serializer_class = AudienceInsightSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_gender': dict(qs.values_list('gender').annotate(c=Count('id'))),
            'by_spending_power': dict(qs.values_list('spending_power').annotate(c=Count('id'))),
            'avg_watch_time': qs.aggregate(a=Avg('avg_watch_time'))['a'] or 0,
        })


class ConversionFunnelViewSet(viewsets.ModelViewSet):
    queryset = ConversionFunnel.objects.all()
    serializer_class = ConversionFunnelSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_visitors': qs.aggregate(s=Sum('total_visitors'))['s'] or 0,
            'total_conversions': qs.aggregate(s=Sum('total_conversions'))['s'] or 0,
            'avg_overall_rate': qs.aggregate(a=Avg('overall_rate'))['a'] or 0,
        })


class ROIAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ROIAnalysis.objects.all()
    serializer_class = ROIAnalysisSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_investment': float(qs.aggregate(s=Sum('investment'))['s'] or 0),
            'total_revenue': float(qs.aggregate(s=Sum('revenue'))['s'] or 0),
            'avg_roi': qs.aggregate(a=Avg('roi'))['a'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class BenchmarkReportViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkReport.objects.all()
    serializer_class = BenchmarkReportSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
            'avg_ranking': qs.aggregate(a=Avg('ranking'))['a'] or 0,
            'by_category': dict(qs.values_list('category').annotate(c=Count('id'))),
        })


class CustomDashboardViewSet(viewsets.ModelViewSet):
    queryset = CustomDashboard.objects.all()
    serializer_class = CustomDashboardSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'shared': qs.filter(is_shared=True).count(),
            'default': qs.filter(is_default=True).count(),
        })


class DataImportViewSet(viewsets.ModelViewSet):
    queryset = DataImport.objects.all()
    serializer_class = DataImportSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_rows': qs.aggregate(s=Sum('total_rows'))['s'] or 0,
            'total_success': qs.aggregate(s=Sum('success_rows'))['s'] or 0,
            'total_failed': qs.aggregate(s=Sum('fail_rows'))['s'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


# ============== 团队管理类 ==============

class SalaryManagementViewSet(viewsets.ModelViewSet):
    queryset = SalaryManagement.objects.all()
    serializer_class = SalaryManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_net_salary': float(qs.aggregate(s=Sum('net_salary'))['s'] or 0),
            'avg_salary': float(qs.aggregate(a=Avg('net_salary'))['a'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class RecruitmentViewSet(viewsets.ModelViewSet):
    queryset = Recruitment.objects.all()
    serializer_class = RecruitmentSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_candidates': qs.aggregate(s=Sum('candidates_count'))['s'] or 0,
            'open_positions': qs.filter(status='open').count(),
        })


class OnboardingViewSet(viewsets.ModelViewSet):
    queryset = Onboarding.objects.all()
    serializer_class = OnboardingSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_completion': qs.aggregate(a=Avg('completion'))['a'] or 0,
            'completed': qs.filter(status='completed').count(),
        })


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_annual_used': qs.aggregate(s=Sum('annual_used'))['s'] or 0,
            'total_sick_used': qs.aggregate(s=Sum('sick_used'))['s'] or 0,
            'total_personal_used': qs.aggregate(s=Sum('personal_used'))['s'] or 0,
        })


class TeamCommunicationViewSet(viewsets.ModelViewSet):
    queryset = TeamCommunication.objects.all()
    serializer_class = TeamCommunicationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'total_members': qs.aggregate(s=Sum('members_count'))['s'] or 0,
            'total_messages': qs.aggregate(s=Sum('messages_count'))['s'] or 0,
            'by_channel_type': dict(qs.values_list('channel_type').annotate(c=Count('id'))),
        })


class OKRManagementViewSet(viewsets.ModelViewSet):
    queryset = OKRManagement.objects.all()
    serializer_class = OKRManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_progress': qs.aggregate(a=Avg('progress'))['a'] or 0,
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
        })


# ============== 财务法务类 ==============

class BudgetManagementViewSet(viewsets.ModelViewSet):
    queryset = BudgetManagement.objects.all()
    serializer_class = BudgetManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_allocated': float(qs.aggregate(s=Sum('allocated'))['s'] or 0),
            'total_spent': float(qs.aggregate(s=Sum('spent'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class ProfitAnalysisViewSet(viewsets.ModelViewSet):
    queryset = ProfitAnalysis.objects.all()
    serializer_class = ProfitAnalysisSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_revenue': float(qs.aggregate(s=Sum('revenue'))['s'] or 0),
            'total_cost': float(qs.aggregate(s=Sum('cost'))['s'] or 0),
            'total_net_profit': float(qs.aggregate(s=Sum('net_profit'))['s'] or 0),
            'avg_margin': qs.aggregate(a=Avg('margin'))['a'] or 0,
        })


class InvoiceManagementViewSet(viewsets.ModelViewSet):
    queryset = InvoiceManagement.objects.all()
    serializer_class = InvoiceManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_amount': float(qs.aggregate(s=Sum('amount'))['s'] or 0),
            'total_tax': float(qs.aggregate(s=Sum('tax'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class PaymentRecordViewSet(viewsets.ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_amount': float(qs.aggregate(s=Sum('amount'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'by_method': dict(qs.values_list('method').annotate(c=Count('id'))),
        })


class InsuranceRecordViewSet(viewsets.ModelViewSet):
    queryset = InsuranceRecord.objects.all()
    serializer_class = InsuranceRecordSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_premium': float(qs.aggregate(s=Sum('premium'))['s'] or 0),
            'total_coverage': float(qs.aggregate(s=Sum('coverage'))['s'] or 0),
            'by_insurance_type': dict(qs.values_list('insurance_type').annotate(c=Count('id'))),
        })


class LegalCaseViewSet(viewsets.ModelViewSet):
    queryset = LegalCase.objects.all()
    serializer_class = LegalCaseSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_case_type': dict(qs.values_list('case_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


# ============== 运营质控类 ==============

class QualityCheckViewSet(viewsets.ModelViewSet):
    queryset = QualityCheck.objects.all()
    serializer_class = QualityCheckSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_score': qs.aggregate(a=Avg('score'))['a'] or 0,
            'by_target_type': dict(qs.values_list('target_type').annotate(c=Count('id'))),
        })


class WorkflowAutomationViewSet(viewsets.ModelViewSet):
    queryset = WorkflowAutomation.objects.all()
    serializer_class = WorkflowAutomationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(is_active=True).count(),
            'total_runs': qs.aggregate(s=Sum('run_count'))['s'] or 0,
            'by_trigger_type': dict(qs.values_list('trigger_type').annotate(c=Count('id'))),
        })


class VendorRatingViewSet(viewsets.ModelViewSet):
    queryset = VendorRating.objects.all()
    serializer_class = VendorRatingSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'avg_overall_rating': qs.aggregate(a=Avg('overall_rating'))['a'] or 0,
            'avg_quality_score': qs.aggregate(a=Avg('quality_score'))['a'] or 0,
            'total_reviews': qs.aggregate(s=Sum('review_count'))['s'] or 0,
        })


class StockAlertViewSet(viewsets.ModelViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active': qs.filter(status='active').count(),
            'by_alert_type': dict(qs.values_list('alert_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class SLAManagementViewSet(viewsets.ModelViewSet):
    queryset = SLAManagement.objects.all()
    serializer_class = SLAManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'total_penalty': float(qs.aggregate(s=Sum('penalty'))['s'] or 0),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_target_value': qs.aggregate(a=Avg('target_value'))['a'] or 0,
        })


class FeedbackSystemViewSet(viewsets.ModelViewSet):
    queryset = FeedbackSystem.objects.all()
    serializer_class = FeedbackSystemSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_category': dict(qs.values_list('category').annotate(c=Count('id'))),
            'avg_rating': qs.aggregate(a=Avg('rating'))['a'] or 0,
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })
