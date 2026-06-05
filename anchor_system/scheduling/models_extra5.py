from django.db import models
from django.contrib.auth.models import User


# ============== 直播运营类 ==============

class StreamChecklist(models.Model):
    name = models.CharField('清单名称', max_length=100)
    stream_plan = models.ForeignKey('StreamPlan', on_delete=models.CASCADE, null=True, blank=True, related_name='checklists', verbose_name='直播计划')
    items = models.JSONField('检查项', default=list)
    completed_items = models.JSONField('已完成项', default=list)
    status = models.CharField('状态', max_length=20, choices=[('pending', '待检查'), ('in_progress', '检查中'), ('done', '已完成')], default='pending')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='完成人')
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播检查清单'
        ordering = ['-id']

    def __str__(self):
        return self.name


class StreamReplay(models.Model):
    title = models.CharField('回放标题', max_length=200)
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE, null=True, blank=True, related_name='replays', verbose_name='直播场次')
    url = models.URLField('回放地址', blank=True)
    duration = models.IntegerField('时长(秒)', default=0)
    views = models.IntegerField('观看次数', default=0)
    highlights = models.JSONField('精彩片段', default=list, blank=True)
    status = models.CharField('状态', max_length=20, choices=[('processing', '处理中'), ('ready', '已就绪'), ('published', '已发布'), ('archived', '已归档')], default='processing')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播回放'
        ordering = ['-id']

    def __str__(self):
        return self.title


class StreamBackup(models.Model):
    name = models.CharField('方案名称', max_length=100)
    stream_plan = models.ForeignKey('StreamPlan', on_delete=models.CASCADE, null=True, blank=True, related_name='backups', verbose_name='直播计划')
    backup_type = models.CharField('备用类型', max_length=20, choices=[('anchor', '备选主播'), ('device', '备用设备'), ('network', '备用网络'), ('content', '备用内容')], default='anchor')
    backup_url = models.URLField('备用链接', blank=True)
    contact = models.CharField('联系人', max_length=100, blank=True)
    notes = models.TextField('备注', blank=True)
    status = models.CharField('状态', max_length=20, choices=[('standby', '待命'), ('activated', '已启用'), ('resolved', '已解决')], default='standby')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播备用方案'
        ordering = ['-id']

    def __str__(self):
        return self.name


class StreamQuality(models.Model):
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE, null=True, blank=True, related_name='quality_records', verbose_name='直播场次')
    resolution = models.CharField('分辨率', max_length=20, default='1080p')
    bitrate = models.IntegerField('码率(kbps)', default=4000)
    fps = models.FloatField('帧率', default=30.0)
    dropped_frames = models.IntegerField('丢帧数', default=0)
    audio_level = models.FloatField('音频电平', default=-12.0)
    latency = models.IntegerField('延迟(ms)', default=200)
    score = models.FloatField('质量评分', default=0)
    issues = models.JSONField('问题记录', default=list, blank=True)
    recorded_at = models.DateTimeField('记录时间', auto_now_add=True)

    class Meta:
        verbose_name = '直播质量'
        ordering = ['-recorded_at']

    def __str__(self):
        return f'Quality-{self.id}'


