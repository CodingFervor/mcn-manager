from django.db import models
from django.contrib.auth.models import User
from .models import Store, Employee, StreamRoom, LiveSession
from .models_extra import Product


# ============== 1. 选品管理 ==============

class ProductSelection(models.Model):
    """选品记录 - 选品会核心流程"""
    STATUS = [
        ('pending', '待评估'), ('shortlisted', '已入选'), ('rejected', '已淘汰'),
        ('testing', '试样中'), ('confirmed', '已确认'), ('archived', '已归档'),
    ]
    SCORE_DIMENSIONS = [
        ('commission', '佣金空间'), ('market', '市场热度'), ('quality', '品质评分'),
        ('supply', '供货稳定'), ('margin', '利润空间'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='目标店铺')
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='供应商')
    suggested_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='推荐人')

    commission_score = models.IntegerField('佣金评分(1-10)', default=5)
    market_score = models.IntegerField('市场评分(1-10)', default=5)
    quality_score = models.IntegerField('品质评分(1-10)', default=5)
    supply_score = models.IntegerField('供应评分(1-10)', default=5)
    margin_score = models.IntegerField('利润评分(1-10)', default=5)
    total_score = models.FloatField('综合得分', default=0)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    meeting_notes = models.TextField('选品会讨论', blank=True)
    decision_reason = models.TextField('决策理由', blank=True)
    planned_stream_date = models.DateField('计划直播日期', null=True, blank=True)
    target_gmv = models.DecimalField('目标GMV', max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '选品记录'
        ordering = ['-total_score']

    def __str__(self):
        return f"{self.product_id} - {self.get_status_display()} ({self.total_score})"

    def save(self, *args, **kwargs):
        self.total_score = (self.commission_score + self.market_score + self.quality_score +
                            self.supply_score + self.margin_score) / 5.0
        super().save(*args, **kwargs)


# ============== 2. 样品管理 ==============

class Sample(models.Model):
    """样品管理"""
    STATUS = [
        ('requested', '已申请'), ('shipped', '已发货'), ('received', '已收到'),
        ('testing', '测试中'), ('approved', '合格'), ('rejected_sample', '不合格'),
        ('in_stream', '直播使用中'), ('returned', '已归还'), ('lost', '已丢失'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, verbose_name='供应商')
    name = models.CharField('样品名称', max_length=200)
    quantity = models.IntegerField('数量', default=1)
    batch_no = models.CharField('批次号', max_length=50, blank=True)
    status = models.CharField('状态', max_length=15, choices=STATUS, default='requested')

    requested_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                     related_name='requested_samples', verbose_name='申请人')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='assigned_samples', verbose_name='使用人')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联店铺')

    shipped_date = models.DateField('发货日期', null=True, blank=True)
    received_date = models.DateField('收到日期', null=True, blank=True)
    test_result = models.TextField('测试结果', blank=True)
    return_deadline = models.DateField('归还截止', null=True, blank=True)
    notes = models.TextField('备注', blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '样品'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# ============== 3. 流量投放 ==============

class AdCampaign(models.Model):
    """流量投放 - DOU+/千川/_feed广告"""
    PLATFORMS = [('douyin', '巨量千川'), ('kuaishou', '磁力金牛'), ('xiaohongshu', '薯条'), ('other', '其他')]
    AD_TYPES = [('live', '直播间推广'), ('video', '短视频推广'), ('product', '商品推广')]
    STATUS = [('draft', '草稿'), ('running', '投放中'), ('paused', '已暂停'), ('completed', '已结束'), ('failed', '失败')]

    name = models.CharField('投放名称', max_length=200)
    platform = models.CharField('投放平台', max_length=20, choices=PLATFORMS)
    ad_type = models.CharField('推广类型', max_length=15, choices=AD_TYPES)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    session = models.ForeignKey(LiveSession, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联直播')

    budget = models.DecimalField('投放预算', max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField('实际花费', max_digits=12, decimal_places=2, default=0)
    impressions = models.IntegerField('曝光量', default=0)
    clicks = models.IntegerField('点击量', default=0)
    conversions = models.IntegerField('转化数', default=0)
    revenue = models.DecimalField('带来GMV', max_digits=12, decimal_places=2, default=0)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='draft')
    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    operator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='投放负责人')

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '流量投放'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"


# ============== 4. 短视频管理 ==============

class ShortVideo(models.Model):
    """短视频内容管理"""
    STATUS = [('draft', '草稿'), ('review', '审核中'), ('approved', '已通过'),
              ('published', '已发布'), ('rejected', '已驳回')]
    PLATFORMS = [('douyin', '抖音'), ('kuaishou', '快手'), ('xiaohongshu', '小红书'),
                 ('bilibili', 'B站'), ('video_account', '视频号')]

    title = models.CharField('视频标题', max_length=200)
    platform = models.CharField('发布平台', max_length=20, choices=PLATFORMS, default='douyin')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联店铺')
    anchor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='short_videos', verbose_name='出镜主播')

    cover_url = models.URLField('封面图', blank=True)
    video_url = models.URLField('视频链接', blank=True)
    duration = models.IntegerField('时长(秒)', default=0)
    script = models.TextField('视频脚本', blank=True)
    tags = models.CharField('标签', max_length=200, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='挂车商品')

    status = models.CharField('状态', max_length=15, choices=STATUS, default='draft')
    creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                 related_name='created_videos', verbose_name='制作人')
    publish_time = models.DateTimeField('发布时间', null=True, blank=True)

    views = models.IntegerField('播放量', default=0)
    likes = models.IntegerField('点赞数', default=0)
    comments = models.IntegerField('评论数', default=0)
    shares = models.IntegerField('转发数', default=0)
    product_clicks = models.IntegerField('商品点击', default=0)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '短视频'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ============== 5. 内容合规审核 ==============

