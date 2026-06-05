from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import time, date, timedelta, datetime
from decimal import Decimal
import random
from scheduling.models import (
    Brand, Store, Team, StreamRoom, Employee, AnchorProfile,
    Shift, Schedule, Attendance, LeaveRequest,
    LiveSession, ProductSales, KPIConfig, PerformanceReview
)


CATEGORIES = ['美妆', '服饰', '食品', '数码', '母婴', '家居', '运动', '图书']
BRAND_NAMES = ['完美日记', '花西子', '李宁', '三只松鼠', '小米', 'babycare', '林氏木业', '安踏',
               '蕉下', '毛戈平', '薇诺娜', '良品铺子', '美的', '戴森', '雅诗兰黛', '海蓝之谜',
               '华为', '耐克', '阿迪达斯', '可口可乐']
PLATFORMS = ['douyin', 'kuaishou', 'taobao', 'xiaohongshu', 'pdd', 'jd']
ANCHOR_SURNAMES = ['李', '王', '张', '陈', '刘', '赵', '孙', '周', '吴', '郑', '冯', '蒋', '沈', '韩']
ANCHOR_GIVENS = ['梓萌', '晓彤', '思涵', '雨欣', '梦琪', '思颖', '佳怡', '婉清', '美玲', '慧君', '雅琪', '若曦',
                 '欣怡', '雪儿', '语桐', '可昕', '诗琪', '一诺', '嘉颖', '晨曦', '紫萱', '安琪', '萌萌', '甜甜']
ANCHOR_NICKS = ['萌萌子', '彤彤', '思思', '欣欣', '梦琪', '颖宝', '佳佳', '婉婉', '美美', '慧慧', '小雅', '若若',
                '欣怡', '雪儿', '小语', '可昕', '诗琪', '诺诺', '嘉嘉', '晨晨', '萱萱', '安安', '小萌', '甜甜',
                '香香', '靓靓', '仙仙', '暖暖', '悠悠', '满满']
LEVELS = ['普通', '银牌', '金牌', '王牌']
STYLES = ['搞笑', '专业', '邻家', '甜美', '御姐', '帅气', '知性']


