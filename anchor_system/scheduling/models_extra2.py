from django.db import models
from .models import Store, Employee, StreamRoom, LiveSession


# ============== 1. 直播监控告警 ==============

class StreamAlert(models.Model):
    """直播监控告警"""
    ALERT_TYPES = [
        ('disconnect', '断流'), ('viewer_drop', '观众骤降'),
        ('gmv_drop', 'GMV异常'), ('overtime', '超时未下播'),
        ('keyword', '违规词'), ('custom', '自定义'),
    ]
    SEVERITY = [('info', '提示'), ('warning', '警告'), ('critical', '严重')]
    STATUS = [('pending', '待处理'), ('acknowledged', '已确认'), ('resolved', '已解决')]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直播间')
    session = models.ForeignKey(LiveSession, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直播场次')
    alert_type = models.CharField('告警类型', max_length=20, choices=ALERT_TYPES)
    severity = models.CharField('严重等级', max_length=10, choices=SEVERITY, default='warning')
    message = models.TextField('告警信息')
    metric_value = models.FloatField('当前值', null=True, blank=True)
    threshold = models.FloatField('阈值', null=True, blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    resolved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='处理人')
    resolved_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '直播告警'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_alert_type_display()}] {self.store.name}"


# ============== 2. 设备资产管理 ==============

class Asset(models.Model):
    """设备资产"""
    CATEGORIES = [
        ('camera', '摄像设备'), ('light', '灯光设备'), ('phone', '手机'),
        ('mic', '麦克风'), ('computer', '电脑'), ('prop', '道具'),
        ('display', '显示屏'), ('other', '其他'),
    ]
    STATUS = [('available', '空闲'), ('in_use', '使用中'), ('maintenance', '维修中'), ('retired', '已报废')]

    name = models.CharField('设备名称', max_length=100)
    category = models.CharField('设备类型', max_length=20, choices=CATEGORIES)
    brand_model = models.CharField('品牌型号', max_length=100, blank=True)
    serial_number = models.CharField('序列号', max_length=50, blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='available')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='使用人')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所在直播间')
    purchase_date = models.DateField('购入日期', null=True, blank=True)
    purchase_price = models.DecimalField('购入价格', max_digits=10, decimal_places=2, default=0)
    warranty_end = models.DateField('保修截止', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设备资产'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


# ============== 3. 知识库 ==============

class KnowledgeDocument(models.Model):
    """知识库文档"""
    CATEGORIES = [
        ('sop', 'SOP流程'), ('guide', '操作指南'), ('template', '模板'),
        ('best_practice', '最佳实践'), ('policy', '制度规范'), ('faq', 'FAQ'),
    ]
    STATUS = [('draft', '草稿'), ('published', '已发布'), ('archived', '已归档')]

    title = models.CharField('标题', max_length=200)
    category = models.CharField('分类', max_length=20, choices=CATEGORIES)
    content = models.TextField('内容')
    tags = models.CharField('标签', max_length=200, blank=True)
    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='作者')
    version = models.IntegerField('版本号', default=1)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='draft')
    view_count = models.IntegerField('浏览次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '知识文档'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


# ============== 4. 费用报销 ==============

class ExpenseClaim(models.Model):
    """费用报销"""
    CATEGORIES = [
        ('travel', '差旅'), ('equipment', '设备采购'), ('marketing', '营销推广'),
        ('office', '办公用品'), ('communication', '通讯费'), ('other', '其他'),
    ]
    STATUS = [('pending', '待审批'), ('approved', '已批准'), ('rejected', '已驳回'), ('paid', '已打款')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='申请人')
    title = models.CharField('报销事由', max_length=200)
    category = models.CharField('费用类型', max_length=20, choices=CATEGORIES)
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    description = models.TextField('详细说明', blank=True)
    receipt_url = models.URLField('凭证附件', blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_claims', verbose_name='审批人')
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    reject_reason = models.TextField('驳回原因', blank=True)
    paid_at = models.DateTimeField('打款时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '费用报销'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.name} - {self.title}"


# ============== 5. 客户投诉 ==============

class CustomerComplaint(models.Model):
    """客户投诉"""
    TYPES = [
        ('quality', '质量问题'), ('logistics', '物流问题'), ('service', '服务态度'),
        ('fake', '假冒伪劣'), ('description', '描述不符'), ('other', '其他'),
    ]
    STATUS = [('pending', '待处理'), ('processing', '处理中'), ('resolved', '已解决'), ('closed', '已关闭')]
    PRIORITY = [('low', '低'), ('medium', '中'), ('high', '高'), ('urgent', '紧急')]

    order_no = models.CharField('订单号', max_length=50)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    customer_name = models.CharField('客户姓名', max_length=50)
    contact = models.CharField('联系方式', max_length=50, blank=True)
    complaint_type = models.CharField('投诉类型', max_length=20, choices=TYPES)
    description = models.TextField('投诉内容')
    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    priority = models.CharField('优先级', max_length=10, choices=PRIORITY, default='medium')
    handler = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='处理人')
    resolution = models.TextField('处理结果', blank=True)
    resolved_at = models.DateTimeField('解决时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '客户投诉'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_no} - {self.get_complaint_type_display()}"


# ============== 6. 直播预告/排期 ==============

class StreamPlan(models.Model):
    """直播预告"""
    STATUS = [
        ('planned', '计划中'), ('confirmed', '已确认'),
        ('live', '直播中'), ('completed', '已完成'), ('cancelled', '已取消'),
    ]

    title = models.CharField('直播主题', max_length=200)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直播间')
    anchor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='主播')
    co_anchor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='co_anchored_plans', verbose_name='副播')
    planned_start = models.DateTimeField('计划开始')
    planned_end = models.DateTimeField('计划结束')
    status = models.CharField('状态', max_length=15, choices=STATUS, default='planned')
    theme = models.CharField('直播标签', max_length=100, blank=True)
    target_gmv = models.DecimalField('目标GMV', max_digits=12, decimal_places=2, default=0)
    target_viewers = models.IntegerField('目标观看人数', default=0)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '直播预告'
        ordering = ['planned_start']

    def __str__(self):
        return f"{self.title} ({self.planned_start:%m-%d %H:%M})"


# ============== 7. 打赏/礼物统计 ==============

class GiftRecord(models.Model):
    """打赏礼物记录"""
    GIFT_TYPES = [
        ('virtual', '虚拟礼物'), ('red_packet', '红包'), ('reward', '打赏'),
    ]

    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, verbose_name='直播场次')
    gift_name = models.CharField('礼物名称', max_length=50)
    gift_type = models.CharField('礼物类型', max_length=15, choices=GIFT_TYPES, default='virtual')
    quantity = models.IntegerField('数量', default=1)
    unit_value = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField('总价值', max_digits=12, decimal_places=2, default=0)
    sender_name = models.CharField('赠送人', max_length=50, blank=True)
    sender_id = models.CharField('赠送人ID', max_length=50, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '礼物记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.gift_name} x{self.quantity}"


# ============== 8. 粉丝群管理 ==============

class FanGroup(models.Model):
    """粉丝群"""
    PLATFORMS = [
        ('wechat', '微信群'), ('douyin', '抖音粉丝群'), ('kuaishou', '快手粉丝群'),
        ('xiaohongshu', '小红书群'), ('qq', 'QQ群'), ('other', '其他'),
    ]
    STATUS = [('active', '活跃'), ('inactive', '不活跃'), ('disbanded', '已解散')]

    name = models.CharField('群名称', max_length=100)
    platform = models.CharField('平台', max_length=20, choices=PLATFORMS)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联店铺')
    member_count = models.IntegerField('成员数', default=0)
    admin = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='管理员')
    qr_code_url = models.URLField('群二维码', blank=True)
    tags = models.CharField('标签', max_length=200, blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='active')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '粉丝群'
        ordering = ['-member_count']

    def __str__(self):
        return f"{self.name} ({self.member_count}人)"


