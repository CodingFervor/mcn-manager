from django.db import models
from django.contrib.auth.models import User
from .models import Store, Employee


# ============== 1. 商品库管理 ==============

class ProductCategory(models.Model):
    """商品类目"""
    name = models.CharField('类目名称', max_length=50)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父类目')
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '商品类目'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品库"""
    STATUS = [('active', '在售'), ('inactive', '下架'), ('draft', '草稿')]
    name = models.CharField('商品名称', max_length=200)
    sku = models.CharField('SKU', max_length=50, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='类目')
    brand = models.CharField('品牌', max_length=100, blank=True)
    cover = models.URLField('主图', blank=True)
    price = models.DecimalField('售价', max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField('成本价', max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField('佣金比例(%)', max_digits=5, decimal_places=2, default=0)
    stock = models.IntegerField('库存', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='active')
    tags = models.CharField('标签', max_length=200, blank=True, help_text='逗号分隔')
    supplier = models.CharField('供应商', max_length=100, blank=True)
    supplier_contact = models.CharField('供应商联系方式', max_length=50, blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '商品'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status']), models.Index(fields=['category'])]

    def __str__(self):
        return self.name


# ============== 2. 库存预警 ==============

class InventoryAlert(models.Model):
    """库存预警规则"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts', verbose_name='商品')
    threshold = models.IntegerField('预警阈值', default=10)
    is_active = models.BooleanField('启用', default=True)
    last_alerted = models.DateTimeField('最后告警时间', null=True, blank=True)

    class Meta:
        verbose_name = '库存预警'
        unique_together = [('product',)]


# ============== 3. 直播脚本 ==============

class StreamScript(models.Model):
    """直播脚本/节目单"""
    STATUS = [('draft', '草稿'), ('active', '使用中'), ('archived', '已归档')]
    title = models.CharField('脚本标题', max_length=200)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='适用店铺')
    duration_minutes = models.IntegerField('预计时长(分钟)', default=120)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='draft')
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '直播脚本'
        ordering = ['-updated_at']


class ScriptSegment(models.Model):
    """脚本段落"""
    SEGMENT_TYPES = [
        ('warmup', '暖场'), ('product', '商品讲解'), ('interaction', '互动'),
        ('promotion', '促销活动'), ('flash_sale', '限时秒杀'), ('closing', '收尾'),
    ]
    script = models.ForeignKey(StreamScript, on_delete=models.CASCADE, related_name='segments', verbose_name='脚本')
    order = models.IntegerField('顺序', default=0)
    segment_type = models.CharField('段落类型', max_length=20, choices=SEGMENT_TYPES, default='product')
    title = models.CharField('标题', max_length=200)
    duration_minutes = models.IntegerField('时长(分钟)', default=10)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联商品')
    talking_points = models.TextField('话术要点', blank=True)
    note = models.CharField('备注', max_length=200, blank=True)

    class Meta:
        verbose_name = '脚本段落'
        ordering = ['script', 'order']


# ============== 4. 话术库 ==============

class SalesScript(models.Model):
    """话术模板库"""
    SCENE_CHOICES = [
        ('opening', '开场白'), ('product_intro', '商品介绍'), ('objection', '异议处理'),
        ('closing', '促单成交'), ('follow_up', '售后跟进'), ('interaction', '互动话术'),
        ('flash_sale', '秒杀话术'),
    ]
    title = models.CharField('话术标题', max_length=200)
    scene = models.CharField('适用场景', max_length=20, choices=SCENE_CHOICES, default='product_intro')
    content = models.TextField('话术内容')
    tags = models.CharField('标签', max_length=200, blank=True)
    use_count = models.IntegerField('使用次数', default=0)
    rating = models.DecimalField('评分', max_digits=3, decimal_places=1, default=0)
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '话术模板'
        ordering = ['-use_count']
        indexes = [models.Index(fields=['scene'])]


# ============== 5. 直播复盘 ==============

class StreamReview(models.Model):
    """直播复盘"""
    session = models.OneToOneField('scheduling.LiveSession', on_delete=models.CASCADE, related_name='review', verbose_name='直播场次')
    highlights = models.TextField('亮点', blank=True)
    issues = models.TextField('问题', blank=True)
    improvements = models.TextField('改进建议', blank=True)
    best_moments = models.TextField('高光时刻', blank=True)
    audience_feedback = models.TextField('观众反馈摘要', blank=True)
    next_action = models.TextField('下一步行动', blank=True)
    rating = models.IntegerField('自评(1-5)', default=3)
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='复盘人')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播复盘'
        ordering = ['-created_at']


# ============== 6. 任务看板 ==============