class Command(BaseCommand):
    help = '填充企业级示例数据：品牌/店铺/小组/员工/排班/考勤/直播/绩效'

    def handle(self, *args, **options):
        self.stdout.write('清空旧数据...')
        for m in [PerformanceReview, KPIConfig, ProductSales, LiveSession, LeaveRequest,
                  Attendance, Schedule, AnchorProfile, Employee, StreamRoom,
                  Team, Store, Brand, Shift]:
            m.objects.all().delete()

        # 创建管理员账号
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        self.stdout.write(self.style.SUCCESS('管理员: admin/admin123'))

        # KPI 配置
        kpis = [
            KPIConfig(role='anchor', metric='gmv', target_value=Decimal('500000'), weight=60, period='monthly'),
            KPIConfig(role='anchor', metric='orders', target_value=Decimal('1000'), weight=10, period='monthly'),
            KPIConfig(role='anchor', metric='hours', target_value=Decimal('120'), weight=10, period='monthly'),
            KPIConfig(role='anchor', metric='conversion', target_value=Decimal('3'), weight=10, period='monthly'),
            KPIConfig(role='anchor', metric='attendance', target_value=Decimal('95'), weight=10, period='monthly'),
            KPIConfig(role='operator', metric='gmv', target_value=Decimal('800000'), weight=50, period='monthly'),
            KPIConfig(role='operator', metric='attendance', target_value=Decimal('98'), weight=20, period='monthly'),
            KPIConfig(role='manager', metric='gmv', target_value=Decimal('5000000'), weight=60, period='monthly'),
        ]
        for k in kpis: k.save()
        self.stdout.write(self.style.SUCCESS(f'创建 {len(kpis)} 个KPI配置'))

        # 班次
        shifts = [
            Shift.objects.create(name='早班', type='morning', start_time=time(8, 0), end_time=time(12, 0), color='#67C23A', description='上午直播', late_minutes=10),
            Shift.objects.create(name='中班', type='afternoon', start_time=time(12, 0), end_time=time(18, 0), color='#E6A23C', description='下午直播', late_minutes=10),
            Shift.objects.create(name='黄金班', type='evening', start_time=time(18, 0), end_time=time(23, 0), color='#F56C6C', description='黄金时段', late_minutes=5),
            Shift.objects.create(name='夜班', type='night', start_time=time(23, 0), end_time=time(2, 0), color='#909399', description='深夜直播', late_minutes=15),
        ]
        self.stdout.write(self.style.SUCCESS(f'创建 {len(shifts)} 个班次'))

        # 品牌
        brands = [Brand.objects.create(name=n, industry=random.choice(CATEGORIES), contact=f'张总', phone=f'139{random.randint(10000000, 99999999)}') for n in BRAND_NAMES]
        self.stdout.write(self.style.SUCCESS(f'创建 {len(brands)} 个品牌方'))

        # 店铺（50个）
        stores = []
        platforms_for_stores = [random.choice(PLATFORMS) for _ in range(50)]
        for i in range(50):
            platform = platforms_for_stores[i]
            platform_name = {'douyin': '抖音', 'kuaishou': '快手', 'taobao': '天猫', 'xiaohongshu': '小红书', 'pdd': '拼多多', 'jd': '京东'}[platform]
            brand = random.choice(brands)
            store = Store.objects.create(
                name=f'{brand.name}{platform_name}旗舰店{i+1:02d}',
                platform=platform,
                brand=brand,
                category=brand.industry,
                status=random.choices(['active', 'paused', 'closed'], weights=[85, 12, 3])[0],
                monthly_target=Decimal(random.randint(50, 500)),
                store_url=f'https://shop.example.com/{i}',
            )
            stores.append(store)
            # 每个店铺 1-3 个直播间
            for j in range(random.randint(1, 3)):
                StreamRoom.objects.create(
                    name=f'直播间{j+1}号',
                    store=store,
                    room_id=f'R{store.id:03d}{j+1}',
                    is_active=True
                )
        self.stdout.write(self.style.SUCCESS(f'创建 {len(stores)} 个店铺'))

        # 小组
        team_names = ['美妆一组', '美妆二组', '服饰组', '食品组', '数码组', '母婴组', '家居组', '新锐组']
        teams = [Team.objects.create(name=n, leader=f'组长{idx+1}', description=f'负责{n}相关店铺运营') for idx, n in enumerate(team_names)]
        self.stdout.write(self.style.SUCCESS(f'创建 {len(teams)} 个小组'))

        # 员工
        anchors = []
        operators = []
        managers = []

        # 100 个主播
        for i in range(100):
            name = random.choice(ANCHOR_SURNAMES) + random.choice(ANCHOR_GIVENS)
            emp = Employee.objects.create(
                name=name,
                role='anchor',
                phone=f'138{random.randint(10000000, 99999999)}',
                team=random.choice(teams),
                is_active=random.choices([True, False], weights=[92, 8])[0],
                join_date=date.today() - timedelta(days=random.randint(30, 720)),
                base_salary=Decimal(random.randint(5000, 20000)),
            )
            # 分配 1-3 个店铺
            emp.stores.set(random.sample(stores, random.randint(1, 3)))
            AnchorProfile.objects.create(
                employee=emp,
                nickname=random.choice(ANCHOR_NICKS) + str(i),
                level=random.choice(LEVELS),
                style=random.choice(STYLES),
                category_tags=random.choice(CATEGORIES),
                fans_count=random.randint(5000, 5000000),
                avg_watch=random.randint(100, 50000),
                conversion_rate=Decimal(str(round(random.uniform(0.5, 8.0), 2))),
                contract_end=date.today() + timedelta(days=random.randint(30, 720)),
            )
            anchors.append(emp)
        self.stdout.write(self.style.SUCCESS(f'创建 {len(anchors)} 个主播'))

        # 80 个运营
        for i in range(80):
            name = random.choice(ANCHOR_SURNAMES) + random.choice(['伟', '强', '磊', '勇', '军', '涛', '明', '超', '辉', '亮'])
            emp = Employee.objects.create(
                name=name,
                role='operator',
                phone=f'139{random.randint(10000000, 99999999)}',
                team=random.choice(teams),
                is_active=random.choices([True, False], weights=[95, 5])[0],
                join_date=date.today() - timedelta(days=random.randint(30, 720)),
                base_salary=Decimal(random.randint(6000, 15000)),
            )
            emp.stores.set(random.sample(stores, random.randint(2, 5)))
            operators.append(emp)
        self.stdout.write(self.style.SUCCESS(f'创建 {len(operators)} 个运营'))

        # 5 个运营经理
        for i in range(5):
            emp = Employee.objects.create(
                name=f'王经理{i+1}',
                role='manager',
                phone=f'136{random.randint(10000000, 99999999)}',
                team=teams[i % len(teams)],
                is_active=True,
                base_salary=Decimal(random.randint(15000, 30000)),
            )
            emp.stores.set(random.sample(stores, 8))
            managers.append(emp)
        self.stdout.write(self.style.SUCCESS(f'创建 {len(managers)} 个经理'))

        # 排班 - 过去 14 天 + 未来 14 天
        all_emps = anchors + operators
        today = date.today()
        schedule_dates = [today + timedelta(days=d) for d in range(-14, 15)]
        schedule_count = 0
        for d in schedule_dates:
            weekday = d.weekday()
            # 每天 60% 员工有排班
            scheduled_today = random.sample(all_emps, int(len(all_emps) * 0.6))
            for emp in scheduled_today:
                # 每人每天 0-1 个班次（不排早+晚两个）
                shift = random.choice(shifts[:3])  # 避免夜班
                if weekday >= 5 and random.random() < 0.7:
                    continue  # 周末 70% 概率不排
                store = random.choice(list(emp.stores.all())) if emp.stores.exists() else None
                room = store.rooms.first() if store else None
                _, created = Schedule.objects.get_or_create(
                    employee=emp, shift=shift, date=d,
                    defaults={'store': store, 'room': room, 'status': 'scheduled'}
                )
                if created:
                    schedule_count += 1
        self.stdout.write(self.style.SUCCESS(f'创建 {schedule_count} 条排班'))

        # 考勤 - 过去 14 天
        att_count = 0
        for sched in Schedule.objects.filter(date__lt=today, date__gte=today - timedelta(days=14)):
            r = random.random()
            if r < 0.85:
                # 正常打卡
                check_in = timezone_combine(sched.date, sched.shift.start_time) + timedelta(minutes=random.randint(-3, sched.shift.late_minutes))
                Attendance.objects.create(
                    schedule=sched, employee=sched.employee, check_type='clock_in',
                    check_time=check_in, result='normal',
                    location='办公室打卡', late_minutes=0
                )
                # 上班打卡
                check_out = timezone_combine(sched.date, sched.shift.end_time) + timedelta(minutes=random.randint(-5, 30))
                Attendance.objects.create(
                    schedule=sched, employee=sched.employee, check_type='clock_out',
                    check_time=check_out,
                    result='normal' if check_out.time() >= sched.shift.end_time else 'normal',
                )
                Schedule.objects.filter(id=sched.id).update(status='completed')
                att_count += 2
            elif r < 0.95:
                # 迟到
                check_in = timezone_combine(sched.date, sched.shift.start_time) + timedelta(minutes=random.randint(sched.shift.late_minutes + 5, 60))
                Attendance.objects.create(
                    schedule=sched, employee=sched.employee, check_type='clock_in',
                    check_time=check_in, result='late',
                    late_minutes=int((check_in - timezone_combine(sched.date, sched.shift.start_time)).total_seconds() / 60)
                )
                Schedule.objects.filter(id=sched.id).update(status='checked_in')
                att_count += 1
        self.stdout.write(self.style.SUCCESS(f'创建 {att_count} 条考勤'))

        # 直播场次 - 过去 30 天
        product_names = ['神仙水', '小金管', '遮瑕膏', '精华液', '气垫BB', '口红', '面膜', '防晒霜',
                         '连衣裙', '运动鞋', '行李箱', '蓝牙耳机', '电动牙刷', '保温杯', '零食大礼包']
        session_count = 0
        for sched in Schedule.objects.filter(date__lt=today, date__gte=today - timedelta(days=30)):
            if sched.employee.role != 'anchor' or not sched.store:
                continue
            if random.random() < 0.5:
                continue
            start = timezone_combine(sched.date, sched.shift.start_time) + timedelta(minutes=random.randint(0, 30))
            duration = random.randint(120, 300)
            end = start + timedelta(minutes=duration)
            gmv = Decimal(random.randint(10000, 500000))
            orders = random.randint(50, 2000)
            session = LiveSession.objects.create(
                schedule=sched, employee=sched.employee, store=sched.store, room=sched.room,
                date=sched.date, start_time=start, end_time=end,
                duration_minutes=duration,
                peak_viewers=random.randint(500, 50000),
                avg_viewers=random.randint(100, 10000),
                new_followers=random.randint(10, 5000),
                gmv=gmv, orders=orders,
                conversion_rate=Decimal(str(round(random.uniform(1, 8), 2))),
            )
            # 商品明细
            for _ in range(random.randint(2, 5)):
                qty = random.randint(10, 200)
                price = Decimal(random.randint(50, 999))
                ProductSales.objects.create(
                    session=session, product_name=random.choice(product_names),
                    quantity=qty, price=price, gmv=qty * price,
                )
            session_count += 1
        self.stdout.write(self.style.SUCCESS(f'创建 {session_count} 场直播'))

        # 请假申请
        for _ in range(15):
            emp = random.choice(all_emps)
            LeaveRequest.objects.create(
                employee=emp,
                leave_type=random.choice(['personal', 'sick', 'annual', 'personal', 'sick']),
                start_date=today - timedelta(days=random.randint(0, 10)),
                end_date=today + timedelta(days=random.randint(0, 5)),
                days=Decimal(str(random.uniform(0.5, 3.0))),
                reason='家中有事',
                status=random.choice(['pending', 'pending', 'approved', 'rejected']),
                approver='王经理' if random.random() < 0.7 else '',
            )
        self.stdout.write(self.style.SUCCESS('创建 15 条请假申请'))

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('企业级数据填充完成！'))
        self.stdout.write(self.style.SUCCESS(f'  - 品牌方: {Brand.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 店铺: {Store.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 主播: {Employee.objects.filter(role="anchor").count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 运营: {Employee.objects.filter(role="operator").count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 排班: {Schedule.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 考勤: {Attendance.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  - 直播: {LiveSession.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))


def timezone_combine(d, t):
    return datetime.combine(d, t)