# ============== 9. 数据报表 ==============

class DataReport(models.Model):
    """数据报表"""
    REPORT_TYPES = [('daily', '日报'), ('weekly', '周报'), ('monthly', '月报'), ('custom', '自定义')]
    CATEGORIES = [
        ('gmv', 'GMV报表'), ('traffic', '流量报表'), ('anchor', '主播报表'),
        ('product', '商品报表'), ('finance', '财务报表'), ('comprehensive', '综合报表'),
    ]
    STATUS = [('pending', '待生成'), ('generating', '生成中'), ('completed', '已完成'), ('failed', '生成失败')]

    title = models.CharField('报表名称', max_length=200)
    report_type = models.CharField('报表类型', max_length=15, choices=REPORT_TYPES)
    category = models.CharField('报表分类', max_length=20, choices=CATEGORIES)
    date_start = models.DateField('开始日期')
    date_end = models.DateField('结束日期')
    config = models.TextField('报表配置', blank=True)
    file_url = models.URLField('报表文件', blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    schedule = models.CharField('定时生成', max_length=15, default='none')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '数据报表'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ============== 10. 供应商管理 ==============

class Supplier(models.Model):
    """供应商"""
    CATEGORIES = [
        ('product', '商品供应'), ('equipment', '设备供应'),
        ('service', '服务供应'), ('logistics', '物流服务'), ('other', '其他'),
    ]
    STATUS = [('active', '合作中'), ('paused', '暂停合作'), ('terminated', '已终止')]

    name = models.CharField('供应商名称', max_length=100)
    contact_person = models.CharField('联系人', max_length=50)
    phone = models.CharField('电话', max_length=20)
    email = models.EmailField('邮箱', blank=True)
    address = models.TextField('地址', blank=True)
    category = models.CharField('供应类别', max_length=20, choices=CATEGORIES)
    status = models.CharField('合作状态', max_length=15, choices=STATUS, default='active')
    rating = models.IntegerField('评级(1-5)', default=3)
    main_products = models.CharField('主营产品', max_length=200, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '供应商'
        ordering = ['-rating']

    def __str__(self):
        return self.name