class ComplianceReview(models.Model):
    """内容合规审核"""
    REVIEW_TYPES = [
        ('script', '话术审核'), ('prop', '道具审核'), ('claim', '功效宣称'),
        ('ad_law', '广告法'), ('platform_rule', '平台规则'), ('other', '其他'),
    ]
    STATUS = [('pending', '待审核'), ('approved', '已通过'), ('rejected', '已驳回'), ('revision', '需修改')]
    RISK_LEVELS = [('low', '低风险'), ('medium', '中风险'), ('high', '高风险'), ('forbidden', '禁止')]

    title = models.CharField('审核标题', max_length=200)
    review_type = models.CharField('审核类型', max_length=20, choices=REVIEW_TYPES)
    content = models.TextField('待审核内容')
    related_session = models.ForeignKey(LiveSession, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联直播')
    related_script = models.ForeignKey('StreamScript', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联脚本')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')

    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    risk_level = models.CharField('风险等级', max_length=12, choices=RISK_LEVELS, default='low')
    reviewer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                  related_name='compliance_reviews', verbose_name='审核人')
    review_notes = models.TextField('审核意见', blank=True)
    violations = models.TextField('违规条目', blank=True)
    suggestions = models.TextField('修改建议', blank=True)

    submitted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                      related_name='submitted_reviews', verbose_name='提交人')
    submitted_at = models.DateTimeField('提交时间', null=True, blank=True)
    reviewed_at = models.DateTimeField('审核时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '合规审核'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_review_type_display()}] {self.title}"


# ============== 6. 舆情监控 ==============

class PublicOpinion(models.Model):
    """舆情监控"""
    SOURCES = [('weibo', '微博'), ('douyin', '抖音评论'), ('kuaishou', '快手评论'),
               ('xiaohongshu', '小红书'), ('news', '新闻'), ('forum', '论坛'), ('other', '其他')]
    SENTIMENTS = [('positive', '正面'), ('neutral', '中性'), ('negative', '负面')]
    STATUS = [('new', '新发现'), ('watching', '关注中'), ('escalated', '已升级'), ('resolved', '已处理')]

    title = models.CharField('舆情标题', max_length=200)
    source = models.CharField('来源', max_length=20, choices=SOURCES)
    url = models.URLField('原文链接', blank=True)
    content = models.TextField('内容摘要')
    sentiment = models.CharField('情感倾向', max_length=12, choices=SENTIMENTS, default='neutral')

    related_store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联店铺')
    related_anchor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='opinion_mentions', verbose_name='关联主播')

    status = models.CharField('状态', max_length=15, choices=STATUS, default='new')
    heat = models.IntegerField('热度值', default=0)
    handler = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='handled_opinions', verbose_name='处理人')
    resolution = models.TextField('处理方案', blank=True)

    discovered_at = models.DateTimeField('发现时间', null=True, blank=True)
    resolved_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '舆情监控'
        ordering = ['-heat']

    def __str__(self):
        return f"[{self.get_sentiment_display()}] {self.title}"


# ============== 7. 售后工单 ==============

class AfterSalesOrder(models.Model):
    """售后工单"""
    TYPES = [('return', '退货'), ('exchange', '换货'), ('refund', '仅退款'),
             ('repair', '维修'), ('complaint', '投诉'), ('other', '其他')]
    STATUS = [('submitted', '已提交'), ('reviewing', '审核中'), ('approved', '已同意'),
              ('rejected', '已拒绝'), ('shipping', '退回中'), ('completed', '已完成'), ('closed', '已关闭')]

    order_no = models.CharField('订单号', max_length=50)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    customer_name = models.CharField('客户姓名', max_length=50)
    customer_contact = models.CharField('联系方式', max_length=50, blank=True)
    type = models.CharField('售后类型', max_length=15, choices=TYPES)
    reason = models.TextField('售后原因')
    amount = models.DecimalField('涉及金额', max_digits=12, decimal_places=2, default=0)
    product_name = models.CharField('商品名称', max_length=200, blank=True)
    quantity = models.IntegerField('数量', default=1)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='submitted')
    handler = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='处理人')
    resolution = models.TextField('处理结果', blank=True)
    tracking_no = models.CharField('快递单号', max_length=50, blank=True)
    related_session = models.ForeignKey(LiveSession, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联直播')

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '售后工单'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_no} ({self.get_type_display()})"


