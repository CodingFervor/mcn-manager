from django.db import models
from django.contrib.auth.models import User


# ============== 数据分析类 ==============

class RealtimeAnalytics(models.Model):
    metric_type = models.CharField('指标类型', max_length=50, choices=[('gmv', 'GMV'), ('viewers', '观看人数'), ('orders', '订单数'), ('conversion', '转化率'), ('engagement', '互动率')])
    value = models.FloatField('指标值', default=0)
    dimension = models.CharField('维度', max_length=50, blank=True)
    source = models.CharField('来源', max_length=50, default='live')
    timestamp = models.DateTimeField('时间戳')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '实时分析'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.metric_type}: {self.value}'


class AudienceInsight(models.Model):
    age_group = models.CharField('年龄段', max_length=20)
    gender = models.CharField('性别', max_length=10, choices=[('male', '男'), ('female', '女'), ('unknown', '未知')], default='unknown')
    location = models.CharField('地区', max_length=100, blank=True)
    interest = models.CharField('兴趣标签', max_length=200, blank=True)
    percentage = models.FloatField('占比%', default=0)
    avg_watch_time = models.IntegerField('平均观看时长(秒)', default=0)
    spending_power = models.CharField('消费力', max_length=20, choices=[('low', '低'), ('medium', '中'), ('high', '高')], default='medium')
    period = models.CharField('统计周期', max_length=20, default='monthly')
    source = models.CharField('数据来源', max_length=50, default='抖音')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '受众洞察'
        ordering = ['-id']

    def __str__(self):
        return f'{self.age_group} - {self.gender} - {self.location}'


