from rest_framework import serializers
from .models_enterprise import (
    SystemAnnouncement, PermissionPolicy, AuditLog, DataBackup, HealthMonitor,
    IntegrationConfig, WorkflowTemplate, NotificationTemplate, ReportScheduler,
    ExportCenter, WhiteLabelConfig, MultiTenantConfig, LicenseManagement,
    RiskAssessment, DisasterRecovery, ComplianceAudit, SystemConfig,
    FeatureFlag, ApiKeyManagement, DeploymentRecord,
)


# ============== 系统管理类 ==============


class SystemAnnouncementSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemAnnouncement
        fields = '__all__'


class PermissionPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = PermissionPolicy
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'


class DataBackupSerializer(serializers.ModelSerializer):
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = DataBackup
        fields = '__all__'

    def get_file_size_display(self, obj):
        """Format bytes to human-readable size."""
        size = obj.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{round(size / 1024, 2)} KB'
        elif size < 1024 * 1024 * 1024:
            return f'{round(size / (1024 * 1024), 2)} MB'
        else:
            return f'{round(size / (1024 * 1024 * 1024), 2)} GB'


class HealthMonitorSerializer(serializers.ModelSerializer):
    uptime_display = serializers.SerializerMethodField()

    class Meta:
        model = HealthMonitor
        fields = '__all__'

    def get_uptime_display(self, obj):
        """Return uptime display based on last check and status."""
        if obj.status == 'down':
            return '0%'
        elif obj.status == 'degraded':
            return '50-99%'
        return '99.9%+'


class IntegrationConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = IntegrationConfig
        fields = '__all__'


class WorkflowTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowTemplate
        fields = '__all__'


class NotificationTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationTemplate
        fields = '__all__'


class ReportSchedulerSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportScheduler
        fields = '__all__'


class ExportCenterSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExportCenter
        fields = '__all__'


class WhiteLabelConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = WhiteLabelConfig
        fields = '__all__'


class MultiTenantConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = MultiTenantConfig
        fields = '__all__'


class LicenseManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = LicenseManagement
        fields = '__all__'


class RiskAssessmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RiskAssessment
        fields = '__all__'


class DisasterRecoverySerializer(serializers.ModelSerializer):

    class Meta:
        model = DisasterRecovery
        fields = '__all__'


class ComplianceAuditSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComplianceAudit
        fields = '__all__'


class SystemConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemConfig
        fields = '__all__'


class FeatureFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureFlag
        fields = '__all__'


class ApiKeyManagementSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApiKeyManagement
        fields = '__all__'


class DeploymentRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeploymentRecord
        fields = '__all__'
