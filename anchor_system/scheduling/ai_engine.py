"""
MCN AI Engine - 直播电商智能引擎
基于历史数据的统计分析 + 智能推荐算法，无需外部 AI API 依赖
"""
import math
from datetime import timedelta, date, datetime
from collections import defaultdict
from django.db.models import Sum, Avg, Count, Q, F, StdDev, Max, Min
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncDate
from django.core.cache import cache

from .models import (
    Store, Employee, Shift, Schedule, Attendance,
    LiveSession, ProductSales, PerformanceReview, KPIConfig, LeaveRequest
)


# ============================================================
# 工具函数
# ============================================================

def _linear_regression(xs, ys):
    n = len(xs)
    if n < 2:
        return 0, 0, 0
    sx = sum(xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2 = sum(x * x for x in xs)
    denom = n * sx2 - sx * sx
    if denom == 0:
        return 0, sy / n, 0
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    # R²
    y_mean = sy / n
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return slope, intercept, r2


def _moving_average(data, window=7):
    if len(data) < window:
        return data[-1] if data else 0
    return sum(data[-window:]) / window


def _z_score(value, mean, std):
    if std == 0:
        return 0
    return (value - mean) / std


def _confidence_level(r2, n):
    if n < 3:
        return 'low'
    if r2 > 0.7 and n >= 7:
        return 'high'
    if r2 > 0.4:
        return 'medium'
    return 'low'


def _risk_label(r2, n, slope_pct):
    if n < 5:
        return '数据不足', 'warning'
    if slope_pct < -15:
        return '下降趋势', 'danger'
    if slope_pct < -5:
        return '轻微下降', 'warning'
    if r2 < 0.3:
        return '波动较大', 'warning'
    return '趋势良好', 'success'


# ============================================================
# 1. GMV 预测引擎
# ============================================================

class GMVPredictor:
    """基于线性回归 + 移动平均的 GMV 预测"""

    @staticmethod
    def predict(days=7, store_id=None, employee_id=None):
        today = date.today()
        lookback = min(60, max(30, days * 4))
        start = today - timedelta(days=lookback)

        qs = LiveSession.objects.filter(date__gte=start, date__lte=today)
        if store_id:
            qs = qs.filter(store_id=store_id)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        daily = list(qs.values('date').annotate(
            gmv=Sum('gmv'), orders=Sum('orders'),
            viewers=Avg('avg_viewers'), sessions=Count('id'),
        ).order_by('date'))

        if len(daily) < 3:
            return {
                'status': 'insufficient_data',
                'message': f'历史数据不足（仅{len(daily)}天），需要至少3天数据',
                'predictions': [],
                'confidence': 'low',
            }

        values = [float(d['gmv'] or 0) for d in daily]
        xs = list(range(len(values)))
        slope, intercept, r2 = _linear_regression(xs, values)
        ma7 = _moving_average(values, 7)
        ma14 = _moving_average(values, 14)
        avg_gmv = sum(values) / len(values)

        # 趋势百分比
        trend_pct = (slope / avg_gmv * 100) if avg_gmv > 0 else 0

        # 季节性调整: 按星期几计算系数
        weekday_gmv = defaultdict(list)
        for d in daily:
            weekday_gmv[d['date'].weekday()].append(float(d['gmv'] or 0))
        weekday_factor = {}
        for wd, gv_list in weekday_gmv.items():
            wd_avg = sum(gv_list) / len(gv_list)
            weekday_factor[wd] = wd_avg / avg_gmv if avg_gmv > 0 else 1.0

        predictions = []
        for i in range(1, days + 1):
            target_date = today + timedelta(days=i)
            base = slope * (len(values) + i - 1) + intercept
            # 融合移动平均
            blended = base * 0.4 + ma7 * 0.35 + ma14 * 0.25
            # 季节性调整
            wf = weekday_factor.get(target_date.weekday(), 1.0)
            predicted = max(0, blended * wf)
            predictions.append({
                'date': target_date.isoformat(),
                'weekday': ['一', '二', '三', '四', '五', '六', '日'][target_date.weekday()],
                'predicted_gmv': round(predicted, 2),
                'confidence': round(r2 * 100, 1),
            })

        # 7天汇总
        total_pred = sum(p['predicted_gmv'] for p in predictions)
        current_week_gmv = sum(values[-7:]) if len(values) >= 7 else sum(values)
        wow_change = ((total_pred - current_week_gmv) / current_week_gmv * 100) if current_week_gmv > 0 else 0

        risk, risk_type = _risk_label(r2, len(daily), trend_pct)

        return {
            'status': 'ok',
            'predictions': predictions,
            'summary': {
                'total_predicted': round(total_pred, 2),
                'daily_avg': round(total_pred / days, 2),
                'trend': round(trend_pct, 2),
                'trend_direction': 'up' if trend_pct > 0 else 'down' if trend_pct < 0 else 'flat',
                'wow_change': round(wow_change, 2),
                'r2': round(r2, 4),
                'confidence': _confidence_level(r2, len(daily)),
                'risk': risk,
                'risk_type': risk_type,
                'data_points': len(daily),
                'ma7': round(ma7, 2),
                'ma14': round(ma14, 2),
                'weekday_factors': {str(k): round(v, 3) for k, v in weekday_factor.items()},
            },
            'history_trend': [
                {'date': d['date'].isoformat(), 'gmv': float(d['gmv'] or 0)}
                for d in daily[-30:]
            ],
        }


# ============================================================
# 2. 智能排班推荐
# ============================================================

class SmartScheduler:
    """基于主播历史表现的智能排班推荐"""

    @staticmethod
    def recommend(target_date=None, store_id=None):
        target_date = target_date or date.today() + timedelta(days=1)

        # 获取所有在职主播
        anchors = Employee.objects.filter(role='anchor', is_active=True)
        if store_id:
            anchors = anchors.filter(stores__id=store_id).distinct()

        shifts = list(Shift.objects.all())
        if not shifts:
            return {'status': 'no_shifts', 'message': '请先配置班次'}

        anchor_ids = list(anchors.values_list('id', flat=True))
        if not anchor_ids:
            return {'status': 'no_anchors', 'message': '没有在职主播'}

        # 过去30天每个主播-班次组合的表现
        lookback = target_date - timedelta(days=30)
        sessions = LiveSession.objects.filter(
            employee_id__in=anchor_ids, date__gte=lookback, date__lt=target_date
        ).annotate(
            hour=ExtractHour('start_time'),
            weekday=ExtractWeekDay('date'),
        )

        # 构建主播画像
        anchor_perf = defaultdict(lambda: {'gmv': [], 'orders': [], 'viewers': [], 'hours': []})
        session_data = list(sessions.values('employee_id', 'hour', 'gmv', 'orders', 'avg_viewers', 'duration_minutes'))
        for s in session_data:
            key = s['employee_id']
            anchor_perf[key]['gmv'].append(float(s['gmv'] or 0))
            anchor_perf[key]['orders'].append(int(s['orders'] or 0))
            anchor_perf[key]['viewers'].append(int(s['avg_viewers'] or 0))
            anchor_perf[key]['hours'].append(s['hour'] or 20)

        # 每个主播在每个班次的表现分数
        anchor_shift_score = {}
        anchor_names = dict(anchors.values_list('id', 'name'))
        for aid in anchor_ids:
            perf = anchor_perf[aid]
            if not perf['gmv']:
                anchor_shift_score[aid] = {s.id: 50 for s in shifts}
                continue
            avg_gmv = sum(perf['gmv']) / len(perf['gmv'])
            avg_viewers = sum(perf['viewers']) / len(perf['viewers'])
            base_score = min(100, (avg_gmv / 50000) * 40 + (avg_viewers / 5000) * 30 + 30)

            for shift in shifts:
                start_h = shift.start_time.hour
                # 主播在该时段附近的表现加权
                hour_matches = [1 for h in perf['hours'] if abs(h - start_h) <= 2]
                time_bonus = (len(hour_matches) / max(len(perf['hours']), 1)) * 20
                anchor_shift_score.setdefault(aid, {})[shift.id] = min(100, base_score + time_bonus)

        # 已有排班
        existing = set(Schedule.objects.filter(
            date=target_date, employee_id__in=anchor_ids
        ).values_list('employee_id', 'shift_id'))

        # 考勤记录（近14天迟到率）
        late_rates = {}
        for aid in anchor_ids:
            total_att = Attendance.objects.filter(
                employee_id=aid,
                check_time__date__gte=target_date - timedelta(days=14)
            ).count()
            late_att = Attendance.objects.filter(
                employee_id=aid, result='late',
                check_time__date__gte=target_date - timedelta(days=14)
            ).count()
            late_rates[aid] = late_att / total_att if total_att > 0 else 0

        # 连续工作天数检测
        consecutive = {}
        for aid in anchor_ids:
            days_worked = 0
            for d in range(1, 8):
                if Schedule.objects.filter(employee_id=aid, date=target_date - timedelta(days=d)).exists():
                    days_worked += 1
                else:
                    break
            consecutive[aid] = days_worked

        # 贪心匹配: 按分数排序，每个班次分配最优主播
        recommendations = []
        assigned_anchors = set()
        for shift in shifts:
            candidates = []
            for aid in anchor_ids:
                if (aid, shift.id) in existing:
                    continue
                if aid in assigned_anchors:
                    continue
                score = anchor_shift_score.get(aid, {}).get(shift.id, 50)
                # 疲劳惩罚
                if consecutive[aid] >= 5:
                    score *= 0.3
                elif consecutive[aid] >= 3:
                    score *= 0.7
                # 迟到惩罚
                score *= (1 - late_rates.get(aid, 0) * 0.5)
                candidates.append({'anchor_id': aid, 'score': round(score, 1)})

            candidates.sort(key=lambda x: x['score'], reverse=True)

            rec = {
                'shift_id': shift.id,
                'shift_name': shift.name,
                'shift_time': f'{shift.start_time.strftime("%H:%M")}-{shift.end_time.strftime("%H:%M")}',
                'candidates': [],
            }
            for c in candidates[:3]:
                aid = c['anchor_id']
                rec['candidates'].append({
                    'anchor_id': aid,
                    'anchor_name': anchor_names.get(aid, ''),
                    'score': c['score'],
                    'consecutive_days': consecutive[aid],
                    'late_rate': round(late_rates.get(aid, 0) * 100, 1),
                    'reason': SmartScheduler._reason(c['score'], consecutive[aid], late_rates.get(aid, 0)),
                })
            if rec['candidates']:
                assigned_anchors.add(rec['candidates'][0]['anchor_id'])
            recommendations.append(rec)

        return {
            'status': 'ok',
            'target_date': target_date.isoformat(),
            'recommendations': recommendations,
            'summary': {
                'total_anchors': len(anchor_ids),
                'available_anchors': len(anchor_ids) - len(existing),
                'shifts_count': len(shifts),
                'best_combo_score': sum(
                    r['candidates'][0]['score'] for r in recommendations if r['candidates']
                ) / max(len([r for r in recommendations if r['candidates']]), 1),
            },
        }

    @staticmethod
    def _reason(score, consecutive, late_rate):
        reasons = []
        if score >= 80:
            reasons.append('历史表现优异')
        elif score >= 60:
            reasons.append('表现稳定')
        if consecutive >= 5:
            reasons.append('⚠连续工作过多建议休息')
        elif consecutive == 0:
            reasons.append('精力充沛')
        if late_rate > 0.2:
            reasons.append('迟到率偏高')
        return '，'.join(reasons) if reasons else '可安排'


# ============================================================
# 3. 主播画像分析
# ============================================================

class AnchorProfiler:
    """主播综合画像与能力分析"""

    @staticmethod
    def analyze(employee_id):
        try:
            anchor = Employee.objects.select_related('anchor_profile').get(id=employee_id, role='anchor')
        except Employee.DoesNotExist:
            return {'status': 'error', 'message': '主播不存在'}

        today = date.today()
        last_30 = today - timedelta(days=30)
        last_90 = today - timedelta(days=90)

        sessions_30 = LiveSession.objects.filter(employee=anchor, date__gte=last_30)
        sessions_90 = LiveSession.objects.filter(employee=anchor, date__gte=last_90)

        # 核心指标
        agg_30 = sessions_30.aggregate(
            total_gmv=Sum('gmv'), total_orders=Sum('orders'),
            avg_viewers=Avg('avg_viewers'), avg_conversion=Avg('conversion_rate'),
            total_followers=Sum('new_followers'), total_hours=Sum('duration_minutes'),
            session_count=Count('id'),
        )
        agg_90 = sessions_90.aggregate(
            total_gmv=Sum('gmv'), session_count=Count('id'),
        )

        gmv_30 = float(agg_30['total_gmv'] or 0)
        orders_30 = int(agg_30['total_orders'] or 0)
        sessions_count = int(agg_30['session_count'] or 0)
        avg_viewers = float(agg_30['avg_viewers'] or 0)
        avg_conversion = float(agg_30['avg_conversion'] or 0)
        total_hours = int(agg_30['total_hours'] or 0)
        new_followers = int(agg_30['total_followers'] or 0)

        # 趋势对比: 最近15天 vs 之前15天
        mid = today - timedelta(days=15)
        recent = LiveSession.objects.filter(employee=anchor, date__gte=mid).aggregate(
            gmv=Sum('gmv'), orders=Sum('orders'), viewers=Avg('avg_viewers')
        )
        earlier = LiveSession.objects.filter(
            employee=anchor, date__gte=last_30, date__lt=mid
        ).aggregate(
            gmv=Sum('gmv'), orders=Sum('orders'), viewers=Avg('avg_viewers')
        )

        recent_gmv = float(recent['gmv'] or 0)
        earlier_gmv = float(earlier['gmv'] or 0)
        gmv_trend = ((recent_gmv - earlier_gmv) / earlier_gmv * 100) if earlier_gmv > 0 else 0

        # 五维能力评分
        all_anchors_gmv = list(
            LiveSession.objects.filter(date__gte=last_30).values('employee_id').annotate(
                gmv=Sum('gmv')
            ).values_list('gmv', flat=True)
        )
        gmv_list = [float(g) for g in all_anchors_gmv if g]
        gmv_mean = sum(gmv_list) / len(gmv_list) if gmv_list else 0
        gmv_std = (sum((g - gmv_mean) ** 2 for g in gmv_list) / len(gmv_list)) ** 0.5 if len(gmv_list) > 1 else 0

        dimensions = {
            'sales': min(100, max(20, 50 + _z_score(gmv_30, gmv_mean, gmv_std) * 15)),
            'traffic': min(100, max(20, min(avg_viewers / 100, 1) * 80 + 20)),
            'conversion': min(100, max(20, min(avg_conversion / 5, 1) * 80 + 20)),
            'stability': 70,
            'growth': min(100, max(20, 50 + gmv_trend * 0.5)),
        }

        # 出勤率
        scheds_30 = Schedule.objects.filter(employee=anchor, date__gte=last_30).count()
        attended_30 = Schedule.objects.filter(
            employee=anchor, date__gte=last_30, status__in=['checked_in', 'completed']
        ).count()
        att_rate = attended_30 / scheds_30 * 100 if scheds_30 > 0 else 100
        dimensions['stability'] = min(100, max(20, att_rate * 0.5 + min(sessions_count / 20, 1) * 50))

        overall = sum(dimensions.values()) / len(dimensions)

        # 最强时段
        best_hours = list(
            LiveSession.objects.filter(employee=anchor, date__gte=last_30).annotate(
                hour=ExtractHour('start_time')
            ).values('hour').annotate(
                avg_gmv=Avg('gmv'), cnt=Count('id')
            ).order_by('-avg_gmv')[:3]
        )

        # 最佳店铺
        best_stores = list(
            LiveSession.objects.filter(employee=anchor, date__gte=last_30).values(
                'store__name', 'store__platform'
            ).annotate(
                gmv=Sum('gmv'), sessions=Count('id')
            ).order_by('-gmv')[:3]
        )

        # AI 洞察
        insights = AnchorProfiler._generate_insights(
            gmv_30, gmv_trend, avg_viewers, avg_conversion, att_rate, sessions_count, total_hours
        )

        profile = anchor.anchor_profile
        return {
            'status': 'ok',
            'anchor': {
                'id': anchor.id,
                'name': anchor.name,
                'nickname': profile.nickname if profile else anchor.name,
                'level': profile.level if profile else '-',
                'fans': profile.fans_count if profile else 0,
                'stores': [s.name for s in anchor.stores.all()[:5]],
            },
            'metrics_30d': {
                'gmv': round(gmv_30, 2),
                'orders': orders_30,
                'sessions': sessions_count,
                'avg_viewers': round(avg_viewers, 0),
                'avg_conversion': round(avg_conversion, 2),
                'total_hours': round(total_hours / 60, 1),
                'new_followers': new_followers,
                'attendance_rate': round(att_rate, 1),
            },
            'trend': {
                'gmv_trend_pct': round(gmv_trend, 2),
                'direction': 'up' if gmv_trend > 5 else 'down' if gmv_trend < -5 else 'stable',
            },
            'dimensions': {k: round(v, 1) for k, v in dimensions.items()},
            'overall_score': round(overall, 1),
            'best_hours': [
                {'hour': h['hour'], 'avg_gmv': float(h['avg_gmv'] or 0), 'sessions': h['cnt']}
                for h in best_hours
            ],
            'best_stores': [
                {'name': s['store__name'], 'platform': s['store__platform'], 'gmv': float(s['gmv'] or 0)}
                for s in best_stores
            ],
            'insights': insights,
        }

    @staticmethod
    def _generate_insights(gmv, trend, viewers, conversion, att_rate, sessions, hours):
        insights = []
        if trend > 20:
            insights.append({'type': 'success', 'icon': '📈', 'text': f'近半月GMV增长{trend:.0f}%，正处于上升期'})
        elif trend < -20:
            insights.append({'type': 'danger', 'icon': '📉', 'text': f'近半月GMV下降{abs(trend):.0f}%，建议排查原因'})
        if conversion > 3:
            insights.append({'type': 'success', 'icon': '🎯', 'text': f'转化率{conversion:.1f}%高于平均水平，带货能力强'})
        elif conversion < 1:
            insights.append({'type': 'warning', 'icon': '⚠️', 'text': f'转化率仅{conversion:.1f}%，建议优化话术和选品'})
        if att_rate < 80:
            insights.append({'type': 'danger', 'icon': '🕐', 'text': f'出勤率{att_rate:.0f}%偏低，影响排班稳定性'})
        if sessions >= 25:
            insights.append({'type': 'warning', 'icon': '🔥', 'text': f'30天内直播{sessions}场，注意劳逸结合'})
        if viewers > 5000:
            insights.append({'type': 'success', 'icon': '👀', 'text': f'场均观看{viewers:.0f}，流量获取能力突出'})
        if gmv > 100000 and sessions > 0:
            insights.append({'type': 'success', 'icon': '💎', 'text': f'场均GMV {gmv/sessions:.0f}元，销售效率高'})
        if not insights:
            insights.append({'type': 'info', 'icon': '📊', 'text': '数据表现稳定，继续保持'})
        return insights


# ============================================================
# 4. 异常检测
# ============================================================

class AnomalyDetector:
    """直播数据异常检测 (Z-Score + 规则引擎)"""

    @staticmethod
    def detect(days=7):
        today = date.today()
        start = today - timedelta(days=days)

        sessions = list(LiveSession.objects.filter(
            date__gte=start, date__lte=today
        ).select_related('employee', 'store').annotate(
            hour=ExtractHour('start_time'),
        ))

        if len(sessions) < 5:
            return {'status': 'insufficient_data', 'anomalies': [], 'summary': {'total_checked': len(sessions)}}

        # 计算全局统计
        gmv_values = [float(s.gmv) for s in sessions]
        viewer_values = [float(s.avg_viewers) for s in sessions]
        conv_values = [float(s.conversion_rate) for s in sessions]

        def _stats(vals):
            m = sum(vals) / len(vals)
            std = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5 if len(vals) > 1 else 0
            return m, std

        gmv_mean, gmv_std = _stats(gmv_values)
        viewer_mean, viewer_std = _stats(viewer_values)
        conv_mean, conv_std = _stats(conv_values)

        anomalies = []
        for s in sessions:
            gmv = float(s.gmv)
            viewers = float(s.avg_viewers)
            conv = float(s.conversion_rate)
            flags = []

            # Z-Score 异常
            if gmv_std > 0:
                z = _z_score(gmv, gmv_mean, gmv_std)
                if z < -2:
                    flags.append(f'GMV异常偏低(偏离{abs(z):.1f}个标准差)')
                elif z > 2:
                    flags.append(f'GMV异常偏高(高出{z:.1f}个标准差)')

            if viewer_std > 0:
                z = _z_score(viewers, viewer_mean, viewer_std)
                if z < -2:
                    flags.append(f'流量骤降(偏离{abs(z):.1f}σ)')

            if conv_std > 0 and conv > 0:
                z = _z_score(conv, conv_mean, conv_std)
                if z < -1.5:
                    flags.append(f'转化率异常低({conv:.1f}%)')

            # 规则引擎
            if s.duration_minutes < 30 and s.duration_minutes > 0:
                flags.append('直播时长过短(<30分钟)')
            if gmv > 0 and s.orders == 0:
                flags.append('有GMV但订单数为0，数据可能异常')
            if conv > 15:
                flags.append(f'转化率超高({conv:.1f}%)，请核实')
            if s.duration_minutes > 480:
                flags.append(f'直播超长({s.duration_minutes//60}小时)，注意疲劳风险')

            if flags:
                severity = 'critical' if any('偏低' in f or '骤降' in f for f in flags) else 'warning'
                anomalies.append({
                    'session_id': s.id,
                    'date': s.date.isoformat(),
                    'anchor': s.employee.name,
                    'store': s.store.name if s.store else '-',
                    'gmv': gmv,
                    'viewers': viewers,
                    'conversion': conv,
                    'duration': s.duration_minutes,
                    'flags': flags,
                    'severity': severity,
                })

        anomalies.sort(key=lambda x: 0 if x['severity'] == 'critical' else 1)

        # 汇总
        anchor_flags = defaultdict(int)
        for a in anomalies:
            anchor_flags[a['anchor']] += 1

        return {
            'status': 'ok',
            'anomalies': anomalies[:50],
            'summary': {
                'total_checked': len(sessions),
                'anomaly_count': len(anomalies),
                'critical_count': sum(1 for a in anomalies if a['severity'] == 'critical'),
                'anomaly_rate': round(len(anomalies) / len(sessions) * 100, 1),
                'top_flagged': [
                    {'name': k, 'count': v} for k, v in sorted(anchor_flags.items(), key=lambda x: -x[1])[:5]
                ],
            },
        }


# ============================================================
# 5. 运营建议引擎
# ============================================================

class InsightEngine:
    """AI 运营建议 - 综合数据生成可执行建议"""

    @staticmethod
    def generate():
        today = date.today()
        last_30 = today - timedelta(days=30)
        last_7 = today - timedelta(days=7)

        recommendations = []

        # 1. 店铺健康度
        stores = Store.objects.filter(status='active')
        for store in stores:
            sessions_30 = LiveSession.objects.filter(store=store, date__gte=last_30)
            agg = sessions_30.aggregate(
                gmv=Sum('gmv'), sessions=Count('id'),
                avg_conv=Avg('conversion_rate'), avg_viewers=Avg('avg_viewers'),
            )
            gmv = float(agg['gmv'] or 0)
            sessions_cnt = int(agg['sessions'] or 0)
            if sessions_cnt == 0:
                continue

            target = float(store.monthly_target or 0) * 10000
            completion = (gmv / target * 100) if target > 0 else 100

            if completion < 50 and target > 0:
                recommendations.append({
                    'priority': 'high',
                    'category': 'store',
                    'icon': '🏪',
                    'title': f'{store.name} 目标达成率仅{completion:.0f}%',
                    'detail': f'30天GMV {gmv/10000:.1f}万，月目标{store.monthly_target}万。建议增加直播场次或调整主播配置。',
                    'action': '查看排班',
                    'store_id': store.id,
                })

            avg_conv = float(agg['avg_conv'] or 0)
            if avg_conv < 1 and sessions_cnt >= 5:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'conversion',
                    'icon': '🎯',
                    'title': f'{store.name} 转化率偏低({avg_conv:.1f}%)',
                    'detail': f'近30天{sessions_cnt}场直播平均转化率仅{avg_conv:.1f}%，建议优化选品策略和主播话术。',
                    'action': '查看主播分析',
                })

        # 2. 主播风险
        anchors = Employee.objects.filter(role='anchor', is_active=True)
        for anchor in anchors:
            # 连续工作天数
            consecutive = 0
            for d in range(0, 7):
                if Schedule.objects.filter(employee=anchor, date=today - timedelta(days=d)).exists():
                    consecutive += 1
                else:
                    break
            if consecutive >= 6:
                recommendations.append({
                    'priority': 'high',
                    'category': 'fatigue',
                    'icon': '😴',
                    'title': f'{anchor.name} 已连续工作{consecutive}天',
                    'detail': '过度疲劳会导致直播质量下降和主播流失风险。建议安排调休。',
                    'action': '调整排班',
                    'employee_id': anchor.id,
                })

            # 合同到期
            profile = getattr(anchor, 'anchor_profile', None)
            if profile and profile.contract_end:
                days_left = (profile.contract_end - today).days
                if 0 < days_left <= 30:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'contract',
                        'icon': '📋',
                        'title': f'{anchor.name} 合同{days_left}天后到期',
                        'detail': f'合同到期日: {profile.contract_end.isoformat()}。请尽快启动续约沟通。',
                        'action': '查看详情',
                        'employee_id': anchor.id,
                    })

        # 3. 考勤异常
        late_anchors = Attendance.objects.filter(
            result='late', check_time__date__gte=last_7
        ).values('employee__name').annotate(
            late_count=Count('id')
        ).filter(late_count__gte=2).order_by('-late_count')

        for la in late_anchors:
            recommendations.append({
                'priority': 'medium',
                'category': 'attendance',
                'icon': '⏰',
                'title': f'{la["employee__name"]} 近7天迟到{la["late_count"]}次',
                'detail': '频繁迟到影响团队纪律和直播准时开播，建议进行沟通。',
                'action': '查看考勤',
            })

        # 4. 待审批请假
        pending = LeaveRequest.objects.filter(status='pending').count()
        if pending > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'leave',
                'icon': '📝',
                'title': f'{pending}条请假申请待审批',
                'detail': '及时审批可避免排班冲突，影响运营安排。',
                'action': '去审批',
            })

        # 5. GMV 趋势预警
        recent_7 = float(LiveSession.objects.filter(date__gte=last_7).aggregate(
            gmv=Sum('gmv')
        )['gmv'] or 0)
        prev_7 = float(LiveSession.objects.filter(
            date__gte=last_30, date__lt=last_7
        ).aggregate(gmv=Sum('gmv'))['gmv'] or 0) / 3  # 日均

        if prev_7 > 0:
            recent_daily = recent_7 / 7
            change = (recent_daily - prev_7) / prev_7 * 100
            if change < -20:
                recommendations.append({
                    'priority': 'high',
                    'category': 'revenue',
                    'icon': '📉',
                    'title': f'全盘GMV近期下降{abs(change):.0f}%',
                    'detail': f'近7天日均{recent_daily/10000:.1f}万，之前日均{prev_7/10000:.1f}万。需排查原因。',
                    'action': '查看数据驾驶舱',
                })

        # 排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 2))

        return {
            'status': 'ok',
            'recommendations': recommendations,
            'summary': {
                'total': len(recommendations),
                'high': sum(1 for r in recommendations if r['priority'] == 'high'),
                'medium': sum(1 for r in recommendations if r['priority'] == 'medium'),
                'categories': list(set(r['category'] for r in recommendations)),
            },
        }