class ConversionFunnel(models.Model):
    name = models.CharField('漏斗名称', max_length=100)
    stages = models.JSONField('阶段数据')
    conversion_rates = models.JSONField('转化率', default=dict)
    total_visitors = models.IntegerField('总访客', default=0)
    total_conversions = models.IntegerField('总转化', default=0)
    overall_rate = models.FloatField('总转化率%', default=0)
    period = models.CharField('统计周期', max_length=20)
    store_id = models.IntegerField('店铺ID', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '转化漏斗'
        ordering = ['-id']

    def __str__(self):
        return self.name


class ROIAnalysis(models.Model):
    campaign_name = models.CharField('活动名称', max_length=200)
    investment = models.DecimalField('投入金额', max_digits=12, decimal_places=2)
    revenue = models.DecimalField('产出金额', max_digits=12, decimal_places=2, default=0)
    roi = models.FloatField('ROI', default=0)
    cost_per_order = models.DecimalField('单均成本', max_digits=10, decimal_places=2, default=0)
    cost_per_click = models.DecimalField('点击成本', max_digits=10, decimal_places=2, default=0)
    period = models.CharField('统计周期', max_length=20)
    category = models.CharField('分类', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=[('active', '进行中'), ('completed', '已完成')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ROI分析'
        ordering = ['-id']

    def __str__(self):
        return self.campaign_name


class BenchmarkReport(models.Model):
    name = models.CharField('报告名称', max_length=200)
    category = models.CharField('分类', max_length=50)
    metrics = models.JSONField('指标数据')
    industry_avg = models.JSONField('行业平均', default=dict)
    ranking = models.IntegerField('排名', default=0)
    total_compared = models.IntegerField('对比总数', default=0)
    period = models.CharField('统计周期', max_length=20)
    score = models.FloatField('综合评分', default=0)
    generated_at = models.DateTimeField('生成时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '基准报告'
        ordering = ['-id']

    def __str__(self):
        return self.name


class CustomDashboard(models.Model):
    name = models.CharField('看板名称', max_length=100)
    owner = models.CharField('所有者', max_length=100, blank=True)
    layout = models.JSONField('布局配置', default=dict)
    widgets = models.JSONField('小组件', default=list)
    is_shared = models.BooleanField('是否共享', default=False)
    is_default = models.BooleanField('默认看板', default=False)
    refresh_interval = models.IntegerField('刷新间隔(秒)', default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '自定义看板'
        ordering = ['-id']

    def __str__(self):
        return self.name


class DataImport(models.Model):
    filename = models.CharField('文件名', max_length=200)
    import_type = models.CharField('导入类型', max_length=50, choices=[('products', '商品'), ('orders', '订单'), ('employees', '员工'), ('stores', '店铺'), ('analytics', '数据')])
    total_rows = models.IntegerField('总行数', default=0)
    success_rows = models.IntegerField('成功行数', default=0)
    fail_rows = models.IntegerField('失败行数', default=0)
    error_log = models.TextField('错误日志', blank=True)
    status = models.CharField('状态', max_length=20, choices=[('uploading', '上传中'), ('processing', '处理中'), ('completed', '已完成'), ('failed', '失败')], default='uploading')
    operator = models.CharField('操作人', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '数据导入'
        ordering = ['-id']

    def __str__(self):
        return self.filename


# ============== 团队管理类 ==============

class SalaryManagement(models.Model):
    employee_id = models.IntegerField('员工ID')
    employee_name = models.CharField('员工姓名', max_length=100, blank=True)
    base_salary = models.DecimalField('基本工资', max_digits=10, decimal_places=2)
    bonus = models.DecimalField('奖金', max_digits=10, decimal_places=2, default=0)
    commission = models.DecimalField('提成', max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField('扣款', max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField('实发工资', max_digits=10, decimal_places=2, default=0)
    period = models.CharField('工资周期', max_length=20)
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('confirmed', '已确认'), ('paid', '已发放')], default='draft')
    paid_at = models.DateTimeField('发放时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '薪资管理'
        ordering = ['-id']

    def __str__(self):
        return f'{self.employee_name} - {self.period}'


class Recruitment(models.Model):
    position = models.CharField('职位', max_length=100)
    department = models.CharField('部门', max_length=100, blank=True)
    candidates_count = models.IntegerField('候选人数量', default=0)
    status = models.CharField('状态', max_length=20, choices=[('open', '招聘中'), ('interviewing', '面试中'), ('offered', '已发offer'), ('filled', '已招满'), ('closed', '已关闭')], default='open')
    deadline = models.DateField('截止日期', null=True, blank=True)
    salary_range = models.CharField('薪资范围', max_length=100, blank=True)
    requirements = models.TextField('岗位要求', blank=True)
    description = models.TextField('职位描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '招聘管理'
        ordering = ['-id']

    def __str__(self):
        return self.position


class Onboarding(models.Model):
    employee_id = models.IntegerField('员工ID')
    employee_name = models.CharField('员工姓名', max_length=100, blank=True)
    progress = models.JSONField('进度', default=dict)
    mentor = models.CharField('导师', max_length=100, blank=True)
    start_date = models.DateField('入职日期')
    end_date = models.DateField('预计完成', null=True, blank=True)
    completion = models.FloatField('完成度%', default=0)
    status = models.CharField('状态', max_length=20, choices=[('in_progress', '进行中'), ('completed', '已完成'), ('overdue', '已逾期')], default='in_progress')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '员工入职'
        ordering = ['-id']

    def __str__(self):
        return f'{self.employee_name} - Onboarding'


class LeaveBalance(models.Model):
    employee_id = models.IntegerField('员工ID')
    employee_name = models.CharField('员工姓名', max_length=100, blank=True)
    annual_total = models.FloatField('年假总额', default=0)
    annual_used = models.FloatField('年假已用', default=0)
    sick_total = models.FloatField('病假总额', default=0)
    sick_used = models.FloatField('病假已用', default=0)
    personal_total = models.FloatField('事假总额', default=0)
    personal_used = models.FloatField('事假已用', default=0)
    year = models.IntegerField('年份')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '假期余额'
        ordering = ['-id']

    def __str__(self):
        return f'{self.employee_name} - {self.year}'


class TeamCommunication(models.Model):
    channel_name = models.CharField('频道名称', max_length=100)
    channel_type = models.CharField('类型', max_length=20, choices=[('group', '群聊'), ('direct', '私聊'), ('announcement', '公告')], default='group')
    members_count = models.IntegerField('成员数', default=0)
    messages_count = models.IntegerField('消息数', default=0)
    last_message = models.TextField('最后消息', blank=True)
    last_message_at = models.DateTimeField('最后消息时间', null=True, blank=True)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '团队沟通'
        ordering = ['-id']

    def __str__(self):
        return self.channel_name


class OKRManagement(models.Model):
    employee_id = models.IntegerField('员工ID')
    employee_name = models.CharField('员工姓名', max_length=100, blank=True)
    objective = models.CharField('目标', max_length=300)
    key_results = models.JSONField('关键结果')
    quarter = models.CharField('季度', max_length=10)
    progress = models.FloatField('进度%', default=0)
    score = models.FloatField('评分', default=0)
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('active', '进行中'), ('review', '评审中'), ('completed', '已完成')], default='draft')
    supervisor = models.CharField('上级', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'OKR管理'
        ordering = ['-id']

    def __str__(self):
        return f'{self.employee_name} - {self.quarter}'


# ============== 财务法务类 ==============

class BudgetManagement(models.Model):
    department = models.CharField('部门', max_length=100)
    category = models.CharField('预算类别', max_length=100)
    allocated = models.DecimalField('预算金额', max_digits=12, decimal_places=2)
    spent = models.DecimalField('已使用', max_digits=12, decimal_places=2, default=0)
    remaining = models.DecimalField('剩余', max_digits=12, decimal_places=2, default=0)
    usage_rate = models.FloatField('使用率%', default=0)
    period = models.CharField('周期', max_length=20)
    status = models.CharField('状态', max_length=20, choices=[('active', '执行中'), ('frozen', '冻结'), ('closed', '已关闭')], default='active')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '预算管理'
        ordering = ['-id']

    def __str__(self):
        return f'{self.department} - {self.category}'


class ProfitAnalysis(models.Model):
    revenue = models.DecimalField('收入', max_digits=12, decimal_places=2)
    cost = models.DecimalField('成本', max_digits=12, decimal_places=2)
    gross_profit = models.DecimalField('毛利', max_digits=12, decimal_places=2, default=0)
    operating_cost = models.DecimalField('运营费用', max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField('净利润', max_digits=12, decimal_places=2, default=0)
    margin = models.FloatField('利润率%', default=0)
    category = models.CharField('分类', max_length=50, blank=True)
    period = models.CharField('周期', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '利润分析'
        ordering = ['-id']

    def __str__(self):
        return f'{self.period} - {self.category}'


class InvoiceManagement(models.Model):
    invoice_no = models.CharField('发票号', max_length=50, unique=True)
    client = models.CharField('客户', max_length=200)
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    tax = models.DecimalField('税额', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('价税合计', max_digits=12, decimal_places=2, default=0)
    invoice_type = models.CharField('发票类型', max_length=20, choices=[('normal', '普通发票'), ('special', '专用发票'), ('electronic', '电子发票')], default='electronic')
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('issued', '已开具'), ('sent', '已发送'), ('paid', '已收款'), ('void', '已作废')], default='draft')
    issue_date = models.DateField('开票日期', null=True, blank=True)
    due_date = models.DateField('到期日期', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '发票管理'
        ordering = ['-id']

    def __str__(self):
        return self.invoice_no


class PaymentRecord(models.Model):
    invoice_no = models.CharField('关联发票', max_length=50, blank=True)
    payer = models.CharField('付款方', max_length=200, blank=True)
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    method = models.CharField('付款方式', max_length=20, choices=[('bank', '银行转账'), ('alipay', '支付宝'), ('wechat', '微信'), ('cash', '现金')], default='bank')
    status = models.CharField('状态', max_length=20, choices=[('pending', '待确认'), ('confirmed', '已确认'), ('failed', '失败')], default='pending')
    paid_at = models.DateTimeField('付款时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '收款记录'
        ordering = ['-id']

    def __str__(self):
        return f'{self.payer} - {self.amount}'


class InsuranceRecord(models.Model):
    insurance_type = models.CharField('保险类型', max_length=50, choices=[('employee', '员工保险'), ('property', '财产保险'), ('liability', '责任保险'), ('equipment', '设备保险')])
    provider = models.CharField('保险公司', max_length=100)
    policy_no = models.CharField('保单号', max_length=50)
    premium = models.DecimalField('保费', max_digits=10, decimal_places=2)
    coverage = models.DecimalField('保额', max_digits=12, decimal_places=2)
    start_date = models.DateField('生效日期')
    end_date = models.DateField('到期日期')
    beneficiary = models.CharField('受益人', max_length=100, blank=True)
    status = models.CharField('状态', max_length=20, choices=[('active', '生效中'), ('expired', '已到期'), ('cancelled', '已取消')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '保险记录'
        ordering = ['-id']

    def __str__(self):
        return f'{self.policy_no} - {self.insurance_type}'


class LegalCase(models.Model):
    title = models.CharField('案件名称', max_length=200)
    case_type = models.CharField('案件类型', max_length=20, choices=[('contract', '合同纠纷'), ('ip', '知识产权'), ('labor', '劳动纠纷'), ('tort', '侵权'), ('other', '其他')])
    parties = models.CharField('当事人', max_length=300, blank=True)
    status = models.CharField('状态', max_length=20, choices=[('filed', '已立案'), ('hearing', '审理中'), ('settled', '已和解'), ('closed', '已结案')], default='filed')
    filed_date = models.DateField('立案日期', null=True, blank=True)
    hearing_date = models.DateField('开庭日期', null=True, blank=True)
    outcome = models.TextField('结果', blank=True)
    lawyer = models.CharField('律师', max_length=100, blank=True)
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '法务案件'
        ordering = ['-id']

    def __str__(self):
        return self.title


# ============== 运营质控类 ==============

class QualityCheck(models.Model):
    target_type = models.CharField('检查对象', max_length=20, choices=[('stream', '直播'), ('video', '视频'), ('product', '商品'), ('service', '服务')])
    target_id = models.IntegerField('对象ID', null=True, blank=True)
    checker = models.CharField('检查人', max_length=100, blank=True)
    score = models.FloatField('评分', default=0)
    max_score = models.FloatField('满分', default=100)
    issues = models.JSONField('问题列表', default=list)
    suggestions = models.TextField('改进建议', blank=True)
    status = models.CharField('状态', max_length=20, choices=[('pending', '待检查'), ('passed', '合格'), ('failed', '不合格'), ('warning', '警告')], default='pending')
    checked_at = models.DateTimeField('检查时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '质量检查'
        ordering = ['-id']

    def __str__(self):
        return f'{self.target_type} - {self.score}/{self.max_score}'


class WorkflowAutomation(models.Model):
    name = models.CharField('工作流名称', max_length=100)
    trigger_type = models.CharField('触发类型', max_length=30, choices=[('schedule', '定时'), ('event', '事件'), ('manual', '手动'), ('webhook', 'Webhook')])
    trigger_config = models.JSONField('触发配置', default=dict)
    actions = models.JSONField('执行动作')
    is_active = models.BooleanField('启用', default=True)
    run_count = models.IntegerField('执行次数', default=0)
    last_run = models.DateTimeField('最后执行', null=True, blank=True)
    last_status = models.CharField('最后状态', max_length=20, choices=[('success', '成功'), ('failed', '失败')], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '工作流自动化'
        ordering = ['-id']

    def __str__(self):
        return self.name


class VendorRating(models.Model):
    vendor_name = models.CharField('供应商名称', max_length=100)
    vendor_id = models.IntegerField('供应商ID', null=True, blank=True)
    quality_score = models.FloatField('质量评分', default=0)
    delivery_score = models.FloatField('交付评分', default=0)
    service_score = models.FloatField('服务评分', default=0)
    price_score = models.FloatField('价格评分', default=0)
    overall_rating = models.FloatField('综合评分', default=0)
    review_count = models.IntegerField('评价数', default=0)
    period = models.CharField('评价周期', max_length=20)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '供应商评级'
        ordering = ['-overall_rating']

    def __str__(self):
        return f'{self.vendor_name} - {self.overall_rating}'


class StockAlert(models.Model):
    product_name = models.CharField('商品名称', max_length=200)
    product_id = models.IntegerField('商品ID', null=True, blank=True)
    warehouse = models.CharField('仓库', max_length=100, blank=True)
    current_stock = models.IntegerField('当前库存', default=0)
    threshold = models.IntegerField('预警阈值', default=10)
    alert_type = models.CharField('预警类型', max_length=20, choices=[('low', '库存不足'), ('overstock', '库存积压'), ('expiry', '即将过期'), ('damaged', '损坏')], default='low')
    status = models.CharField('状态', max_length=20, choices=[('active', '预警中'), ('resolved', '已处理'), ('ignored', '已忽略')], default='active')
    resolved_by = models.CharField('处理人', max_length=100, blank=True)
    resolved_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '库存预警'
        ordering = ['-id']

    def __str__(self):
        return f'{self.product_name} - {self.alert_type}'


class SLAManagement(models.Model):
    name = models.CharField('SLA名称', max_length=100)
    client = models.CharField('客户', max_length=200, blank=True)
    metric = models.CharField('指标', max_length=50)
    target_value = models.FloatField('目标值')
    actual_value = models.FloatField('实际值', default=0)
    unit = models.CharField('单位', max_length=20, default='%')
    penalty = models.DecimalField('违约金', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=[('meeting', '达标'), ('at_risk', '有风险'), ('breached', '违约')], default='meeting')
    period = models.CharField('周期', max_length=20)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'SLA管理'
        ordering = ['-id']

    def __str__(self):
        return self.name


class FeedbackSystem(models.Model):
    from_user = models.CharField('反馈人', max_length=100, blank=True)
    to_user = models.CharField('接收人', max_length=100, blank=True)
    category = models.CharField('分类', max_length=30, choices=[('performance', '绩效'), ('process', '流程'), ('product', '产品'), ('service', '服务'), ('suggestion', '建议'), ('complaint', '投诉')])
    content = models.TextField('反馈内容')
    rating = models.IntegerField('评分', default=5)
    is_anonymous = models.BooleanField('匿名', default=False)
    status = models.CharField('状态', max_length=20, choices=[('pending', '待处理'), ('reviewed', '已查看'), ('replied', '已回复'), ('closed', '已关闭')], default='pending')
    reply = models.TextField('回复', blank=True)
    replied_at = models.DateTimeField('回复时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '反馈系统'
        ordering = ['-id']

    def __str__(self):
        return f'{self.category} - {self.from_user}'