class LiveTimeline(models.Model):
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE, null=True, blank=True, related_name='timeline_events', verbose_name='直播场次')
    event_type = models.CharField('事件类型', max_length=20, choices=[('start', '开播'), ('product', '上品'), ('coupon', '发券'), ('game', '互动'), ('peak', '高峰'), ('end', '下播'), ('other', '其他')], default='other')
    title = models.CharField('事件标题', max_length=200)
    description = models.TextField('描述', blank=True)
    offset_seconds = models.IntegerField('时间偏移(秒)', default=0)
    product_name = models.CharField('关联商品', max_length=200, blank=True)
    gmv_at_point = models.DecimalField('时点GMV', max_digits=12, decimal_places=2, default=0)
    viewers_at_point = models.IntegerField('时点观众', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播时间轴'
        ordering = ['offset_seconds']

    def __str__(self):
        return self.title


class ProductLink(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, related_name='links', verbose_name='商品')
    platform = models.CharField('平台', max_length=50)
    url = models.URLField('链接地址')
    short_url = models.URLField('短链接', blank=True)
    click_count = models.IntegerField('点击次数', default=0)
    conversion_count = models.IntegerField('转化次数', default=0)
    conversion_rate = models.FloatField('转化率', default=0)
    status = models.CharField('状态', max_length=20, choices=[('active', '正常'), ('expired', '已失效'), ('disabled', '已禁用')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '商品链接'
        ordering = ['-id']

    def __str__(self):
        return f'{self.platform} - {self.url[:50]}'


class StreamTemplate(models.Model):
    name = models.CharField('模板名称', max_length=100)
    category = models.CharField('分类', max_length=50, choices=[('standard', '标准'), ('festival', '节日'), ('brand', '品牌'), ('clearance', '清仓'), ('new_product', '新品')], default='standard')
    duration_minutes = models.IntegerField('预计时长(分)', default=120)
    segments = models.JSONField('流程段落', default=list)
    notes = models.TextField('备注', blank=True)
    usage_count = models.IntegerField('使用次数', default=0)
    is_public = models.BooleanField('是否公开', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播模板'
        ordering = ['-id']

    def __str__(self):
        return self.name


class StreamOverlay(models.Model):
    name = models.CharField('名称', max_length=100)
    overlay_type = models.CharField('类型', max_length=20, choices=[('countdown', '倒计时'), ('banner', '横幅'), ('product_card', '商品卡'), ('poll', '投票'), ('lottery', '抽奖'), ('qr_code', '二维码')], default='banner')
    config = models.JSONField('配置', default=dict)
    preview_url = models.URLField('预览图', blank=True)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播叠加层'
        ordering = ['-id']

    def __str__(self):
        return self.name


# ============== 电商销售类 ==============

class Order(models.Model):
    order_no = models.CharField('订单号', max_length=50, unique=True)
    product_name = models.CharField('商品名称', max_length=200)
    product_id = models.IntegerField('商品ID', null=True, blank=True)
    store_id = models.IntegerField('店铺ID', null=True, blank=True)
    customer_name = models.CharField('客户名称', max_length=100, blank=True)
    quantity = models.IntegerField('数量', default=1)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=[('pending', '待付款'), ('paid', '已付款'), ('shipped', '已发货'), ('completed', '已完成'), ('cancelled', '已取消'), ('refunded', '已退款')], default='pending')
    source = models.CharField('来源', max_length=20, choices=[('live', '直播'), ('video', '短视频'), ('shop', '店铺')], default='live')
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '订单管理'
        ordering = ['-id']

    def __str__(self):
        return self.order_no


class Refund(models.Model):
    order_no = models.CharField('关联订单号', max_length=50)
    product_name = models.CharField('商品名称', max_length=200, blank=True)
    reason = models.CharField('退款原因', max_length=200)
    amount = models.DecimalField('退款金额', max_digits=12, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=[('pending', '待处理'), ('approved', '已批准'), ('rejected', '已拒绝'), ('completed', '已完成')], default='pending')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='处理人')
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '退款管理'
        ordering = ['-id']

    def __str__(self):
        return f'Refund-{self.order_no}'


class PriceMonitor(models.Model):
    product_name = models.CharField('商品名称', max_length=200)
    platform = models.CharField('平台', max_length=50)
    current_price = models.DecimalField('当前价格', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2)
    lowest_price = models.DecimalField('历史最低', max_digits=10, decimal_places=2)
    competitor_price = models.DecimalField('竞品价格', max_digits=10, decimal_places=2, null=True, blank=True)
    price_change = models.FloatField('价格变动%', default=0)
    alert_triggered = models.BooleanField('已触发预警', default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '价格监控'
        ordering = ['-id']

    def __str__(self):
        return f'{self.product_name} - {self.platform}'


class CommissionConfig(models.Model):
    name = models.CharField('配置名称', max_length=100)
    category = models.CharField('商品分类', max_length=50, blank=True)
    rate = models.FloatField('佣金比例%', default=10)
    min_amount = models.DecimalField('最低金额', max_digits=10, decimal_places=2, default=0)
    max_amount = models.DecimalField('最高金额', max_digits=12, decimal_places=2, null=True, blank=True)
    anchor_rate = models.FloatField('主播分成%', default=50)
    platform_rate = models.FloatField('平台分成%', default=30)
    is_active = models.BooleanField('启用', default=True)
    effective_date = models.DateField('生效日期', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '佣金配置'
        ordering = ['-id']

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    name = models.CharField('标签名称', max_length=100)
    color = models.CharField('标签颜色', max_length=20, default='#7c5cff')
    icon = models.CharField('图标', max_length=50, blank=True)
    product_count = models.IntegerField('商品数量', default=0)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '商品标签'
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product_name = models.CharField('商品名称', max_length=200)
    product_id = models.IntegerField('商品ID', null=True, blank=True)
    rating = models.IntegerField('评分', default=5)
    content = models.TextField('评价内容', blank=True)
    reviewer = models.CharField('评价人', max_length=100, blank=True)
    source = models.CharField('来源平台', max_length=50, blank=True)
    sentiment = models.CharField('情感', max_length=10, choices=[('positive', '好评'), ('neutral', '中评'), ('negative', '差评')], default='positive')
    is_replied = models.BooleanField('已回复', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '商品评价'
        ordering = ['-id']

    def __str__(self):
        return f'{self.product_name} - {self.rating}星'


class SalesTarget(models.Model):
    name = models.CharField('目标名称', max_length=100)
    target_type = models.CharField('目标类型', max_length=20, choices=[('anchor', '主播'), ('store', '店铺'), ('team', '团队'), ('category', '品类')], default='anchor')
    target_id = models.IntegerField('目标ID', null=True, blank=True)
    period = models.CharField('周期', max_length=20)
    target_amount = models.DecimalField('目标金额', max_digits=12, decimal_places=2)
    actual_amount = models.DecimalField('实际金额', max_digits=12, decimal_places=2, default=0)
    completion_rate = models.FloatField('完成率%', default=0)
    status = models.CharField('状态', max_length=20, choices=[('active', '进行中'), ('completed', '已完成'), ('failed', '未完成')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '销售目标'
        ordering = ['-id']

    def __str__(self):
        return self.name


class PromoCode(models.Model):
    code = models.CharField('推广码', max_length=50, unique=True)
    discount_type = models.CharField('优惠类型', max_length=20, choices=[('fixed', '固定金额'), ('percent', '百分比')], default='fixed')
    discount_value = models.DecimalField('优惠值', max_digits=10, decimal_places=2)
    min_order = models.DecimalField('最低订单额', max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField('最大使用次数', default=100)
    used_count = models.IntegerField('已使用', default=0)
    anchor_id = models.IntegerField('关联主播ID', null=True, blank=True)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '推广码'
        ordering = ['-id']

    def __str__(self):
        return self.code


# ============== 营销推广类 ==============

class ContentCalendar(models.Model):
    title = models.CharField('内容标题', max_length=200)
    content_type = models.CharField('内容类型', max_length=20, choices=[('live', '直播'), ('video', '短视频'), ('article', '图文'), ('story', '故事')], default='live')
    platform = models.CharField('发布平台', max_length=50, default='抖音')
    publish_date = models.DateField('发布日期')
    publish_time = models.TimeField('发布时间', null=True, blank=True)
    assignee = models.CharField('负责人', max_length=100, blank=True)
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('scheduled', '已排期'), ('published', '已发布'), ('cancelled', '已取消')], default='draft')
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '内容日历'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title


class InfluencerCollab(models.Model):
    influencer_name = models.CharField('达人名称', max_length=100)
    platform = models.CharField('平台', max_length=50)
    followers = models.IntegerField('粉丝数', default=0)
    collab_type = models.CharField('合作类型', max_length=20, choices=[('commission', '佣金'), ('fixed_fee', '固定费用'), ('revenue_share', '分成')], default='commission')
    fee = models.DecimalField('费用', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=[('negotiating', '洽谈中'), ('confirmed', '已确认'), ('live', '进行中'), ('completed', '已完成'), ('cancelled', '已取消')], default='negotiating')
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    expected_gmv = models.DecimalField('预期GMV', max_digits=12, decimal_places=2, default=0)
    actual_gmv = models.DecimalField('实际GMV', max_digits=12, decimal_places=2, default=0)
    notes = models.TextField('备注', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '达人合作'
        ordering = ['-id']

    def __str__(self):
        return self.influencer_name


class SocialMedia(models.Model):
    platform = models.CharField('平台', max_length=50)
    account_name = models.CharField('账号名称', max_length=100)
    account_id = models.CharField('账号ID', max_length=100, blank=True)
    followers = models.IntegerField('粉丝数', default=0)
    following = models.IntegerField('关注数', default=0)
    posts_count = models.IntegerField('帖子数', default=0)
    avg_likes = models.IntegerField('平均点赞', default=0)
    avg_comments = models.IntegerField('平均评论', default=0)
    engagement_rate = models.FloatField('互动率%', default=0)
    last_sync = models.DateTimeField('最后同步', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '社媒管理'
        ordering = ['-id']

    def __str__(self):
        return f'{self.platform} - {self.account_name}'


class EmailCampaign(models.Model):
    name = models.CharField('活动名称', max_length=200)
    subject = models.CharField('邮件主题', max_length=300)
    content = models.TextField('邮件内容', blank=True)
    recipients_count = models.IntegerField('收件人数', default=0)
    open_count = models.IntegerField('打开数', default=0)
    click_count = models.IntegerField('点击数', default=0)
    open_rate = models.FloatField('打开率%', default=0)
    click_rate = models.FloatField('点击率%', default=0)
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('scheduled', '已排期'), ('sending', '发送中'), ('sent', '已发送')], default='draft')
    scheduled_at = models.DateTimeField('发送时间', null=True, blank=True)
    sent_at = models.DateTimeField('发送完成', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '邮件营销'
        ordering = ['-id']

    def __str__(self):
        return self.name


class ReferralProgram(models.Model):
    name = models.CharField('活动名称', max_length=100)
    referrer_reward = models.DecimalField('推荐人奖励', max_digits=10, decimal_places=2)
    referee_reward = models.DecimalField('被推荐人奖励', max_digits=10, decimal_places=2)
    total_referrals = models.IntegerField('总推荐数', default=0)
    total_conversions = models.IntegerField('总转化数', default=0)
    conversion_rate = models.FloatField('转化率%', default=0)
    budget = models.DecimalField('预算', max_digits=12, decimal_places=2, default=0)
    spent = models.DecimalField('已花费', max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField('启用', default=True)
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '推荐计划'
        ordering = ['-id']

    def __str__(self):
        return self.name


class LoyaltyProgram(models.Model):
    name = models.CharField('计划名称', max_length=100)
    points_per_yuan = models.FloatField('每元积分', default=1)
    min_points = models.IntegerField('最低积分', default=100)
    reward_type = models.CharField('奖励类型', max_length=20, choices=[('discount', '折扣'), ('gift', '赠品'), ('cashback', '返现')], default='discount')
    reward_value = models.DecimalField('奖励价值', max_digits=10, decimal_places=2, default=0)
    total_members = models.IntegerField('总会员数', default=0)
    active_members = models.IntegerField('活跃会员', default=0)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '会员积分'
        ordering = ['-id']

    def __str__(self):
        return self.name


class EventManagement(models.Model):
    name = models.CharField('活动名称', max_length=200)
    event_type = models.CharField('活动类型', max_length=20, choices=[('live', '直播活动'), ('offline', '线下活动'), ('online', '线上活动'), ('brand', '品牌活动')], default='live')
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    location = models.CharField('地点', max_length=200, blank=True)
    budget = models.DecimalField('预算', max_digits=12, decimal_places=2, default=0)
    actual_cost = models.DecimalField('实际费用', max_digits=12, decimal_places=2, default=0)
    participants = models.IntegerField('参与人数', default=0)
    status = models.CharField('状态', max_length=20, choices=[('planning', '策划中'), ('active', '进行中'), ('completed', '已完成')], default='planning')
    description = models.TextField('描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '活动管理'
        ordering = ['-id']

    def __str__(self):
        return self.name


class SEOOptimization(models.Model):
    page_url = models.URLField('页面地址')
    title = models.CharField('页面标题', max_length=200, blank=True)
    keywords = models.CharField('关键词', max_length=500, blank=True)
    description = models.TextField('页面描述', blank=True)
    score = models.IntegerField('SEO评分', default=0)
    issues = models.JSONField('问题列表', default=list, blank=True)
    suggestions = models.JSONField('优化建议', default=list, blank=True)
    page_speed = models.IntegerField('页面速度', default=0)
    mobile_score = models.IntegerField('移动评分', default=0)
    last_audit = models.DateTimeField('最后审计', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'SEO优化'
        ordering = ['-id']

    def __str__(self):
        return self.page_url


class LivePoll(models.Model):
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE, null=True, blank=True, related_name='polls', verbose_name='直播场次')
    question = models.CharField('投票问题', max_length=300)
    options = models.JSONField('选项')
    votes = models.JSONField('投票结果', default=dict)
    total_votes = models.IntegerField('总票数', default=0)
    status = models.CharField('状态', max_length=20, choices=[('draft', '草稿'), ('active', '进行中'), ('closed', '已结束')], default='draft')
    duration_seconds = models.IntegerField('持续时间(秒)', default=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播投票'
        ordering = ['-id']

    def __str__(self):
        return self.question