class TaskBoard(models.Model):
    """任务看板"""
    name = models.CharField('看板名称', max_length=100)
    team = models.CharField('团队', max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '任务看板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TaskCard(models.Model):
    """任务卡片"""
    PRIORITY = [('high', '高'), ('medium', '中'), ('low', '低')]
    STATUS = [('todo', '待办'), ('doing', '进行中'), ('done', '已完成'), ('blocked', '阻塞')]
    board = models.ForeignKey(TaskBoard, on_delete=models.CASCADE, related_name='cards', verbose_name='看板')
    title = models.CharField('标题', max_length=200)
    description = models.TextField('描述', blank=True)
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY, default='medium')
    status = models.CharField('状态', max_length=10, choices=STATUS, default='todo')
    assignee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='负责人')
    due_date = models.DateField('截止日期', null=True, blank=True)
    order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '任务卡片'
        ordering = ['board', 'status', 'order']
        indexes = [models.Index(fields=['status']), models.Index(fields=['assignee'])]


# ============== 7. 消息中心 ==============

class Notification(models.Model):
    """系统消息"""
    TYPE_CHOICES = [
        ('system', '系统通知'), ('schedule', '排班通知'), ('attendance', '考勤通知'),
        ('performance', '绩效通知'), ('leave', '请假通知'), ('alert', '预警通知'),
        ('contract', '合同通知'), ('task', '任务通知'),
    ]
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='system')
    target = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='接收人')
    is_read = models.BooleanField('已读', default=False)
    link = models.CharField('跳转链接', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '消息通知'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['target', 'is_read'])]


# ============== 8. 财务报表 ==============

class FinanceRecord(models.Model):
    """财务记录"""
    TYPE_CHOICES = [('income', '收入'), ('expense', '支出')]
    CATEGORY_CHOICES = [
        ('gmv', '直播GMV'), ('commission', '佣金收入'), ('salary', '工资'),
        ('bonus', '奖金'), ('equipment', '设备费用'), ('ads', '推广费用'),
        ('logistics', '物流费用'), ('other', '其他'),
    ]
    date = models.DateField('日期')
    type = models.CharField('类型', max_length=10, choices=TYPE_CHOICES)
    category = models.CharField('类目', max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联人员')
    remark = models.CharField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '财务记录'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type', 'category']),
            models.Index(fields=['store', 'date']),
        ]


# ============== 9. 佣金管理 ==============

