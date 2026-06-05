from django.db import models
from django.contrib.auth.models import User


# ============== 运营管理类 ==============

class LiveInteraction(models.Model):
    """直播间互动 - 弹幕/评论/点赞记录"""
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE,
                                related_name='interactions', verbose_name='直播场次')
    interaction_type = models.CharField('互动类型', max_length=20,
                                        choices=[('comment', '评论'), ('like', '点赞'),
                                                 ('gift', '送礼'), ('share', '分享'),
                                                 ('follow', '关注'), ('question', '提问')])
    user_id = models.CharField('用户ID', max_length=100)
    user_name = models.CharField('用户昵称', max_length=100, blank=True)
    content = models.TextField('互动内容', blank=True)
    is_anchor = models.BooleanField('是否主播', default=False)
    sentiment = models.CharField('情感倾向', max_length=10,
                                  choices=[('positive', '正面'), ('neutral', '中性'), ('negative', '负面')],
                                  default='neutral')
    timestamp = models.DateTimeField('互动时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '直播间互动'
        verbose_name_plural = verbose_name
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user_name} - {self.interaction_type}'


class Coupon(models.Model):
    """优惠券管理 - 直播专属优惠券"""
    store = models.ForeignKey('Store', on_delete=models.CASCADE,
                               related_name='coupons', verbose_name='所属店铺')
    name = models.CharField('优惠券名称', max_length=100)
    coupon_type = models.CharField('类型', max_length=20,
                                    choices=[('fixed', '满减'), ('percent', '折扣'),
                                             ('free_shipping', '包邮'), ('gift', '赠品')])
    value = models.DecimalField('优惠金额/折扣', max_digits=10, decimal_places=2)
    min_amount = models.DecimalField('最低消费', max_digits=10, decimal_places=2, default=0)
    total_count = models.IntegerField('发放总量', default=100)
    used_count = models.IntegerField('已使用', default=0)
    remain_count = models.IntegerField('剩余数量', default=100)
    start_time = models.DateTimeField('生效时间')
    end_time = models.DateTimeField('失效时间')
    session = models.ForeignKey('LiveSession', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='coupons', verbose_name='关联直播')
    status = models.CharField('状态', max_length=20,
                               choices=[('draft', '草稿'), ('active', '生效中'),
                                        ('paused', '暂停'), ('expired', '已过期')],
                               default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FlashSale(models.Model):
    """秒杀活动 - 限时抢购"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                 related_name='flash_sales', verbose_name='商品')
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE,
                                 related_name='flash_sales', verbose_name='直播场次')
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2)
    sale_price = models.DecimalField('秒杀价', max_digits=10, decimal_places=2)
    total_stock = models.IntegerField('秒杀库存', default=50)
    sold_count = models.IntegerField('已售数量', default=0)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间')
    limit_per_user = models.IntegerField('每人限购', default=1)
    status = models.CharField('状态', max_length=20,
                               choices=[('pending', '待开始'), ('ongoing', '进行中'),
                                        ('ended', '已结束'), ('cancelled', '已取消')],
                               default='pending')
    priority = models.IntegerField('优先级', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '秒杀活动'
        verbose_name_plural = verbose_name
        ordering = ['-priority', '-start_time']

    def __str__(self):
        return f'{self.product.name} - ¥{self.sale_price}'


class RoomDecoration(models.Model):
    """直播间装修 - 背景/贴片/挂件"""
    room = models.ForeignKey('StreamRoom', on_delete=models.CASCADE,
                              related_name='decorations', verbose_name='直播间')
    deco_type = models.CharField('装修类型', max_length=20,
                                  choices=[('background', '背景板'), ('overlay', '贴片'),
                                           ('widget', '挂件'), ('watermark', '水印'),
                                           ('countdown', '倒计时'), ('product_card', '商品卡')])
    name = models.CharField('名称', max_length=100)
    image_url = models.URLField('图片地址')
    position = models.CharField('位置', max_length=20,
                                 choices=[('top_left', '左上'), ('top_right', '右上'),
                                          ('bottom_left', '左下'), ('bottom_right', '右下'),
                                          ('center', '居中'), ('full', '全屏')],
                                 default='center')
    is_active = models.BooleanField('是否启用', default=True)
    start_time = models.DateTimeField('展示开始', null=True, blank=True)
    end_time = models.DateTimeField('展示结束', null=True, blank=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '直播间装修'
        verbose_name_plural = verbose_name
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.room.name} - {self.name}'


class ScriptTag(models.Model):
    """话术标签库 - 话术分类标签与片段"""
    parent = models.ForeignKey('self', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='children', verbose_name='父标签')
    name = models.CharField('标签名', max_length=50)
    color = models.CharField('颜色', max_length=7, default='#00ff88')
    tag_type = models.CharField('标签类型', max_length=20,
                                 choices=[('opening', '开场'), ('product', '产品介绍'),
                                          ('promo', '促销'), ('closing', '收尾'),
                                          ('qa', '问答'), ('story', '故事'), ('other', '其他')])
    content = models.TextField('话术内容', blank=True)
    usage_count = models.IntegerField('使用次数', default=0)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '话术标签'
        verbose_name_plural = verbose_name
        ordering = ['-usage_count']

    def __str__(self):
        return self.name


# ============== 商务拓展类 ==============

class SignContract(models.Model):
    """MCN签约管理 - 主播签约/解约/续约"""
    anchor = models.ForeignKey('Employee', on_delete=models.CASCADE,
                                related_name='sign_contracts', verbose_name='主播')
    contract_type = models.CharField('合同类型', max_length=20,
                                      choices=[('new', '新签'), ('renew', '续签'), ('terminate', '解约')])
    start_date = models.DateField('签约日期')
    end_date = models.DateField('到期日期')
    revenue_share = models.DecimalField('分成比例(%)', max_digits=5, decimal_places=2, default=50)
    base_salary = models.DecimalField('底薪', max_digits=10, decimal_places=2, default=0)
    min_live_hours = models.IntegerField('最低直播时长(h/月)', default=60)
    min_sessions = models.IntegerField('最低直播场次(场/月)', default=20)
    penalty_clause = models.TextField('违约条款', blank=True)
    special_terms = models.TextField('特殊条款', blank=True)
    status = models.CharField('状态', max_length=20,
                               choices=[('pending', '待签署'), ('active', '生效中'),
                                        ('expired', '已到期'), ('terminated', '已解约')],
                               default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, related_name='reviewed_contracts', verbose_name='审核人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'MCN签约'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.anchor.name} - {self.contract_type}'


class BusinessNegotiation(models.Model):
    """商务洽谈 - 合作洽谈记录与跟进"""
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE,
                               related_name='negotiations', verbose_name='品牌方')
    anchor = models.ForeignKey('Employee', on_delete=models.CASCADE,
                                related_name='negotiations', verbose_name='对接主播')
    contact_name = models.CharField('对方联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    cooperation_type = models.CharField('合作类型', max_length=20,
                                         choices=[('live_sale', '直播带货'), ('brand_ambassador', '品牌代言'),
                                                  ('content', '内容合作'), ('event', '活动参与')])
    budget = models.DecimalField('预算', max_digits=12, decimal_places=2, default=0)
    stage = models.CharField('洽谈阶段', max_length=20,
                              choices=[('initial', '初步接触'), ('negotiating', '商务谈判'),
                                       ('proposal', '方案确认'), ('contract', '合同签订'),
                                       ('closed', '已成交'), ('lost', '已流失')],
                              default='initial')
    probability = models.IntegerField('成交概率(%)', default=20)
    note = models.TextField('洽谈记录', blank=True)
    next_follow_up = models.DateTimeField('下次跟进', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商务洽谈'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.brand.name} - {self.anchor.name}'


class Investment(models.Model):
    """招商管理 - 品牌招商/商家入驻"""
    brand_name = models.CharField('品牌/商家名', max_length=100)
    contact = models.CharField('联系人', max_length=50)
    phone = models.CharField('联系电话', max_length=20)
    category = models.CharField('品类', max_length=50)
    source = models.CharField('来源渠道', max_length=20,
                               choices=[('referral', '转介绍'), ('exhibition', '展会'),
                                        ('online', '线上'), ('cold_call', '陌拜'), ('other', '其他')],
                               default='online')
    commission_rate = models.DecimalField('佣金比例(%)', max_digits=5, decimal_places=2, default=20)
    monthly_budget = models.DecimalField('月预算', max_digits=12, decimal_places=2, default=0)
    stage = models.CharField('招商阶段', max_length=20,
                              choices=[('inquiry', '咨询'), ('qualified', '资质审核'),
                                       ('sample', '寄样'), ('trial', '试播'),
                                       ('formal', '正式合作'), ('paused', '暂停合作')],
                              default='inquiry')
    score = models.IntegerField('意向评分', default=50)
    remark = models.TextField('备注', blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, verbose_name='负责人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '招商管理'
        verbose_name_plural = verbose_name
        ordering = ['-score', '-created_at']

    def __str__(self):
        return self.brand_name


class ContractLedger(models.Model):
    """合同台账 - 电子合同归档与到期提醒"""
    name = models.CharField('合同名称', max_length=200)
    contract_no = models.CharField('合同编号', max_length=50, unique=True)
    contract_type = models.CharField('合同类型', max_length=20,
                                      choices=[('brand', '品牌合同'), ('anchor', '主播合同'),
                                               ('supplier', '供应商合同'), ('platform', '平台协议'),
                                               ('service', '服务合同'), ('other', '其他')])
    party_a = models.CharField('甲方', max_length=100)
    party_b = models.CharField('乙方', max_length=100)
    amount = models.DecimalField('合同金额', max_digits=12, decimal_places=2, default=0)
    sign_date = models.DateField('签订日期')
    start_date = models.DateField('生效日期')
    end_date = models.DateField('到期日期')
    file_url = models.URLField('合同文件', blank=True)
    remind_days = models.IntegerField('提前提醒天数', default=30)
    status = models.CharField('状态', max_length=20,
                               choices=[('draft', '草稿'), ('signed', '已签署'),
                                        ('active', '执行中'), ('expired', '已到期'),
                                        ('terminated', '已终止')],
                               default='draft')
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '合同台账'
        verbose_name_plural = verbose_name
        ordering = ['-end_date']

    def __str__(self):
        return f'{self.contract_no} - {self.name}'


class Authorization(models.Model):
    """授权管理 - 品牌授权/肖像权/版权"""
    auth_type = models.CharField('授权类型', max_length=20,
                                  choices=[('brand', '品牌授权'), ('portrait', '肖像权'),
                                           ('copyright', '版权'), ('music', '音乐版权'),
                                           ('image', '图片版权'), ('video', '视频版权')])
    name = models.CharField('授权名称', max_length=200)
    licensor = models.CharField('授权方', max_length=100)
    licensee = models.CharField('被授权方', max_length=100)
    scope = models.TextField('授权范围', blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='authorizations', verbose_name='关联品牌')
    anchor = models.ForeignKey('Employee', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='authorizations', verbose_name='关联主播')
    start_date = models.DateField('授权开始')
    end_date = models.DateField('授权结束')
    file_url = models.URLField('授权文件', blank=True)
    status = models.CharField('状态', max_length=20,
                               choices=[('pending', '待生效'), ('active', '生效中'),
                                        ('expired', '已过期'), ('revoked', '已撤销')],
                               default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '授权管理'
        verbose_name_plural = verbose_name
        ordering = ['-end_date']

    def __str__(self):
        return self.name


# ============== 数据与策略类 ==============

class CompetitorRoom(models.Model):
    """竞品直播间 - 数据采集与对比"""
    platform = models.CharField('平台', max_length=20,
                                 choices=[('douyin', '抖音'), ('kuaishou', '快手'),
                                          ('taobao', '淘宝'), ('xiaohongshu', '小红书')])
    room_id = models.CharField('直播间ID', max_length=50)
    anchor_name = models.CharField('主播名', max_length=100)
    follower_count = models.IntegerField('粉丝数', default=0)
    avg_viewers = models.IntegerField('场均观看', default=0)
    avg_gmv = models.DecimalField('场均GMV', max_digits=12, decimal_places=2, default=0)
    peak_viewers = models.IntegerField('最高在线', default=0)
    live_frequency = models.IntegerField('月直播频次', default=0)
    top_product = models.CharField('爆款商品', max_length=200, blank=True)
    strategy = models.TextField('运营策略分析', blank=True)
    last_tracked = models.DateTimeField('最后采集时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '竞品直播间'
        verbose_name_plural = verbose_name
        ordering = ['-avg_gmv']

    def __str__(self):
        return f'{self.anchor_name} ({self.platform})'


class TrafficAnalysis(models.Model):
    """流量分析 - 自然/付费流量来源分析"""
    session = models.ForeignKey('LiveSession', on_delete=models.CASCADE,
                                 related_name='traffic_records', verbose_name='直播场次')
    traffic_type = models.CharField('流量类型', max_length=20,
                                     choices=[('natural', '自然流量'), ('paid', '付费流量'),
                                              ('private', '私域流量'), ('recommend', '推荐流量')])
    source = models.CharField('来源', max_length=50,
                               choices=[('homepage', '首页推荐'), ('search', '搜索'),
                                        ('live_tab', '直播广场'), ('follow', '关注'),
                                        ('dou_plus', 'DOU+'), ('qianchuan', '千川'),
                                        ('private', '私域'), ('share', '分享')])
    impressions = models.IntegerField('曝光量', default=0)
    clicks = models.IntegerField('点击量', default=0)
    ctr = models.DecimalField('点击率(%)', max_digits=5, decimal_places=2, default=0)
    cost = models.DecimalField('花费', max_digits=10, decimal_places=2, default=0)
    conversions = models.IntegerField('转化数', default=0)
    cvr = models.DecimalField('转化率(%)', max_digits=5, decimal_places=2, default=0)
    recorded_at = models.DateTimeField('记录时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '流量分析'
        verbose_name_plural = verbose_name
        ordering = ['-recorded_at']

    def __str__(self):
        return f'{self.session} - {self.traffic_type}'


class UserPersona(models.Model):
    """用户画像 - 观众/买家标签管理"""
    user_id = models.CharField('用户ID', max_length=100)
    platform = models.CharField('平台', max_length=20,
                                 choices=[('douyin', '抖音'), ('kuaishou', '快手'),
                                          ('taobao', '淘宝'), ('xiaohongshu', '小红书')])
    nickname = models.CharField('昵称', max_length=100, blank=True)
    gender = models.CharField('性别', max_length=10,
                               choices=[('male', '男'), ('female', '女'), ('unknown', '未知')],
                               default='unknown')
    age_range = models.CharField('年龄段', max_length=20, blank=True)
    city = models.CharField('城市', max_length=50, blank=True)
    tags = models.TextField('标签(JSON)', blank=True)
    total_spent = models.DecimalField('累计消费', max_digits=12, decimal_places=2, default=0)
    order_count = models.IntegerField('订单数', default=0)
    last_active = models.DateTimeField('最后活跃', null=True, blank=True)
    fan_level = models.CharField('粉丝等级', max_length=20,
                                  choices=[('new', '新粉'), ('regular', '常看'),
                                           ('loyal', '铁粉'), ('vip', 'VIP')],
                                  default='new')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户画像'
        verbose_name_plural = verbose_name
        ordering = ['-total_spent']

    def __str__(self):
        return f'{self.nickname or self.user_id}'


class ABTest(models.Model):
    """AB测试 - 直播间策略实验"""
    name = models.CharField('实验名称', max_length=100)
    test_type = models.CharField('实验类型', max_length=20,
                                  choices=[('script', '话术'), ('scene', '场景'),
                                           ('product', '商品排序'), ('price', '定价策略'),
                                           ('time', '直播时段'), ('title', '标题')])
    hypothesis = models.TextField('假设', blank=True)
    control_plan = models.TextField('对照组方案', blank=True)
    test_plan = models.TextField('实验组方案', blank=True)
    control_sessions = models.CharField('对照组场次IDs', max_length=500, blank=True)
    test_sessions = models.CharField('实验组场次IDs', max_length=500, blank=True)
    control_gmv = models.DecimalField('对照组GMV', max_digits=12, decimal_places=2, default=0)
    test_gmv = models.DecimalField('实验组GMV', max_digits=12, decimal_places=2, default=0)
    control_metric = models.DecimalField('对照组关键指标', max_digits=10, decimal_places=2, default=0)
    test_metric = models.DecimalField('实验组关键指标', max_digits=10, decimal_places=2, default=0)
    confidence = models.DecimalField('置信度(%)', max_digits=5, decimal_places=2, default=0)
    winner = models.CharField('胜出方案', max_length=10,
                               choices=[('control', '对照组'), ('test', '实验组'), ('tie', '持平')],
                               blank=True)
    status = models.CharField('状态', max_length=20,
                               choices=[('draft', '草稿'), ('running', '进行中'),
                                        ('completed', '已完成'), ('cancelled', '已取消')],
                               default='draft')
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'AB测试'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class DataWarning(models.Model):
    """数据预警 - 关键指标预警规则与触发"""
    name = models.CharField('预警名称', max_length=100)
    metric = models.CharField('监控指标', max_length=50,
                               choices=[('gmv', 'GMV'), ('viewers', '在线人数'),
                                        ('conversion_rate', '转化率'), ('refund_rate', '退款率'),
                                        ('complaint_rate', '投诉率'), ('follower_change', '粉丝变化')])
    condition = models.CharField('条件', max_length=20,
                                  choices=[('gt', '大于'), ('lt', '小于'), ('eq', '等于'),
                                           ('drop', '下跌超过'), ('rise', '上涨超过')])
    threshold = models.DecimalField('阈值', max_digits=12, decimal_places=2)
    time_window = models.CharField('时间窗口', max_length=20,
                                    choices=[('realtime', '实时'), ('hourly', '每小时'),
                                             ('daily', '每日'), ('weekly', '每周')],
                                    default='daily')
    severity = models.CharField('严重程度', max_length=10,
                                 choices=[('info', '提示'), ('warning', '警告'), ('critical', '严重')],
                                 default='warning')
    notify_method = models.CharField('通知方式', max_length=20,
                                      choices=[('sms', '短信'), ('wechat', '微信'),
                                               ('email', '邮件'), ('system', '系统通知')],
                                      default='system')
    notify_users = models.TextField('通知人IDs', blank=True)
    is_active = models.BooleanField('启用', default=True)
    trigger_count = models.IntegerField('触发次数', default=0)
    last_triggered = models.DateTimeField('最后触发', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '数据预警'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ============== 财务与供应链类 ==============

class Settlement(models.Model):
    """结算单 - MCN与主播/平台结算"""
    settlement_type = models.CharField('结算类型', max_length=20,
                                        choices=[('anchor', '主播结算'), ('platform', '平台结算'),
                                                 ('brand', '品牌结算'), ('supplier', '供应商结算')])
    period_start = models.DateField('结算周期开始')
    period_end = models.DateField('结算周期结束')
    anchor = models.ForeignKey('Employee', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='settlements', verbose_name='主播')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='settlements', verbose_name='品牌')
    store = models.ForeignKey('Store', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='settlements', verbose_name='店铺')
    total_gmv = models.DecimalField('总GMV', max_digits=12, decimal_places=2, default=0)
    total_orders = models.IntegerField('总订单数', default=0)
    refund_amount = models.DecimalField('退款金额', max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField('佣金收入', max_digits=12, decimal_places=2, default=0)
    share_amount = models.DecimalField('分成金额', max_digits=12, decimal_places=2, default=0)
    deduction = models.DecimalField('扣款', max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField('实结金额', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20,
                               choices=[('draft', '草稿'), ('confirmed', '已确认'),
                                        ('approved', '已审批'), ('paid', '已打款'),
                                        ('disputed', '有争议')],
                               default='draft')
    remark = models.TextField('备注', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '结算单'
        verbose_name_plural = verbose_name
        ordering = ['-period_end']

    def __str__(self):
        return f'{self.settlement_type} {self.period_start}~{self.period_end}'


class Logistics(models.Model):
    """物流跟踪 - 发货/退货物流"""
    order_no = models.CharField('订单号', max_length=100)
    product_name = models.CharField('商品名称', max_length=200)
    quantity = models.IntegerField('数量', default=1)
    logistics_type = models.CharField('物流类型', max_length=20,
                                       choices=[('delivery', '发货'), ('return', '退货'),
                                                ('exchange', '换货')])
    carrier = models.CharField('物流公司', max_length=50)
    tracking_no = models.CharField('物流单号', max_length=100)
    sender_address = models.TextField('发件地址', blank=True)
    receiver_address = models.TextField('收件地址', blank=True)
    status = models.CharField('物流状态', max_length=20,
                               choices=[('pending', '待发货'), ('shipped', '已发货'),
                                        ('in_transit', '运输中'), ('delivered', '已签收'),
                                        ('returned', '已退回'), ('lost', '丢失')],
                               default='pending')
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('签收时间', null=True, blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '物流跟踪'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.tracking_no}'


class Inventory(models.Model):
    """库存管理 - 多仓库存"""
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                 related_name='inventories', verbose_name='商品')
    warehouse = models.CharField('仓库名称', max_length=100)
    sku = models.CharField('SKU', max_length=100, blank=True)
    quantity = models.IntegerField('库存数量', default=0)
    safety_stock = models.IntegerField('安全库存', default=10)
    locked_quantity = models.IntegerField('锁定数量', default=0)
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='inventories', verbose_name='供应商')
    location = models.CharField('库位', max_length=50, blank=True)
    last_restock = models.DateTimeField('最后补货', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '库存管理'
        verbose_name_plural = verbose_name
        ordering = ['warehouse']
        unique_together = ['product', 'warehouse', 'sku']

    def __str__(self):
        return f'{self.product.name} @ {self.warehouse}'


class ReturnAnalysis(models.Model):
    """退货分析 - 退货原因与改进"""
    order_no = models.CharField('订单号', max_length=100)
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                 related_name='returns', verbose_name='商品')
    anchor = models.ForeignKey('Employee', on_delete=models.SET_NULL,
                                null=True, related_name='returns', verbose_name='主播')
    session = models.ForeignKey('LiveSession', on_delete=models.SET_NULL,
                                 null=True, related_name='returns', verbose_name='直播场次')
    reason = models.CharField('退货原因', max_length=20,
                               choices=[('quality', '质量问题'), ('description', '描述不符'),
                                        ('wrong', '发错货'), ('damage', '物流损坏'),
                                        ('size', '尺寸不合'), ('change_mind', '不想要了'),
                                        ('other', '其他')])
    detail = models.TextField('详细说明', blank=True)
    amount = models.DecimalField('退货金额', max_digits=10, decimal_places=2)
    status = models.CharField('处理状态', max_length=20,
                               choices=[('pending', '待处理'), ('approved', '已同意'),
                                        ('rejected', '已拒绝'), ('refunded', '已退款'),
                                        ('resolved', '已解决')],
                               default='pending')
    improvement = models.TextField('改进措施', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '退货分析'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.reason}'


class TaxRecord(models.Model):
    """税务管理 - 发票/纳税/合规"""
    tax_type = models.CharField('税务类型', max_length=20,
                                 choices=[('invoice_out', '销项发票'), ('invoice_in', '进项发票'),
                                          ('vat', '增值税'), ('income_tax', '企业所得税'),
                                          ('individual_tax', '个人所得税'), ('stamp_tax', '印花税')])
    invoice_no = models.CharField('发票号', max_length=50, blank=True)
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField('税额', max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField('税率(%)', max_digits=5, decimal_places=2, default=6)
    counterparty = models.CharField('对方名称', max_length=200)
    invoice_date = models.DateField('开票日期', null=True, blank=True)
    period = models.CharField('所属期间', max_length=7)
    file_url = models.URLField('附件', blank=True)
    status = models.CharField('状态', max_length=20,
                               choices=[('pending', '待处理'), ('issued', '已开具'),
                                        ('received', '已收到'), ('filed', '已申报'),
                                        ('paid', '已缴纳')],
                               default='pending')
    remark = models.TextField('备注', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '税务管理'
        verbose_name_plural = verbose_name
        ordering = ['-invoice_date']

    def __str__(self):
        return f'{self.tax_type} - {self.invoice_no or self.counterparty}'
