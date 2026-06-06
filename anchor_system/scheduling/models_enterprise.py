from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ============== 系统管理类 ==============


class SystemAnnouncement(models.Model):
    """系统公告"""
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    type = models.CharField('类型', max_length=20, choices=[
        ('info', '信息'), ('warning', '警告'), ('urgent', '紧急')
    ], default='info')
    priority = models.IntegerField('优先级', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    created_by = models.CharField('创建人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '系统公告'
        verbose_name_plural = '系统公告'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title


class PermissionPolicy(models.Model):
    """权限策略"""
    name = models.CharField('策略名称', max_length=100)
    code = models.CharField('策略编码', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    module = models.CharField('模块', max_length=50)
    actions = models.JSONField('操作列表', default=list)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '权限策略'
        verbose_name_plural = '权限策略'
        ordering = ['module', 'name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class AuditLog(models.Model):
    """审计日志"""
    user = models.CharField('用户', max_length=100)
    action = models.CharField('操作', max_length=50)
    resource_type = models.CharField('资源类型', max_length=50)
    resource_id = models.IntegerField('资源ID', null=True, blank=True)
    details = models.JSONField('详细信息', default=dict)
    ip_address = models.CharField('IP地址', max_length=50, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} - {self.resource_type}'


class DataBackup(models.Model):
    """数据备份"""
    name = models.CharField('备份名称', max_length=200)
    file_path = models.CharField('文件路径', max_length=500)
    file_size = models.BigIntegerField('文件大小', default=0)
    backup_type = models.CharField('备份类型', max_length=20, choices=[
        ('full', '全量备份'), ('incremental', '增量备份'), ('snapshot', '快照备份')
    ], default='full')
    status = models.CharField('状态', max_length=20, choices=[
        ('pending', '等待中'), ('running', '运行中'),
        ('completed', '已完成'), ('failed', '失败')
    ], default='pending')
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_by = models.CharField('创建人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '数据备份'
        verbose_name_plural = '数据备份'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class HealthMonitor(models.Model):
    """健康监控"""
    service_name = models.CharField('服务名称', max_length=100)
    endpoint_url = models.URLField('端点URL', max_length=500)
    status = models.CharField('状态', max_length=20, choices=[
        ('healthy', '健康'), ('degraded', '降级'), ('down', '宕机')
    ], default='healthy')
    response_time = models.IntegerField('响应时间', default=0, help_text='毫秒')
    last_check = models.DateTimeField('最后检查时间', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    check_interval = models.IntegerField('检查间隔', default=60, help_text='秒')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '健康监控'
        verbose_name_plural = '健康监控'
        ordering = ['service_name']

    def __str__(self):
        return f'{self.service_name} - {self.status}'


class IntegrationConfig(models.Model):
    """集成配置"""
    name = models.CharField('集成名称', max_length=100)
    integration_type = models.CharField('集成类型', max_length=20, choices=[
        ('erp', 'ERP'), ('crm', 'CRM'), ('payment', '支付'),
        ('analytics', '分析'), ('messaging', '消息'), ('oss', '对象存储')
    ])
    config = models.JSONField('配置', default=dict)
    api_endpoint = models.URLField('API端点', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    last_sync = models.DateTimeField('最后同步时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '集成配置'
        verbose_name_plural = '集成配置'
        ordering = ['integration_type', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_integration_type_display()})'


class WorkflowTemplate(models.Model):
    """工作流模板"""
    name = models.CharField('模板名称', max_length=100)
    description = models.TextField('描述', blank=True)
    trigger_type = models.CharField('触发类型', max_length=20, choices=[
        ('manual', '手动'), ('scheduled', '定时'), ('event', '事件')
    ], default='manual')
    trigger_config = models.JSONField('触发配置', default=dict)
    steps = models.JSONField('步骤列表', default=list)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '工作流模板'
        verbose_name_plural = '工作流模板'
        ordering = ['name']

    def __str__(self):
        return self.name


class NotificationTemplate(models.Model):
    """通知模板"""
    name = models.CharField('模板名称', max_length=100)
    code = models.CharField('模板编码', max_length=100, unique=True)
    channel = models.CharField('渠道', max_length=20, choices=[
        ('email', '邮件'), ('sms', '短信'), ('wechat', '微信'),
        ('push', '推送'), ('in_app', '站内信')
    ])
    subject = models.CharField('主题', max_length=200, blank=True)
    content = models.TextField('内容')
    variables = models.JSONField('变量列表', default=list)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'
        ordering = ['channel', 'name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class ReportScheduler(models.Model):
    """报表调度"""
    name = models.CharField('报表名称', max_length=100)
    report_type = models.CharField('报表类型', max_length=50)
    schedule_cron = models.CharField('Cron表达式', max_length=100, help_text='cron表达式')
    recipients = models.JSONField('收件人列表', default=list)
    format = models.CharField('格式', max_length=10, choices=[
        ('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')
    ], default='pdf')
    last_run = models.DateTimeField('最后运行时间', null=True, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '报表调度'
        verbose_name_plural = '报表调度'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ExportCenter(models.Model):
    """导出中心"""
    name = models.CharField('导出名称', max_length=200)
    export_type = models.CharField('导出类型', max_length=50)
    filters = models.JSONField('筛选条件', default=dict)
    file_url = models.URLField('文件URL', blank=True)
    file_size = models.BigIntegerField('文件大小', default=0)
    status = models.CharField('状态', max_length=20, choices=[
        ('pending', '等待中'), ('processing', '处理中'),
        ('completed', '已完成'), ('failed', '失败')
    ], default='pending')
    total_rows = models.IntegerField('总行数', default=0)
    created_by = models.CharField('创建人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '导出中心'
        verbose_name_plural = '导出中心'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class WhiteLabelConfig(models.Model):
    """白标配置"""
    brand_name = models.CharField('品牌名称', max_length=100)
    logo_url = models.URLField('Logo URL', blank=True)
    primary_color = models.CharField('主色调', max_length=7, default='#7c5cff')
    secondary_color = models.CharField('辅助色', max_length=7, default='#ff4d9e')
    domain = models.URLField('域名', blank=True)
    custom_css = models.TextField('自定义CSS', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '白标配置'
        verbose_name_plural = '白标配置'
        ordering = ['brand_name']

    def __str__(self):
        return self.brand_name


class MultiTenantConfig(models.Model):
    """多租户配置"""
    tenant_name = models.CharField('租户名称', max_length=100)
    tenant_code = models.CharField('租户编码', max_length=50, unique=True)
    plan = models.CharField('套餐', max_length=20, choices=[
        ('free', '免费版'), ('basic', '基础版'), ('pro', '专业版'), ('enterprise', '企业版')
    ], default='free')
    max_users = models.IntegerField('最大用户数', default=10)
    max_stores = models.IntegerField('最大店铺数', default=5)
    features = models.JSONField('功能列表', default=list)
    is_active = models.BooleanField('是否启用', default=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '多租户配置'
        verbose_name_plural = '多租户配置'
        ordering = ['tenant_name']

    def __str__(self):
        return f'{self.tenant_name} ({self.tenant_code})'


class LicenseManagement(models.Model):
    """许可证管理"""
    license_key = models.CharField('许可证密钥', max_length=200, unique=True)
    product_name = models.CharField('产品名称', max_length=100)
    license_type = models.CharField('许可证类型', max_length=20, choices=[
        ('trial', '试用版'), ('standard', '标准版'),
        ('professional', '专业版'), ('enterprise', '企业版')
    ], default='trial')
    max_activations = models.IntegerField('最大激活数', default=1)
    current_activations = models.IntegerField('当前激活数', default=0)
    issued_to = models.CharField('颁发对象', max_length=200)
    issued_at = models.DateTimeField('颁发时间')
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    is_active = models.BooleanField('是否有效', default=True)

    class Meta:
        verbose_name = '许可证管理'
        verbose_name_plural = '许可证管理'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.product_name} - {self.license_key[:16]}...'


class RiskAssessment(models.Model):
    """风险评估"""
    title = models.CharField('标题', max_length=200)
    risk_type = models.CharField('风险类型', max_length=20, choices=[
        ('operational', '运营风险'), ('financial', '财务风险'),
        ('compliance', '合规风险'), ('technology', '技术风险'), ('reputation', '声誉风险')
    ])
    severity = models.CharField('严重程度', max_length=20, choices=[
        ('low', '低'), ('medium', '中'), ('high', '高'), ('critical', '严重')
    ], default='low')
    probability = models.CharField('发生概率', max_length=20, choices=[
        ('low', '低'), ('medium', '中'), ('high', '高')
    ], default='low')
    description = models.TextField('描述')
    mitigation_plan = models.TextField('缓解计划', blank=True)
    status = models.CharField('状态', max_length=20, choices=[
        ('identified', '已识别'), ('analyzing', '分析中'),
        ('mitigated', '已缓解'), ('resolved', '已解决'), ('accepted', '已接受')
    ], default='identified')
    owner = models.CharField('负责人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '风险评估'
        verbose_name_plural = '风险评估'
        ordering = ['-severity', '-created_at']

    def __str__(self):
        return f'{self.title} - {self.get_severity_display()}'


class DisasterRecovery(models.Model):
    """灾备恢复"""
    name = models.CharField('名称', max_length=100)
    dr_type = models.CharField('灾备类型', max_length=20, choices=[
        ('backup', '备份'), ('failover', '故障转移'), ('replication', '复制')
    ])
    rpo = models.IntegerField('RPO', help_text='分钟')
    rto = models.IntegerField('RTO', help_text='分钟')
    config = models.JSONField('配置', default=dict)
    last_test = models.DateTimeField('最后测试时间', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=[
        ('active', '活跃'), ('testing', '测试中'), ('inactive', '未激活')
    ], default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '灾备恢复'
        verbose_name_plural = '灾备恢复'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_dr_type_display()})'


class ComplianceAudit(models.Model):
    """合规审计"""
    title = models.CharField('标题', max_length=200)
    audit_type = models.CharField('审计类型', max_length=20, choices=[
        ('internal', '内部审计'), ('external', '外部审计'), ('regulatory', '监管审计')
    ])
    standard = models.CharField('标准', max_length=50, help_text='例如 SOC2/GDPR/ISO27001')
    auditor = models.CharField('审计师', max_length=100, blank=True)
    status = models.CharField('状态', max_length=20, choices=[
        ('scheduled', '已计划'), ('in_progress', '进行中'),
        ('completed', '已完成'), ('failed', '未通过')
    ], default='scheduled')
    findings = models.IntegerField('发现项数', default=0)
    critical_findings = models.IntegerField('严重发现项数', default=0)
    start_date = models.DateTimeField('开始日期', null=True, blank=True)
    end_date = models.DateTimeField('结束日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '合规审计'
        verbose_name_plural = '合规审计'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.standard}'


class SystemConfig(models.Model):
    """系统配置"""
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    category = models.CharField('分类', max_length=50)
    description = models.TextField('描述', blank=True)
    is_public = models.BooleanField('是否公开', default=False)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['category', 'key']

    def __str__(self):
        return f'{self.category}: {self.key}'


class FeatureFlag(models.Model):
    """功能开关"""
    name = models.CharField('功能名称', max_length=100, unique=True)
    code = models.CharField('功能编码', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    is_enabled = models.BooleanField('是否启用', default=False)
    target_users = models.JSONField('目标用户', default=list)
    rollout_percentage = models.IntegerField(
        '灰度比例',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '功能开关'
        verbose_name_plural = '功能开关'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({"开启" if self.is_enabled else "关闭"})'


class ApiKeyManagement(models.Model):
    """API密钥管理"""
    name = models.CharField('名称', max_length=100)
    key_hash = models.CharField('密钥哈希', max_length=200, unique=True)
    permissions = models.JSONField('权限列表', default=list)
    rate_limit = models.IntegerField('速率限制', default=1000, help_text='每小时请求数')
    last_used = models.DateTimeField('最后使用时间', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.CharField('创建人', max_length=100, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'API密钥管理'
        verbose_name_plural = 'API密钥管理'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class DeploymentRecord(models.Model):
    """部署记录"""
    version = models.CharField('版本号', max_length=50)
    environment = models.CharField('环境', max_length=20, choices=[
        ('development', '开发环境'), ('staging', '预发布环境'), ('production', '生产环境')
    ])
    description = models.TextField('描述', blank=True)
    changelog = models.TextField('更新日志', blank=True)
    deployed_by = models.CharField('部署人', max_length=100, blank=True)
    deployed_at = models.DateTimeField('部署时间')
    status = models.CharField('状态', max_length=20, choices=[
        ('pending', '等待中'), ('deploying', '部署中'),
        ('running', '运行中'), ('rollback', '已回滚'), ('failed', '失败')
    ], default='pending')
    rollback_version = models.CharField('回滚版本', max_length=50, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '部署记录'
        verbose_name_plural = '部署记录'
        ordering = ['-deployed_at']

    def __str__(self):
        return f'{self.version} - {self.get_environment_display()}'