class CommissionRule(models.Model):
    """佣金规则"""
    CALC_TYPE = [('fixed', '固定金额'), ('percent', '比例')]
    name = models.CharField('规则名称', max_length=100)
    calc_type = models.CharField('计算方式', max_length=10, choices=CALC_TYPE, default='percent')
    value = models.DecimalField('佣金值(金额或比例%)', max_digits=10, decimal_places=2)
    min_gmv = models.DecimalField('最低GMV门槛', max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '佣金规则'


class CommissionRecord(models.Model):
    """佣金结算记录"""
    STATUS = [('pending', '待结算'), ('settled', '已结算'), ('cancelled', '已取消')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='commissions', verbose_name='员工')
    period = models.CharField('结算周期', max_length=20, help_text='格式:2026-06')
    gmv = models.DecimalField('GMV', max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField('佣金金额', max_digits=10, decimal_places=2, default=0)
    rule = models.ForeignKey(CommissionRule, on_delete=models.SET_NULL, null=True, verbose_name='佣金规则')
    status = models.CharField('状态', max_length=20, choices=STATUS, default='pending')
    settled_at = models.DateTimeField('结算时间', null=True, blank=True)
    remark = models.CharField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '佣金记录'
        unique_together = [('employee', 'period')]
        ordering = ['-period']
        indexes = [models.Index(fields=['status'])]


# ============== 10. 合同管理 ==============

class Contract(models.Model):
    """合同管理"""
    TYPE_CHOICES = [('labor', '劳动合同'), ('service', '服务协议'), ('anchor', '主播合约'), ('brand', '品牌合作')]
    STATUS = [('active', '生效中'), ('expiring', '即将到期'), ('expired', '已过期'), ('terminated', '已终止')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contracts', verbose_name='员工')
    contract_type = models.CharField('合同类型', max_length=20, choices=TYPE_CHOICES, default='labor')
    contract_no = models.CharField('合同编号', max_length=50, blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('到期日期')
    status = models.CharField('状态', max_length=20, choices=STATUS, default='active')
    salary = models.DecimalField('合同薪资', max_digits=10, decimal_places=2, default=0)
    attachment = models.URLField('合同附件', blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '合同'
        ordering = ['-end_date']
        indexes = [models.Index(fields=['status']), models.Index(fields=['end_date'])]


# ============== 11. 培训管理 ==============

class TrainingCourse(models.Model):
    """培训课程"""
    STATUS = [('draft', '草稿'), ('active', '进行中'), ('completed', '已结束')]
    title = models.CharField('课程名称', max_length=200)
    description = models.TextField('课程简介', blank=True)
    trainer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='讲师')
    category = models.CharField('分类', max_length=50, blank=True)
    duration_minutes = models.IntegerField('时长(分钟)', default=60)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='draft')
    start_date = models.DateField('开始日期', null=True, blank=True)
    material_url = models.URLField('课件链接', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '培训课程'
        ordering = ['-created_at']


class TrainingRecord(models.Model):
    """培训记录"""
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='records', verbose_name='课程')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='trainings', verbose_name='学员')
    score = models.DecimalField('考核分数', max_digits=5, decimal_places=2, default=0)
    passed = models.BooleanField('是否通过', default=False)
    feedback = models.TextField('学员反馈', blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '培训记录'
        unique_together = [('course', 'employee')]


# ============== 12. 竞品分析 ==============

class Competitor(models.Model):
    """竞品信息"""
    name = models.CharField('竞品名称', max_length=100)
    platform = models.CharField('平台', max_length=20, default='douyin')
    account_id = models.CharField('账号ID', max_length=100, blank=True)
    followers = models.IntegerField('粉丝数', default=0)
    category = models.CharField('主营类目', max_length=50, blank=True)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '竞品'
        ordering = ['-followers']


class CompetitorData(models.Model):
    """竞品数据追踪"""
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='data', verbose_name='竞品')
    date = models.DateField('日期')
    followers = models.IntegerField('粉丝数', default=0)
    gmv_estimate = models.DecimalField('预估GMV', max_digits=12, decimal_places=2, default=0)
    live_sessions = models.IntegerField('直播场次', default=0)
    avg_viewers = models.IntegerField('场均观看', default=0)
    hot_products = models.CharField('热销商品', max_length=500, blank=True)
    note = models.TextField('备注', blank=True)

    class Meta:
        verbose_name = '竞品数据'
        ordering = ['-date']
        unique_together = [('competitor', 'date')]
        indexes = [models.Index(fields=['date'])]


# ============== 13. 粉丝分析 ==============

class FanAnalysis(models.Model):
    """粉丝分析数据"""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='fan_analysis', verbose_name='店铺')
    date = models.DateField('日期')
    total_fans = models.IntegerField('总粉丝数', default=0)
    new_fans = models.IntegerField('新增粉丝', default=0)
    lost_fans = models.IntegerField('流失粉丝', default=0)
    male_ratio = models.DecimalField('男性比例(%)', max_digits=5, decimal_places=2, default=0)
    age_18_24 = models.DecimalField('18-24岁(%)', max_digits=5, decimal_places=2, default=0)
    age_25_34 = models.DecimalField('25-34岁(%)', max_digits=5, decimal_places=2, default=0)
    age_35_44 = models.DecimalField('35-44岁(%)', max_digits=5, decimal_places=2, default=0)
    age_45plus = models.DecimalField('45岁以上(%)', max_digits=5, decimal_places=2, default=0)
    top_cities = models.CharField('TOP城市', max_length=200, blank=True, help_text='JSON数组')
    engagement_rate = models.DecimalField('互动率(%)', max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = '粉丝分析'
        unique_together = [('store', 'date')]
        ordering = ['-date']
        indexes = [models.Index(fields=['date'])]


# ============== 14. 活动营销 ==============

class Campaign(models.Model):
    """营销活动"""
    STATUS = [('draft', '草稿'), ('active', '进行中'), ('completed', '已结束'), ('cancelled', '已取消')]
    TYPE_CHOICES = [
        ('flash_sale', '限时秒杀'), ('coupon', '优惠券'), ('gift', '满赠'),
        ('discount', '折扣'), ('live_debut', '直播首发'), ('festival', '节日大促'),
    ]
    name = models.CharField('活动名称', max_length=200)
    campaign_type = models.CharField('活动类型', max_length=20, choices=TYPE_CHOICES, default='flash_sale')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    start_date = models.DateTimeField('开始时间')
    end_date = models.DateTimeField('结束时间')
    status = models.CharField('状态', max_length=20, choices=STATUS, default='draft')
    target_gmv = models.DecimalField('目标GMV', max_digits=12, decimal_places=2, default=0)
    actual_gmv = models.DecimalField('实际GMV', max_digits=12, decimal_places=2, default=0)
    budget = models.DecimalField('活动预算', max_digits=10, decimal_places=2, default=0)
    products = models.ManyToManyField(Product, blank=True, related_name='campaigns', verbose_name='活动商品')
    description = models.TextField('活动描述', blank=True)
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '营销活动'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status']), models.Index(fields=['start_date'])]


# ============== 15. 目标管理 ==============

class Goal(models.Model):
    """目标管理"""
    PERIOD = [('weekly', '周'), ('monthly', '月'), ('quarterly', '季'), ('yearly', '年')]
    STATUS = [('active', '进行中'), ('completed', '已完成'), ('failed', '未达成')]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='goals', verbose_name='员工')
    period_type = models.CharField('周期', max_length=20, choices=PERIOD, default='monthly')
    period = models.CharField('周期值', max_length=20, help_text='如2026-06')
    metric = models.CharField('指标', max_length=20, help_text='gmv/orders/hours/followers/conversion')
    target_value = models.DecimalField('目标值', max_digits=12, decimal_places=2, default=0)
    actual_value = models.DecimalField('实际值', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='active')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '目标'
        ordering = ['-period']
        indexes = [models.Index(fields=['employee', 'period'])]


# ============== 16. 运营日志 ==============

class OperationLog(models.Model):
    """运营操作日志"""
    user = models.CharField('操作人', max_length=50)
    action = models.CharField('操作', max_length=50)
    model_name = models.CharField('模型', max_length=50)
    object_id = models.CharField('对象ID', max_length=50, blank=True)
    detail = models.TextField('详情', blank=True)
    ip = models.CharField('IP', max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '操作日志'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]


# ============== 17. 实时大屏配置 ==============

class BillboardConfig(models.Model):
    """大屏展示配置"""
    name = models.CharField('配置名', max_length=100)
    is_default = models.BooleanField('默认配置', default=False)
    show_gmv = models.BooleanField('显示GMV', default=True)
    show_orders = models.BooleanField('显示订单', default=True)
    show_viewers = models.BooleanField('显示观看', default=True)
    show_top_anchors = models.BooleanField('显示主播排行', default=True)
    show_platform_dist = models.BooleanField('显示平台分布', default=True)
    show_trend = models.BooleanField('显示趋势', default=True)
    refresh_interval = models.IntegerField('刷新间隔(秒)', default=30)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='限定店铺')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '大屏配置'


