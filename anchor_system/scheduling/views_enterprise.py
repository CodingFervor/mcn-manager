from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from datetime import datetime

from .models_enterprise import (
    SystemAnnouncement, PermissionPolicy, AuditLog, DataBackup, HealthMonitor,
    IntegrationConfig, WorkflowTemplate, NotificationTemplate, ReportScheduler,
    ExportCenter, WhiteLabelConfig, MultiTenantConfig, LicenseManagement,
    RiskAssessment, DisasterRecovery, ComplianceAudit, SystemConfig,
    FeatureFlag, ApiKeyManagement, DeploymentRecord,
)
from .serializers_enterprise import (
    SystemAnnouncementSerializer, PermissionPolicySerializer, AuditLogSerializer,
    DataBackupSerializer, HealthMonitorSerializer, IntegrationConfigSerializer,
    WorkflowTemplateSerializer, NotificationTemplateSerializer, ReportSchedulerSerializer,
    ExportCenterSerializer, WhiteLabelConfigSerializer, MultiTenantConfigSerializer,
    LicenseManagementSerializer, RiskAssessmentSerializer, DisasterRecoverySerializer,
    ComplianceAuditSerializer, SystemConfigSerializer, FeatureFlagSerializer,
    ApiKeyManagementSerializer, DeploymentRecordSerializer,
)


# ============== 系统管理类 ==============


class SystemAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = SystemAnnouncement.objects.all()
    serializer_class = SystemAnnouncementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_type': dict(qs.values_list('type').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        instance = self.get_object()
        instance.is_active = True
        instance.published_at = datetime.now()
        instance.save()
        return Response({'message': '公告已发布', 'published_at': instance.published_at},
                        status=status.HTTP_200_OK)


class PermissionPolicyViewSet(viewsets.ModelViewSet):
    queryset = PermissionPolicy.objects.all()
    serializer_class = PermissionPolicySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_module': dict(qs.values_list('module').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_action': dict(qs.values_list('action').annotate(c=Count('id'))),
            'by_resource_type': dict(qs.values_list('resource_type').annotate(c=Count('id'))),
            'top_users': dict(
                qs.values_list('user').annotate(c=Count('id')).order_by('-c')[:10]
            ),
        })


class DataBackupViewSet(viewsets.ModelViewSet):
    queryset = DataBackup.objects.all()
    serializer_class = DataBackupSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_backup_type': dict(qs.values_list('backup_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_size': qs.aggregate(s=Sum('file_size'))['s'] or 0,
        })

    @action(detail=True, methods=['post'])
    def run_backup(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'running'
        instance.started_at = datetime.now()
        instance.save()
        return Response({'message': '备份任务已启动', 'backup_id': instance.id},
                        status=status.HTTP_200_OK)


class HealthMonitorViewSet(viewsets.ModelViewSet):
    queryset = HealthMonitor.objects.all()
    serializer_class = HealthMonitorSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_response_time': qs.aggregate(a=Avg('response_time'))['a'] or 0,
        })

    @action(detail=True, methods=['post'])
    def check_health(self, request, pk=None):
        instance = self.get_object()
        instance.last_check = datetime.now()
        # Simulate a health check result
        try:
            import random
            instance.response_time = random.randint(50, 500)
            instance.status = 'healthy' if instance.response_time < 300 else 'degraded'
            instance.error_message = ''
        except Exception as e:
            instance.status = 'down'
            instance.error_message = str(e)
        instance.save()
        return Response({
            'service': instance.service_name,
            'status': instance.status,
            'response_time': instance.response_time,
            'last_check': instance.last_check,
        }, status=status.HTTP_200_OK)


class IntegrationConfigViewSet(viewsets.ModelViewSet):
    queryset = IntegrationConfig.objects.all()
    serializer_class = IntegrationConfigSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_integration_type': dict(qs.values_list('integration_type').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTemplate.objects.all()
    serializer_class = WorkflowTemplateSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_trigger_type': dict(qs.values_list('trigger_type').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_channel': dict(qs.values_list('channel').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })


class ReportSchedulerViewSet(viewsets.ModelViewSet):
    queryset = ReportScheduler.objects.all()
    serializer_class = ReportSchedulerSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_format': dict(qs.values_list('format').annotate(c=Count('id'))),
            'by_report_type': dict(qs.values_list('report_type').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
        })


class ExportCenterViewSet(viewsets.ModelViewSet):
    queryset = ExportCenter.objects.all()
    serializer_class = ExportCenterSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'by_export_type': dict(qs.values_list('export_type').annotate(c=Count('id'))),
            'total_rows': qs.aggregate(s=Sum('total_rows'))['s'] or 0,
        })

    @action(detail=True, methods=['post'])
    def start_export(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'processing'
        instance.save()
        return Response({'message': '导出任务已启动', 'export_id': instance.id},
                        status=status.HTTP_200_OK)


class WhiteLabelConfigViewSet(viewsets.ModelViewSet):
    queryset = WhiteLabelConfig.objects.all()
    serializer_class = WhiteLabelConfigSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active_count': qs.filter(is_active=True).count(),
        })


class MultiTenantConfigViewSet(viewsets.ModelViewSet):
    queryset = MultiTenantConfig.objects.all()
    serializer_class = MultiTenantConfigSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_plan': dict(qs.values_list('plan').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
            'total_max_users': qs.aggregate(s=Sum('max_users'))['s'] or 0,
            'total_max_stores': qs.aggregate(s=Sum('max_stores'))['s'] or 0,
        })


class LicenseManagementViewSet(viewsets.ModelViewSet):
    queryset = LicenseManagement.objects.all()
    serializer_class = LicenseManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_license_type': dict(qs.values_list('license_type').annotate(c=Count('id'))),
            'active_count': qs.filter(is_active=True).count(),
            'total_activations': qs.aggregate(s=Sum('current_activations'))['s'] or 0,
        })


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_risk_type': dict(qs.values_list('risk_type').annotate(c=Count('id'))),
            'by_severity': dict(qs.values_list('severity').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })


class DisasterRecoveryViewSet(viewsets.ModelViewSet):
    queryset = DisasterRecovery.objects.all()
    serializer_class = DisasterRecoverySerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_dr_type': dict(qs.values_list('dr_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'avg_rpo': qs.aggregate(a=Avg('rpo'))['a'] or 0,
            'avg_rto': qs.aggregate(a=Avg('rto'))['a'] or 0,
        })


class ComplianceAuditViewSet(viewsets.ModelViewSet):
    queryset = ComplianceAudit.objects.all()
    serializer_class = ComplianceAuditSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_audit_type': dict(qs.values_list('audit_type').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
            'total_findings': qs.aggregate(s=Sum('findings'))['s'] or 0,
            'total_critical_findings': qs.aggregate(s=Sum('critical_findings'))['s'] or 0,
        })


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_category': dict(qs.values_list('category').annotate(c=Count('id'))),
            'public_count': qs.filter(is_public=True).count(),
        })


class FeatureFlagViewSet(viewsets.ModelViewSet):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'enabled_count': qs.filter(is_enabled=True).count(),
            'disabled_count': qs.filter(is_enabled=False).count(),
            'avg_rollout_percentage': qs.aggregate(a=Avg('rollout_percentage'))['a'] or 0,
        })


class ApiKeyManagementViewSet(viewsets.ModelViewSet):
    queryset = ApiKeyManagement.objects.all()
    serializer_class = ApiKeyManagementSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'active_count': qs.filter(is_active=True).count(),
            'avg_rate_limit': qs.aggregate(a=Avg('rate_limit'))['a'] or 0,
        })


class DeploymentRecordViewSet(viewsets.ModelViewSet):
    queryset = DeploymentRecord.objects.all()
    serializer_class = DeploymentRecordSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'by_environment': dict(qs.values_list('environment').annotate(c=Count('id'))),
            'by_status': dict(qs.values_list('status').annotate(c=Count('id'))),
        })
