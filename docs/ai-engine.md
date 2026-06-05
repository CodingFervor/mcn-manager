# MCN AI Engine 技术文档

> 版本: 1.0 | 纯算法引擎，无需外部 AI API 依赖 | 基于 Django ORM + 统计分析

---

## 目录

- [架构概览](#架构概览)
- [GMVPredictor -- GMV 预测引擎](#1-gmvpredictor----gmv-预测引擎)
- [SmartScheduler -- 智能排班推荐](#2-smartscheduler----智能排班推荐)
- [AnchorProfiler -- 主播画像分析](#3-anchorprofiler----主播画像分析)
- [AnomalyDetector -- 异常数据检测](#4-anomalydetector----异常数据检测)
- [InsightEngine -- 运营建议引擎](#5-insightengine----运营建议引擎)
- [AnchorMatcher -- 主播店铺匹配](#6-anchormatcher----主播店铺匹配)
- [缓存策略](#缓存策略)

---

## 架构概览

MCN AI Engine 包含 6 个独立的智能引擎，全部基于历史数据的统计分析和规则引擎实现，不依赖任何外部 AI 服务。

```
                    +-------------------+
                    |   AIViewSet       |
                    |   (API 入口)      |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v----+  +------v----+
     | GMV        |  | Smart     |  | Anchor    |
     | Predictor  |  | Scheduler |  | Profiler  |
     +--------+---+  +------+----+  +------+----+
              |              |              |
     +--------v---+  +------v----+  +------v----+
     | Anomaly    |  | Insight   |  | Anchor    |
     | Detector   |  | Engine    |  | Matcher   |
     +------------+  +-----------+  +-----------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v----------+
                    |  Django ORM       |
                    |  (LiveSession,    |
                    |   Schedule, ...)  |
                    +-------------------+
```

### 公共工具函数

| 函数 | 用途 |
|------|------|
| `_linear_regression(xs, ys)` | 最小二乘法线性回归，返回 slope, intercept, R-squared |
| `_moving_average(data, window)` | 滑动窗口移动平均 |
| `_z_score(value, mean, std)` | 标准 Z-Score 计算公式 |
| `_confidence_level(r2, n)` | 基于 R-squared 和样本量的置信度评估 |
| `_risk_label(r2, n, slope_pct)` | 风险标签生成 |

---

## 1. GMVPredictor -- GMV 预测引擎

### 接口

```
GET /api/ai/predict/?days=7&store_id=1&employee_id=5
```

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| days | int | 1 - 30 | 预测天数 (默认 7) |
| store_id | int | 可选 | 按店铺筛选 |
| employee_id | int | 可选 | 按主播筛选 |

### 算法原理

采用 **线性回归 + 移动平均 + 季节性调整** 三层融合模型:

#### 步骤一: 线性回归拟合

对历史 N 天的日 GMV 数据，使用最小二乘法拟合线性回归模型:

```
slope     = (n * Sum(xi*yi) - Sum(xi)*Sum(yi)) / (n * Sum(xi^2) - Sum(xi)^2)
intercept = (Sum(yi) - slope * Sum(xi)) / n
```

拟合度 (R-squared):

```
R^2 = 1 - SS_res / SS_tot
  SS_res = Sum((yi - (slope*xi + intercept))^2)
  SS_tot = Sum((yi - y_mean)^2)
```

#### 步骤二: 季节性系数

按星期几计算调整系数:

```
weekday_factor(w) = 该星期几的平均GMV / 全局平均GMV
```

#### 步骤三: 三层融合

```
base    = slope * (N + i - 1) + intercept          # 线性回归基线
blended = base * 0.40 + MA7 * 0.35 + MA14 * 0.25   # 融合移动平均
predicted = max(0, blended * weekday_factor(w))     # 季节性调整
```

### 置信度评估

| 级别 | 条件 |
|------|------|
| `high` | R^2 > 0.7 且数据点 >= 7 |
| `medium` | R^2 > 0.4 |
| `low` | 其他情况 |

### 风险标签

| 标签 | 条件 | 级别 |
|------|------|------|
| 数据不足 | 样本 < 5 天 | warning |
| 下降趋势 | 周期斜率 < -15% | danger |
| 轻微下降 | 周期斜率 < -5% | warning |
| 波动较大 | R^2 < 0.3 | warning |
| 趋势良好 | 其他 | success |

### 响应示例

```json
{
  "status": "ok",
  "predictions": [
    {
      "date": "2026-06-06",
      "weekday": "六",
      "predicted_gmv": 62850.75,
      "confidence": 72.3
    },
    {
      "date": "2026-06-07",
      "weekday": "日",
      "predicted_gmv": 71200.40,
      "confidence": 72.3
    }
  ],
  "summary": {
    "total_predicted": 448925.30,
    "daily_avg": 64132.19,
    "trend": 5.23,
    "trend_direction": "up",
    "wow_change": 3.15,
    "r2": 0.7230,
    "confidence": "high",
    "risk": "趋势良好",
    "risk_type": "success",
    "data_points": 30,
    "ma7": 62100.50,
    "ma14": 58900.30,
    "weekday_factors": {
      "0": 0.95,
      "1": 0.92,
      "2": 0.98,
      "3": 1.02,
      "4": 1.05,
      "5": 1.12,
      "6": 1.15
    }
  },
  "history_trend": [
    {"date": "2026-05-07", "gmv": 52000.00},
    {"date": "2026-05-08", "gmv": 55000.00}
  ]
}
```

### 最小数据要求

至少 3 天历史数据。不足时返回:

```json
{
  "status": "insufficient_data",
  "message": "历史数据不足（仅2天），需要至少3天数据",
  "predictions": [],
  "confidence": "low"
}
```

---

## 2. SmartScheduler -- 智能排班推荐

### 接口

```
GET /api/ai/schedule/?date=2026-06-06&store_id=1
```

| 参数 | 类型 | 说明 |
|------|------|------|
| date | date | 目标日期 (默认明天) |
| store_id | int | 按店铺筛选 (可选) |

### 算法原理

采用 **贪心匹配 + 多因子评分** 策略: 对每个班次，按综合评分从高到低排列候选人，取最优分配。

#### 评分公式

```
final_score = base_score * fatigue_penalty * late_penalty
```

#### base_score 计算 (0-100)

```
base_score = min(avg_gmv / 50000, 1) * 40      # GMV 贡献 (权重 40)
           + min(avg_viewers / 5000, 1) * 30    # 流量贡献 (权重 30)
           + 30                                   # 基础分
           + time_bonus                           # 时段匹配奖励 (最高 20)
```

**时段匹配奖励:**

```
time_bonus = (主播在该班次时段附近开播次数 / 总开播次数) * 20
```

判定条件: 主播历史开播时间与班次开始时间差 <= 2 小时。

#### 疲劳惩罚

| 连续工作天数 | 惩罚系数 |
|------------|---------|
| >= 5 天 | x 0.3 (强烈建议休息) |
| >= 3 天 | x 0.7 |
| < 3 天 | x 1.0 |

#### 迟到惩罚

```
late_penalty = 1 - late_rate * 0.5
```

近 14 天迟到率越高，惩罚越大。

### 匹配流程

1. 获取所有在职主播和班次模板
2. 计算每个主播在每个班次的表现分
3. 获取已有排班 (排除已排班主播)
4. 获取近 14 天迟到率
5. 获取连续工作天数
6. 贪心分配: 按班次遍历，每班分配评分最高的未分配主播

### 响应示例

```json
{
  "status": "ok",
  "target_date": "2026-06-06",
  "recommendations": [
    {
      "shift_id": 1,
      "shift_name": "早班",
      "shift_time": "08:00-14:00",
      "candidates": [
        {
          "anchor_id": 5,
          "anchor_name": "李佳琦",
          "score": 85.2,
          "consecutive_days": 0,
          "late_rate": 5.0,
          "reason": "历史表现优异，精力充沛"
        },
        {
          "anchor_id": 8,
          "anchor_name": "薇娅",
          "score": 72.1,
          "consecutive_days": 2,
          "late_rate": 0.0,
          "reason": "表现稳定"
        }
      ]
    },
    {
      "shift_id": 2,
      "shift_name": "晚班",
      "shift_time": "18:00-24:00",
      "candidates": [
        {
          "anchor_id": 12,
          "anchor_name": "张三",
          "score": 25.5,
          "consecutive_days": 5,
          "late_rate": 15.0,
          "reason": "历史表现优异，连续工作过多建议休息，迟到率偏高"
        }
      ]
    }
  ],
  "summary": {
    "total_anchors": 15,
    "available_anchors": 12,
    "shifts_count": 4,
    "best_combo_score": 78.6
  }
}
```

### 推荐理由生成规则

| 条件 | 生成文本 |
|------|---------|
| score >= 80 | "历史表现优异" |
| score >= 60 | "表现稳定" |
| consecutive >= 5 | "连续工作过多建议休息" |
| consecutive == 0 | "精力充沛" |
| late_rate > 20% | "迟到率偏高" |
| 默认 | "可安排" |

---

## 3. AnchorProfiler -- 主播画像分析

### 接口

```
GET /api/ai/anchor/?employee_id=5
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| employee_id | int | 是 | 主播员工 ID |

### 五维能力模型

基于最近 30 天的直播数据，从 5 个维度量化主播能力:

#### 销售力 (sales)

```
sales = clamp(50 + Z-Score(gmv_30d, 全局gmv均值, 全局gmv标准差) * 15, 20, 100)
```

将主播 30 天 GMV 与全平台所有主播的均值和标准差进行 Z-Score 标准化后映射到 20-100 区间。

#### 流量力 (traffic)

```
traffic = clamp(min(avg_viewers / 100, 1) * 80 + 20, 20, 100)
```

基于场均观看人数，每 100 人对应 80 分的线性映射。

#### 转化力 (conversion)

```
conversion = clamp(min(avg_conversion / 5, 1) * 80 + 20, 20, 100)
```

基于平均转化率，5% 对应满分 100 的线性映射。

#### 稳定性 (stability)

```
stability = clamp(attendance_rate * 0.5 + min(sessions / 20, 1) * 50, 20, 100)
```

综合出勤率和开播频率的稳定性评估。

#### 成长性 (growth)

```
growth = clamp(50 + gmv_trend_15d * 0.5, 20, 100)
```

基于近半月与上半月的 GMV 环比增长率。

#### 综合评分

```
overall = (sales + traffic + conversion + stability + growth) / 5
```

### 趋势对比逻辑

将最近 30 天分为两个 15 天区间:

```
gmv_trend = (recent_15d_gmv - earlier_15d_gmv) / earlier_15d_gmv * 100
```

| 趋势 | 方向判定 |
|------|---------|
| > +5% | `up` |
| -5% ~ +5% | `stable` |
| < -5% | `down` |

### AI 洞察规则

系统根据主播各项指标自动生成洞察建议:

| 条件 | 类型 | 洞察文本 |
|------|------|---------|
| GMV 增长 > 20% | success | "近半月GMV增长{trend}%，正处于上升期" |
| GMV 下降 > 20% | danger | "近半月GMV下降{trend}%，建议排查原因" |
| 转化率 > 3% | success | "转化率{conv}%高于平均水平，带货能力强" |
| 转化率 < 1% | warning | "转化率仅{conv}%，建议优化话术和选品" |
| 出勤率 < 80% | danger | "出勤率{rate}%偏低，影响排班稳定性" |
| 30天直播 >= 25场 | warning | "30天内直播{sessions}场，注意劳逸结合" |
| 场均观看 > 5000 | success | "场均观看{viewers}，流量获取能力突出" |
| 场均GMV较高 | success | "场均GMV {avg}元，销售效率高" |
| 默认 | info | "数据表现稳定，继续保持" |

### 响应示例

```json
{
  "status": "ok",
  "anchor": {
    "id": 5,
    "name": "李佳琦",
    "nickname": "佳琦LJQ",
    "level": "金牌",
    "fans": 3500000,
    "stores": ["旗舰店", "美妆专营店"]
  },
  "metrics_30d": {
    "gmv": 1280000.00,
    "orders": 5600,
    "sessions": 28,
    "avg_viewers": 8500,
    "avg_conversion": 3.82,
    "total_hours": 56.0,
    "new_followers": 28000,
    "attendance_rate": 96.4
  },
  "trend": {
    "gmv_trend_pct": 12.5,
    "direction": "up"
  },
  "dimensions": {
    "sales": 82.5,
    "traffic": 88.0,
    "conversion": 81.2,
    "stability": 92.0,
    "growth": 56.3
  },
  "overall_score": 80.0,
  "best_hours": [
    {"hour": 20, "avg_gmv": 65000.00, "sessions": 12},
    {"hour": 19, "avg_gmv": 58000.00, "sessions": 8},
    {"hour": 21, "avg_gmv": 52000.00, "sessions": 5}
  ],
  "best_stores": [
    {"name": "旗舰店", "platform": "douyin", "gmv": 850000.00},
    {"name": "美妆专营店", "platform": "taobao", "gmv": 430000.00}
  ],
  "insights": [
    {"type": "success", "icon": "📈", "text": "近半月GMV增长13%，正处于上升期"},
    {"type": "success", "icon": "🎯", "text": "转化率3.8%高于平均水平，带货能力强"},
    {"type": "success", "icon": "👀", "text": "场均观看8500，流量获取能力突出"}
  ]
}
```

---

## 4. AnomalyDetector -- 异常数据检测

### 接口

```
GET /api/ai/anomaly/?days=7
```

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| days | int | 1 - 30 | 检测天数 (默认 7) |

### 算法原理

采用 **Z-Score 统计检测 + 业务规则引擎** 双重检测机制。

#### Z-Score 统计检测

对指定时间范围内的所有直播场次，计算 GMV、平均观看、转化率三个维度的全局均值和标准差:

```
z = (value - mean) / std
```

| 检测维度 | 阈值 | 异常判定 |
|---------|------|---------|
| GMV | z < -2 | "GMV异常偏低(偏离{z}个标准差)" |
| GMV | z > 2 | "GMV异常偏高(高出{z}个标准差)" |
| 平均观看 | z < -2 | "流量骤降(偏离{z}σ)" |
| 转化率 | z < -1.5 | "转化率异常低({value}%)" |

#### 业务规则引擎

| 规则 | 触发条件 | 说明 |
|------|---------|------|
| 直播过短 | duration < 30 min | 可能是异常开播 |
| 数据矛盾 | GMV > 0 且 orders == 0 | 数据录入可能出错 |
| 转化率超高 | conversion > 15% | 需人工核实 |
| 超长直播 | duration > 480 min | 疲劳风险预警 |

#### 严重级别

| 级别 | 判定条件 |
|------|---------|
| `critical` | 包含"偏低"或"骤降"关键词的异常 |
| `warning` | 其他所有异常 |

### 响应示例

```json
{
  "status": "ok",
  "anomalies": [
    {
      "session_id": 245,
      "date": "2026-06-03",
      "anchor": "张三",
      "store": "旗舰店",
      "gmv": 5200.00,
      "viewers": 320,
      "conversion": 0.3,
      "duration": 22,
      "flags": [
        "GMV异常偏低(偏离2.5个标准差)",
        "流量骤降(偏离2.1σ)",
        "直播时长过短(<30分钟)"
      ],
      "severity": "critical"
    },
    {
      "session_id": 251,
      "date": "2026-06-04",
      "anchor": "李四",
      "store": "专营店",
      "gmv": 58000.00,
      "viewers": 2800,
      "conversion": 18.5,
      "duration": 240,
      "flags": [
        "转化率超高(18.5%)，请核实"
      ],
      "severity": "warning"
    }
  ],
  "summary": {
    "total_checked": 42,
    "anomaly_count": 5,
    "critical_count": 2,
    "anomaly_rate": 11.9,
    "top_flagged": [
      {"name": "张三", "count": 3},
      {"name": "王五", "count": 1}
    ]
  }
}
```

### 最小数据要求

至少 5 场直播数据。不足时返回:

```json
{
  "status": "insufficient_data",
  "anomalies": [],
  "summary": {"total_checked": 3}
}
```

---

## 5. InsightEngine -- 运营建议引擎

### 接口

```
GET /api/ai/insights/
```

无参数，自动扫描全盘数据生成建议。

### 检测维度

引擎自动检测以下 7 个维度，生成可执行的运营建议:

#### 1. 店铺目标达成 (store)

| 条件 | 优先级 |
|------|--------|
| 30天GMV完成率 < 50% | high |

建议内容: 增加直播场次或调整主播配置。

#### 2. 店铺转化率 (conversion)

| 条件 | 优先级 |
|------|--------|
| 30天平均转化率 < 1% 且场次 >= 5 | medium |

建议内容: 优化选品策略和主播话术。

#### 3. 主播疲劳 (fatigue)

| 条件 | 优先级 |
|------|--------|
| 连续工作天数 >= 6 | high |

建议内容: 安排调休，防止质量下降和流失。

#### 4. 合同到期 (contract)

| 条件 | 优先级 |
|------|--------|
| 合同 30 天内到期 | high |

建议内容: 尽快启动续约沟通。

#### 5. 考勤异常 (attendance)

| 条件 | 优先级 |
|------|--------|
| 近 7 天迟到 >= 2 次 | medium |

建议内容: 进行沟通，避免影响团队纪律。

#### 6. 待审批请假 (leave)

| 条件 | 优先级 |
|------|--------|
| 有 pending 状态的请假申请 | medium |

建议内容: 及时审批以避免排班冲突。

#### 7. GMV 趋势预警 (revenue)

| 条件 | 优先级 |
|------|--------|
| 近 7 天日均 GMV 较之前下降 > 20% | high |

建议内容: 排查原因。

### 响应示例

```json
{
  "status": "ok",
  "recommendations": [
    {
      "priority": "high",
      "category": "fatigue",
      "icon": "😴",
      "title": "李佳琦 已连续工作6天",
      "detail": "过度疲劳会导致直播质量下降和主播流失风险。建议安排调休。",
      "action": "调整排班",
      "employee_id": 5
    },
    {
      "priority": "high",
      "category": "contract",
      "icon": "📋",
      "title": "张三 合同15天后到期",
      "detail": "合同到期日: 2026-06-20。请尽快启动续约沟通。",
      "action": "查看详情",
      "employee_id": 8
    },
    {
      "priority": "high",
      "category": "revenue",
      "icon": "📉",
      "title": "全盘GMV近期下降28%",
      "detail": "近7天日均12.5万，之前日均17.4万。需排查原因。",
      "action": "查看数据驾驶舱"
    },
    {
      "priority": "medium",
      "category": "store",
      "icon": "🏪",
      "title": "快手专营店 目标达成率仅42%",
      "detail": "30天GMV 21.0万，月目标50.0万。建议增加直播场次或调整主播配置。",
      "action": "查看排班",
      "store_id": 3
    },
    {
      "priority": "medium",
      "category": "attendance",
      "icon": "⏰",
      "title": "王五 近7天迟到3次",
      "detail": "频繁迟到影响团队纪律和直播准时开播，建议进行沟通。",
      "action": "查看考勤"
    },
    {
      "priority": "medium",
      "category": "leave",
      "icon": "📝",
      "title": "5条请假申请待审批",
      "detail": "及时审批可避免排班冲突，影响运营安排。",
      "action": "去审批"
    }
  ],
  "summary": {
    "total": 6,
    "high": 3,
    "medium": 3,
    "categories": ["fatigue", "contract", "revenue", "store", "attendance", "leave"]
  }
}
```

建议按优先级排序: `high` > `medium` > `low`。

---

## 6. AnchorMatcher -- 主播店铺匹配

### 接口

```
GET /api/ai/match/?store_id=1
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| store_id | int | 否 | 指定店铺 (不传则返回所有活跃店铺) |

### 算法原理

基于最近 30 天的每个主播-店铺组合数据，计算多维匹配评分:

```
score = min(gmv / 100000, 1) * 40          # GMV 贡献 (权重 40)
      + min(avg_viewers / 5000, 1) * 20    # 流量贡献 (权重 20)
      + min(avg_conversion / 5, 1) * 20    # 转化贡献 (权重 20)
      + min(sessions / 10, 1) * 20         # 稳定性 (权重 20)
```

| 维度 | 归一化基准 | 权重 |
|------|-----------|------|
| GMV | 10 万元满分 | 40% |
| 场均观看 | 5000 人满分 | 20% |
| 转化率 | 5% 满分 | 20% |
| 场次稳定性 | 10 场满分 | 20% |

### 匹配流程

1. 获取所有在职主播和活跃店铺
2. 查询近 30 天所有主播在各店铺的聚合表现
3. 对每个组合计算匹配评分
4. 按店铺分组，取各店铺 Top 5 主播
5. 全局排序取 Top 20 最佳组合

### 响应示例

```json
{
  "status": "ok",
  "matches": [
    {
      "store_id": 1,
      "store_name": "旗舰店",
      "platform": "douyin",
      "top_anchors": [
        {
          "anchor_id": 5,
          "anchor_name": "李佳琦",
          "store_id": 1,
          "store_name": "旗舰店",
          "platform": "douyin",
          "gmv": 850000.00,
          "orders": 3800,
          "sessions": 18,
          "avg_viewers": 8500,
          "avg_conversion": 4.2,
          "score": 88.5
        }
      ],
      "has_data": true
    },
    {
      "store_id": 2,
      "store_name": "美妆专营店",
      "platform": "taobao",
      "top_anchors": [],
      "has_data": false
    }
  ],
  "best_combos": [
    {
      "anchor_id": 5,
      "anchor_name": "李佳琦",
      "store_id": 1,
      "store_name": "旗舰店",
      "platform": "douyin",
      "gmv": 850000.00,
      "orders": 3800,
      "sessions": 18,
      "avg_viewers": 8500,
      "avg_conversion": 4.2,
      "score": 88.5
    }
  ]
}
```

---

## 缓存策略

所有 AI 接口的计算结果均通过 Django 缓存框架缓存，缓存键由接口名称和参数哈希生成:

```
cache_key = "ai:{engine_name}:{md5(sorted_params_json)}"
```

| 引擎 | 缓存时间 | 说明 |
|------|---------|------|
| GMVPredictor | 120 秒 | GMV 趋势短期稳定 |
| SmartScheduler | 120 秒 | 排班推荐日内有效 |
| AnchorProfiler | 180 秒 | 画像变化较慢 |
| AnomalyDetector | 120 秒 | 异常检测需一定时效 |
| InsightEngine | 120 秒 | 建议扫描较重 |
| AnchorMatcher | 180 秒 | 匹配结果较稳定 |

**缓存失效:** 核心业务数据变更时 (创建/更新/删除)，自动清除关联缓存:

```python
invalidate_cache('dashboard', 'daily_gmv', 'store_overview')
```

**生产环境建议:** 将缓存后端从 `LocMemCache` 切换为 `Redis`，以获得持久化和跨进程共享能力。