# ============== 8. MCN 分成 ==============

class RevenueSharing(models.Model):
    """MCN分成规则与记录"""
    PERIOD_TYPES = [('daily', '日结'), ('weekly', '周结'), ('monthly', '月结')]
    STATUS = [('pending', '待结算'), ('calculating', '计算中'), ('confirmed', '已确认'), ('settled', '已打款')]

    title = models.CharField('结算名称', max_length=200)
    period_type = models.CharField('结算周期', max_length=15, choices=PERIOD_TYPES)
    period_start = models.DateField('周期开始')
    period_end = models.DateField('周期结束')

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name='店铺')
    anchor = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='主播')

    total_revenue = models.DecimalField('总营收', max_digits=14, decimal_places=2, default=0)
    platform_fee = models.DecimalField('平台扣点', max_digits=12, decimal_places=2, default=0)
    mcn_share = models.DecimalField('MCN分成', max_digits=12, decimal_places=2, default=0)
    anchor_share = models.DecimalField('主播分成', max_digits=12, decimal_places=2, default=0)
    mcn_ratio = models.FloatField('MCN比例%', default=50)
    anchor_ratio = models.FloatField('主播比例%', default=50)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='pending')
    settled_at = models.DateTimeField('打款时间', null=True, blank=True)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '分成记录'
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.title} - {self.anchor}"


# ============== 9. 品牌合作项目 ==============

class BrandProject(models.Model):
    """品牌合作项目"""
    STATUS = [('negotiating', '洽谈中'), ('contracted', '已签约'), ('executing', '执行中'),
              ('delivering', '交付中'), ('completed', '已完成'), ('terminated', '已终止')]
    PRIORITY = [('low', '低'), ('medium', '中'), ('high', '高'), ('strategic', '战略级')]

    name = models.CharField('项目名称', max_length=200)
    brand = models.CharField('品牌方', max_length=100)
    contact_person = models.CharField('品牌对接人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='negotiating')
    priority = models.CharField('优先级', max_length=12, choices=PRIORITY, default='medium')
    pm = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name='项目经理')
    stores = models.ManyToManyField(Store, blank=True, verbose_name='参与店铺')
    anchors = models.ManyToManyField(Employee, blank=True, related_name='brand_projects', verbose_name='参与主播')

    total_budget = models.DecimalField('总预算', max_digits=14, decimal_places=2, default=0)
    actual_revenue = models.DecimalField('实际营收', max_digits=14, decimal_places=2, default=0)
    target_gmv = models.DecimalField('目标GMV', max_digits=14, decimal_places=2, default=0)

    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('截止日期', null=True, blank=True)
    requirements = models.TextField('品牌需求', blank=True)
    deliverables = models.TextField('交付要求', blank=True)
    notes = models.TextField('备注', blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '品牌合作'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.brand})"


# ============== 10. 直播间场景 ==============

class StreamScene(models.Model):
    """直播间场景管理"""
    TYPES = [
        ('standard', '标准场景'), ('festival', '节日主题'), ('brand', '品牌定制'),
        ('outdoor', '户外场景'), ('warehouse', '仓库场景'), ('other', '其他'),
    ]
    STATUS = [('active', '使用中'), ('standby', '待用'), ('maintenance', '维护中'), ('archived', '已归档')]

    name = models.CharField('场景名称', max_length=100)
    scene_type = models.CharField('场景类型', max_length=15, choices=TYPES, default='standard')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直播间')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联店铺')

    description = models.TextField('场景描述', blank=True)
    cover_url = models.URLField('场景效果图', blank=True)
    background_color = models.CharField('背景色', max_length=20, blank=True)
    props_list = models.TextField('道具清单', blank=True)
    lighting_plan = models.TextField('灯光方案', blank=True)
    setup_guide = models.TextField('搭建指南', blank=True)

    status = models.CharField('状态', max_length=15, choices=STATUS, default='standby')
    setup_time = models.IntegerField('搭建耗时(分)', default=0)
    cost = models.DecimalField('搭建成本', max_digits=10, decimal_places=2, default=0)
    usage_count = models.IntegerField('使用次数', default=0)
    last_used_at = models.DateTimeField('最后使用', null=True, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '直播场景'
        ordering = ['-usage_count']

    def __str__(self):
        return f"{self.name} ({self.get_scene_type_display()})"
