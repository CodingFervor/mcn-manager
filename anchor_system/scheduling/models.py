from django.db import models
from django.contrib.auth.models import User


# ============== 组织架构 ==============

class Brand(models.Model):
    """合作品牌方"""
    name = models.CharField('品牌名', max_length=100, unique=True)
    industry = models.CharField('行业', max_length=50, blank=True)
    contact = models.CharField('联系人', max_length=50, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    logo = models.URLField('Logo', blank=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '品牌方'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Store(models.Model):
    """店铺（一个主播可对应多个店铺）"""
    PLATFORM_CHOICES = [
        ('douyin', '抖音'),
        ('kuaishou', '快手'),
        ('taobao', '淘宝'),
        ('xiaohongshu', '小红书'),
        ('pdd', '拼多多'),
        ('jd', '京东'),
        ('video_account', '视频号'),
    ]
    STATUS_CHOICES = [
        ('active', '运营中'),
        ('paused', '已暂停'),
        ('closed', '已关停'),
    ]

    name = models.CharField('店铺名', max_length=100)
    platform = models.CharField('平台', max_length=20, choices=PLATFORM_CHOICES, default='douyin')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='stores', verbose_name='品牌方')
    store_url = models.URLField('店铺链接', blank=True)
    category = models.CharField('类目', max_length=50, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    monthly_target = models.DecimalField('月度GMV目标(万)', max_digits=12, decimal_places=2, default=0)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = verbose_name
        ordering = ['name']
        indexes = [
            models.Index(fields=['platform']),
            models.Index(fields=['status']),
            models.Index(fields=['brand']),
        ]

    def __str__(self):
        return f'[{self.get_platform_display()}] {self.name}'


class Team(models.Model):
    """运营小组"""
    name = models.CharField('小组名', max_length=50, unique=True)
    leader = models.CharField('组长', max_length=50, blank=True)
    description = models.CharField('职责描述', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '运营小组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class StreamRoom(models.Model):
    """直播间（一个店铺可能多直播间）"""
    name = models.CharField('直播间名称', max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='rooms', verbose_name='所属店铺')
    room_id = models.CharField('平台房间号', max_length=50, blank=True)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播间'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.store.name}-{self.name}'


# ============== 人员 ==============

class Employee(models.Model):
    """员工（统一管理主播/运营/管理员）"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('manager', '运营经理'),
        ('operator', '运营/中控'),
        ('anchor', '主播'),
        ('assistant', '助理'),
    ]
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee', verbose_name='登录账号')
    name = models.CharField('姓名', max_length=50)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='anchor')
    phone = models.CharField('联系电话', max_length=20, blank=True)
    wechat = models.CharField('微信号', max_length=50, blank=True)
    avatar = models.URLField('头像', blank=True)
    id_card = models.CharField('身份证号', max_length=20, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name='所属小组')
    stores = models.ManyToManyField(Store, blank=True, related_name='employees', verbose_name='负责店铺')
    join_date = models.DateField('入职日期', null=True, blank=True)
    base_salary = models.DecimalField('底薪', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('在职', default=True)
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '员工'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['team']),
        ]

    def __str__(self):
        return f'{self.name}({self.get_role_display()})'


class AnchorProfile(models.Model):
    """主播档案（主播特有信息）"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='anchor_profile', verbose_name='员工')
    nickname = models.CharField('直播昵称', max_length=50)
    level = models.CharField('主播等级', max_length=20, default='普通')
    style = models.CharField('风格', max_length=100, blank=True, help_text='如：搞笑/专业/邻家')
    category_tags = models.CharField('擅长类目', max_length=200, blank=True)
    fans_count = models.IntegerField('粉丝总数', default=0)
    follower_count = models.IntegerField('关注数', default=0)
    avg_watch = models.IntegerField('场均观看', default=0)
    conversion_rate = models.DecimalField('转化率(%)', max_digits=5, decimal_places=2, default=0)
    contract_end = models.DateField('合同到期', null=True, blank=True)

    class Meta:
        verbose_name = '主播档案'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname


# ============== 班次 & 排班 ==============

class Shift(models.Model):
    """班次模板"""
    SHIFT_TYPE_CHOICES = [
        ('morning', '早班'),
        ('afternoon', '中班'),
        ('evening', '晚班'),
        ('night', '夜班'),
        ('custom', '自定义'),
    ]
    name = models.CharField('班次名称', max_length=50)
    type = models.CharField('类型', max_length=20, choices=SHIFT_TYPE_CHOICES, default='morning')
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    color = models.CharField('颜色', max_length=20, default='#409EFF')
    description = models.CharField('描述', max_length=200, blank=True)
    late_minutes = models.IntegerField('迟到容忍分钟', default=10)

    class Meta:
        verbose_name = '班次'
        verbose_name_plural = verbose_name
        ordering = ['start_time']

    def __str__(self):
        return f'{self.name}({self.start_time.strftime("%H:%M")}-{self.end_time.strftime("%H:%M")})'


class Schedule(models.Model):
    """排班（员工+班次+店铺+直播间+日期）"""
    STATUS_CHOICES = [
        ('scheduled', '已排班'),
        ('checked_in', '已打卡'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('absent', '缺勤'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules', verbose_name='员工')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='schedules', verbose_name='班次')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules', verbose_name='店铺')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules', verbose_name='直播间')
    date = models.DateField('日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='scheduled')
    note = models.CharField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '排班'
        verbose_name_plural = verbose_name
        ordering = ['date', 'shift__start_time']
        indexes = [
            models.Index(fields=['date', 'employee']),
            models.Index(fields=['date', 'store']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['employee', 'date', 'shift']),
        ]

    def __str__(self):
        return f'{self.employee.name} - {self.date} {self.shift.name} @ {self.store or "-"}'


# ============== 考勤 ==============

class Attendance(models.Model):
    """考勤记录"""
    CHECK_TYPE_CHOICES = [
        ('clock_in', '上班打卡'),
        ('clock_out', '下班打卡'),
    ]
    RESULT_CHOICES = [
        ('normal', '正常'),
        ('late', '迟到'),
        ('early', '早退'),
        ('absent', '缺勤'),
        ('leave', '请假'),
        ('overtime', '加班'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances', verbose_name='排班')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances', verbose_name='员工')
    check_type = models.CharField('打卡类型', max_length=20, choices=CHECK_TYPE_CHOICES)
    check_time = models.DateTimeField('打卡时间')
    result = models.CharField('结果', max_length=20, choices=RESULT_CHOICES, default='normal')
    location = models.CharField('打卡位置', max_length=200, blank=True)
    photo = models.URLField('打卡照片', blank=True)
    late_minutes = models.IntegerField('迟到分钟', default=0)
    remark = models.CharField('备注', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = verbose_name
        ordering = ['-check_time']
        indexes = [
            models.Index(fields=['employee', 'check_time']),
            models.Index(fields=['result']),
        ]

    def __str__(self):
        return f'{self.employee.name} {self.get_check_type_display()} {self.check_time}'


class LeaveRequest(models.Model):
    """请假申请"""
    LEAVE_TYPE_CHOICES = [
        ('personal', '事假'),
        ('sick', '病假'),
        ('annual', '年假'),
        ('marriage', '婚假'),
        ('bereavement', '丧假'),
        ('maternity', '产假'),
    ]
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves', verbose_name='员工')
    leave_type = models.CharField('请假类型', max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField('开始日期')
    end_date = models.DateField('结束日期')
    days = models.DecimalField('天数', max_digits=5, decimal_places=1, default=1)
    reason = models.TextField('请假原因')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    approver = models.CharField('审批人', max_length=50, blank=True)
    approve_time = models.DateTimeField('审批时间', null=True, blank=True)
    approve_remark = models.CharField('审批意见', max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['employee']),
        ]

    def __str__(self):
        return f'{self.employee.name} {self.get_leave_type_display()} {self.start_date}'


# ============== 业绩 & 直播数据 ==============

class LiveSession(models.Model):
    """一场直播记录"""
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions', verbose_name='排班')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sessions', verbose_name='主播')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='店铺')
    room = models.ForeignKey(StreamRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='直播间')
    date = models.DateField('直播日期')
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    duration_minutes = models.IntegerField('直播时长(分钟)', default=0)
    peak_viewers = models.IntegerField('峰值在线', default=0)
    avg_viewers = models.IntegerField('平均在线', default=0)
    new_followers = models.IntegerField('新增粉丝', default=0)
    gmv = models.DecimalField('GMV(元)', max_digits=12, decimal_places=2, default=0)
    orders = models.IntegerField('订单数', default=0)
    conversion_rate = models.DecimalField('转化率(%)', max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '直播记录'
        verbose_name_plural = verbose_name
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['store', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f'{self.employee.name} {self.date} GMV:{self.gmv}'


class ProductSales(models.Model):
    """单场商品销售明细"""
    session = models.ForeignKey(LiveSession, on_delete=models.CASCADE, related_name='products', verbose_name='直播场次')
    product_name = models.CharField('商品名称', max_length=200)
    sku = models.CharField('SKU', max_length=50, blank=True)
    price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField('销量', default=0)
    gmv = models.DecimalField('GMV', max_digits=12, decimal_places=2, default=0)
    commission = models.DecimalField('佣金', max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = '商品销售明细'
        verbose_name_plural = verbose_name
        indexes = [models.Index(fields=['session'])]

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'


# ============== 绩效考核 ==============

class KPIConfig(models.Model):
    """KPI 指标配置"""
    METRIC_TYPE_CHOICES = [
        ('gmv', 'GMV'),
        ('orders', '订单数'),
        ('hours', '直播时长'),
        ('followers', '新增粉丝'),
        ('conversion', '转化率'),
        ('attendance', '出勤率'),
    ]
    role = models.CharField('适用角色', max_length=20, default='anchor')
    metric = models.CharField('指标', max_length=20, choices=METRIC_TYPE_CHOICES)
    target_value = models.DecimalField('月度目标', max_digits=12, decimal_places=2, default=0)
    weight = models.DecimalField('权重(%)', max_digits=5, decimal_places=2, default=0)
    period = models.CharField('周期', max_length=20, default='monthly')
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        verbose_name = 'KPI配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.get_role_display()}-{self.get_metric_display()} 目标:{self.target_value}'


class PerformanceReview(models.Model):
    """绩效考核结果"""
    LEVEL_CHOICES = [
        ('S', 'S-优秀'),
        ('A', 'A-良好'),
        ('B', 'B-合格'),
        ('C', 'C-待改进'),
        ('D', 'D-不合格'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews', verbose_name='员工')
    period = models.CharField('考核周期', max_length=20, help_text='格式:2026-06')
    gmv = models.DecimalField('GMV达成', max_digits=12, decimal_places=2, default=0)
    gmv_target = models.DecimalField('GMV目标', max_digits=12, decimal_places=2, default=0)
    gmv_rate = models.DecimalField('GMV完成率(%)', max_digits=5, decimal_places=2, default=0)
    orders = models.IntegerField('订单数', default=0)
    live_hours = models.DecimalField('直播时长', max_digits=8, decimal_places=2, default=0)
    attendance_rate = models.DecimalField('出勤率(%)', max_digits=5, decimal_places=2, default=0)
    score = models.DecimalField('综合得分', max_digits=5, decimal_places=2, default=0)
    level = models.CharField('评级', max_length=5, choices=LEVEL_CHOICES, default='B')
    bonus = models.DecimalField('绩效奖金', max_digits=10, decimal_places=2, default=0)
    remark = models.TextField('评语', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '绩效考核'
        verbose_name_plural = verbose_name
        ordering = ['-period', '-score']
        unique_together = [('employee', 'period')]
        indexes = [
            models.Index(fields=['period']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return f'{self.employee.name} {self.period} {self.level}'


from .models_extra import *  # noqa: F401,F403
from .models_extra2 import *  # noqa: F401,F403
from .models_extra3 import *  # noqa: F401,F403
from .models_extra4 import *  # noqa: F401,F403
from .models_extra5 import *  # noqa: F401,F403
from .models_extra6 import *  # noqa: F401,F403