# ============== 18. 权限管理 ==============

class Role(models.Model):
    """自定义角色"""
    name = models.CharField('角色名', max_length=50, unique=True)
    description = models.CharField('描述', max_length=200, blank=True)
    permissions = models.TextField('权限列表', blank=True, help_text='JSON数组，如["store:view","store:edit"]')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '角色'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """用户角色绑定"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='roles', verbose_name='员工')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='members', verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户角色'
        unique_together = [('employee', 'role')]


# ============== 19. 达人对接 ==============

class KOLContact(models.Model):
    """达人/KOL资源"""
    PLATFORM = [('douyin', '抖音'), ('kuaishou', '快手'), ('xiaohongshu', '小红书'), ('weibo', '微博')]
    STATUS = [('contacting', '接洽中'), ('negotiating', '谈判中'), ('cooperating', '合作中'), ('completed', '已结束')]
    name = models.CharField('达人名称', max_length=100)
    platform = models.CharField('平台', max_length=20, choices=PLATFORM, default='douyin')
    account_id = models.CharField('账号ID', max_length=100, blank=True)
    followers = models.IntegerField('粉丝数', default=0)
    category = models.CharField('领域', max_length=50, blank=True)
    contact_person = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系方式', max_length=50, blank=True)
    fee_estimate = models.DecimalField('预估合作费用', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='contacting')
    our_contact = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='我方对接人')
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '达人资源'
        ordering = ['-followers']
        indexes = [models.Index(fields=['status']), models.Index(fields=['platform'])]


# ============== 20. 数据导出 ==============

class ExportTask(models.Model):
    """数据导出任务"""
    STATUS = [('pending', '待处理'), ('processing', '处理中'), ('done', '已完成'), ('failed', '失败')]
    name = models.CharField('导出名称', max_length=200)
    export_type = models.CharField('导出类型', max_length=50, help_text='如 sessions/finance/attendance')
    params = models.TextField('查询参数', blank=True, help_text='JSON')
    file_url = models.URLField('文件链接', blank=True)
    file_size = models.BigIntegerField('文件大小(bytes)', default=0)
    row_count = models.IntegerField('数据行数', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS, default='pending')
    creator = models.CharField('创建人', max_length=50, blank=True)
    error_msg = models.TextField('错误信息', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '导出任务'
        ordering = ['-created_at']