# ============================================================
# 6. 主播-店铺匹配推荐
# ============================================================

class AnchorMatcher:
    """基于历史数据的最佳主播-店铺匹配"""

    @staticmethod
    def match(store_id=None):
        anchors = Employee.objects.filter(role='anchor', is_active=True).select_related('anchor_profile')
        stores = Store.objects.filter(status='active')
        if store_id:
            stores = stores.filter(id=store_id)

        today = date.today()
        last_30 = today - timedelta(days=30)

        # 每个主播在每个店铺的表现
        combos = LiveSession.objects.filter(
            date__gte=last_30, employee__role='anchor'
        ).values('employee_id', 'employee__name', 'store_id', 'store__name', 'store__platform').annotate(
            gmv=Sum('gmv'), orders=Sum('orders'), sessions=Count('id'),
            avg_viewers=Avg('avg_viewers'), avg_conversion=Avg('conversion_rate'),
        ).order_by('-gmv')

        combo_list = []
        for c in combos:
            score = (
                min(float(c['gmv'] or 0) / 100000, 1) * 40 +
                min(float(c['avg_viewers'] or 0) / 5000, 1) * 20 +
                min(float(c['avg_conversion'] or 0) / 5, 1) * 20 +
                min(c['sessions'] / 10, 1) * 20
            )
            combo_list.append({
                'anchor_id': c['employee_id'],
                'anchor_name': c['employee__name'],
                'store_id': c['store_id'],
                'store_name': c['store__name'],
                'platform': c['store__platform'],
                'gmv': float(c['gmv'] or 0),
                'orders': int(c['orders'] or 0),
                'sessions': c['sessions'],
                'avg_viewers': round(float(c['avg_viewers'] or 0), 0),
                'avg_conversion': round(float(c['avg_conversion'] or 0), 2),
                'score': round(score, 1),
            })

        # 每个店铺推荐最佳主播
        store_recs = defaultdict(list)
        for c in combo_list:
            store_recs[c['store_id']].append(c)

        result = []
        for store in stores:
            recs = store_recs.get(store.id, [])
            recs.sort(key=lambda x: x['score'], reverse=True)
            result.append({
                'store_id': store.id,
                'store_name': store.name,
                'platform': store.platform,
                'top_anchors': recs[:5],
                'has_data': len(recs) > 0,
            })

        return {
            'status': 'ok',
            'matches': result,
            'best_combos': sorted(combo_list, key=lambda x: x['score'], reverse=True)[:20],
        }
