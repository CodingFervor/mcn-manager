# MCN AI Engine Technical Document

> Version: 1.0 | Pure algorithm engine, no external AI API dependencies | Based on Django ORM + Statistical Analysis

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [GMVPredictor -- GMV Prediction Engine](#1-gmvpredictor----gmv-prediction-engine)
- [SmartScheduler -- Smart Scheduling Recommendation](#2-smartscheduler----smart-scheduling-recommendation)
- [AnchorProfiler -- Anchor Profile Analysis](#3-anchorprofiler----anchor-profile-analysis)
- [AnomalyDetector -- Anomaly Data Detection](#4-anomalydetector----anomaly-data-detection)
- [InsightEngine -- Operations Insight Engine](#5-insightengine----operations-insight-engine)
- [AnchorMatcher -- Anchor-Store Matching](#6-anchormatcher----anchor-store-matching)
- [Caching Strategy](#caching-strategy)

---

## Architecture Overview

The MCN AI Engine contains 6 independent intelligent engines, all implemented based on historical data statistical analysis and rule engines, with no dependency on any external AI services.

```
                    +-------------------+
                    |   AIViewSet       |
                    |   (API Entry)     |
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

### Common Utility Functions

| Function | Purpose |
|------|------|
| `_linear_regression(xs, ys)` | Least-squares linear regression, returns slope, intercept, R-squared |
| `_moving_average(data, window)` | Sliding window moving average |
| `_z_score(value, mean, std)` | Standard Z-Score calculation |
| `_confidence_level(r2, n)` | Confidence level assessment based on R-squared and sample size |
| `_risk_label(r2, n, slope_pct)` | Risk label generation |

---

## 1. GMVPredictor -- GMV Prediction Engine

### Endpoint

```
GET /api/ai/predict/?days=7&store_id=1&employee_id=5
```

| Parameter | Type | Range | Description |
|------|------|------|------|
| days | int | 1 - 30 | Number of days to predict (default 7) |
| store_id | int | Optional | Filter by store |
| employee_id | int | Optional | Filter by anchor |

### Algorithm

Uses a **Linear Regression + Moving Average + Seasonality Adjustment** three-layer fusion model:

#### Step 1: Linear Regression Fitting

For daily GMV data over the past N days, fit a linear regression model using least squares:

```
slope     = (n * Sum(xi*yi) - Sum(xi)*Sum(yi)) / (n * Sum(xi^2) - Sum(xi)^2)
intercept = (Sum(yi) - slope * Sum(xi)) / n
```

Goodness of fit (R-squared):

```
R^2 = 1 - SS_res / SS_tot
  SS_res = Sum((yi - (slope*xi + intercept))^2)
  SS_tot = Sum((yi - y_mean)^2)
```

#### Step 2: Seasonality Factor

Calculate adjustment factor by day of week:

```
weekday_factor(w) = average_gmv_for_weekday_w / global_average_gmv
```

#### Step 3: Three-Layer Fusion

```
base    = slope * (N + i - 1) + intercept          # Linear regression baseline
blended = base * 0.40 + MA7 * 0.35 + MA14 * 0.25   # Fuse with moving averages
predicted = max(0, blended * weekday_factor(w))     # Seasonality adjustment
```

### Confidence Assessment

| Level | Condition |
|------|------|
| `high` | R^2 > 0.7 and data points >= 7 |
| `medium` | R^2 > 0.4 |
| `low` | All other cases |

### Risk Labels

| Label | Condition | Level |
|------|------|------|
| Insufficient data | Samples < 5 days | warning |
| Downward trend | Period slope < -15% | danger |
| Slight decline | Period slope < -5% | warning |
| High volatility | R^2 < 0.3 | warning |
| Good trend | All other cases | success |

### Response Example

```json
{
  "status": "ok",
  "predictions": [
    {
      "date": "2026-06-06",
      "weekday": "Sat",
      "predicted_gmv": 62850.75,
      "confidence": 72.3
    },
    {
      "date": "2026-06-07",
      "weekday": "Sun",
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
    "risk": "Good trend",
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

### Minimum Data Requirement

At least 3 days of historical data. When insufficient, returns:

```json
{
  "status": "insufficient_data",
  "message": "Insufficient historical data (only 2 days), at least 3 days required",
  "predictions": [],
  "confidence": "low"
}
```

---

## 2. SmartScheduler -- Smart Scheduling Recommendation

### Endpoint

```
GET /api/ai/schedule/?date=2026-06-06&store_id=1
```

| Parameter | Type | Description |
|------|------|------|
| date | date | Target date (default: tomorrow) |
| store_id | int | Filter by store (optional) |

### Algorithm

Uses a **Greedy Matching + Multi-Factor Scoring** strategy: for each shift, rank candidates by composite score in descending order and assign the best match.

#### Scoring Formula

```
final_score = base_score * fatigue_penalty * late_penalty
```

#### base_score Calculation (0-100)

```
base_score = min(avg_gmv / 50000, 1) * 40      # GMV contribution (weight 40)
           + min(avg_viewers / 5000, 1) * 30    # Traffic contribution (weight 30)
           + 30                                   # Base score
           + time_bonus                           # Time slot match bonus (up to 20)
```

**Time Slot Match Bonus:**

```
time_bonus = (anchor's go-live count near the shift time / total go-live count) * 20
```

Matching condition: the difference between the anchor's historical go-live time and shift start time is <= 2 hours.

#### Fatigue Penalty

| Consecutive Work Days | Penalty Factor |
|------------|---------|
| >= 5 days | x 0.3 (strongly recommend rest) |
| >= 3 days | x 0.7 |
| < 3 days | x 1.0 |

#### Late Penalty

```
late_penalty = 1 - late_rate * 0.5
```

Higher late rate in the past 14 days results in greater penalty.

### Matching Process

1. Retrieve all active anchors and shift templates
2. Calculate performance score for each anchor on each shift
3. Retrieve existing schedules (exclude already-scheduled anchors)
4. Retrieve late rate for the past 14 days
5. Retrieve consecutive work days
6. Greedy assignment: iterate through shifts, assign the highest-scoring unassigned anchor to each

### Response Example

```json
{
  "status": "ok",
  "target_date": "2026-06-06",
  "recommendations": [
    {
      "shift_id": 1,
      "shift_name": "Morning Shift",
      "shift_time": "08:00-14:00",
      "candidates": [
        {
          "anchor_id": 5,
          "anchor_name": "Li Jiaqi",
          "score": 85.2,
          "consecutive_days": 0,
          "late_rate": 5.0,
          "reason": "Excellent historical performance, well-rested"
        },
        {
          "anchor_id": 8,
          "anchor_name": "Viya",
          "score": 72.1,
          "consecutive_days": 2,
          "late_rate": 0.0,
          "reason": "Stable performance"
        }
      ]
    },
    {
      "shift_id": 2,
      "shift_name": "Evening Shift",
      "shift_time": "18:00-24:00",
      "candidates": [
        {
          "anchor_id": 12,
          "anchor_name": "Zhang San",
          "score": 25.5,
          "consecutive_days": 5,
          "late_rate": 15.0,
          "reason": "Excellent historical performance, overworked consecutive days recommend rest, high late rate"
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

### Recommendation Reason Generation Rules

| Condition | Generated Text |
|------|---------|
| score >= 80 | "Excellent historical performance" |
| score >= 60 | "Stable performance" |
| consecutive >= 5 | "Overworked consecutive days recommend rest" |
| consecutive == 0 | "Well-rested" |
| late_rate > 20% | "High late rate" |
| Default | "Available for scheduling" |

---

## 3. AnchorProfiler -- Anchor Profile Analysis

### Endpoint

```
GET /api/ai/anchor/?employee_id=5
```

| Parameter | Type | Required | Description |
|------|------|------|------|
| employee_id | int | Yes | Anchor employee ID |

### Five-Dimensional Competency Model

Based on the last 30 days of live streaming data, quantifies anchor capability across 5 dimensions:

#### Sales Power (sales)

```
sales = clamp(50 + Z-Score(gmv_30d, global_gmv_mean, global_gmv_std) * 15, 20, 100)
```

Maps the anchor's 30-day GMV to the 20-100 range using Z-Score standardization against the mean and standard deviation of all anchors across the platform.

#### Traffic Power (traffic)

```
traffic = clamp(min(avg_viewers / 100, 1) * 80 + 20, 20, 100)
```

Linear mapping based on average viewers per session; every 100 viewers corresponds to 80 points.

#### Conversion Power (conversion)

```
conversion = clamp(min(avg_conversion / 5, 1) * 80 + 20, 20, 100)
```

Linear mapping based on average conversion rate; 5% maps to a full score of 100.

#### Stability (stability)

```
stability = clamp(attendance_rate * 0.5 + min(sessions / 20, 1) * 50, 20, 100)
```

Composite assessment of attendance rate and streaming frequency stability.

#### Growth (growth)

```
growth = clamp(50 + gmv_trend_15d * 0.5, 20, 100)
```

Based on the month-over-month GMV growth rate comparing the recent half-month to the prior half-month.

#### Overall Score

```
overall = (sales + traffic + conversion + stability + growth) / 5
```

### Trend Comparison Logic

The last 30 days are split into two 15-day periods:

```
gmv_trend = (recent_15d_gmv - earlier_15d_gmv) / earlier_15d_gmv * 100
```

| Trend | Direction |
|------|---------|
| > +5% | `up` |
| -5% ~ +5% | `stable` |
| < -5% | `down` |

### AI Insight Rules

The system automatically generates actionable insight suggestions based on the anchor's metrics:

| Condition | Type | Insight Text |
|------|------|---------|
| GMV growth > 20% | success | "GMV grew {trend}% in the last half-month, currently on an upward trend" |
| GMV decline > 20% | danger | "GMV declined {trend}% in the last half-month, recommend investigating the cause" |
| Conversion rate > 3% | success | "Conversion rate {conv}% is above average, strong sales capability" |
| Conversion rate < 1% | warning | "Conversion rate is only {conv}%, recommend optimizing sales pitch and product selection" |
| Attendance rate < 80% | danger | "Attendance rate {rate}% is below normal, affects scheduling stability" |
| 30-day sessions >= 25 | warning | "30-day live sessions: {sessions}, ensure adequate rest" |
| Avg viewers > 5000 | success | "Average viewers: {viewers}, outstanding traffic acquisition ability" |
| High avg GMV per session | success | "Average GMV per session: {avg}, high sales efficiency" |
| Default | info | "Data performance is stable, keep it up" |

### Response Example

```json
{
  "status": "ok",
  "anchor": {
    "id": 5,
    "name": "Li Jiaqi",
    "nickname": "JiaqiLJQ",
    "level": "Gold",
    "fans": 3500000,
    "stores": ["Flagship Store", "Beauty Specialty Store"]
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
    {"name": "Flagship Store", "platform": "douyin", "gmv": 850000.00},
    {"name": "Beauty Specialty Store", "platform": "taobao", "gmv": 430000.00}
  ],
  "insights": [
    {"type": "success", "icon": "📈", "text": "GMV grew 13% in the last half-month, currently on an upward trend"},
    {"type": "success", "icon": "🎯", "text": "Conversion rate 3.8% is above average, strong sales capability"},
    {"type": "success", "icon": "👀", "text": "Average viewers 8500, outstanding traffic acquisition ability"}
  ]
}
```

---

## 4. AnomalyDetector -- Anomaly Data Detection

### Endpoint

```
GET /api/ai/anomaly/?days=7
```

| Parameter | Type | Range | Description |
|------|------|------|------|
| days | int | 1 - 30 | Detection period in days (default 7) |

### Algorithm

Uses a dual detection mechanism: **Z-Score Statistical Detection + Business Rule Engine**.

#### Z-Score Statistical Detection

For all live sessions within the specified time range, calculate global mean and standard deviation across three dimensions: GMV, average viewers, and conversion rate:

```
z = (value - mean) / std
```

| Detection Dimension | Threshold | Anomaly Determination |
|---------|------|---------|
| GMV | z < -2 | "GMV abnormally low (deviates {z} standard deviations)" |
| GMV | z > 2 | "GMV abnormally high (exceeds {z} standard deviations)" |
| Avg viewers | z < -2 | "Traffic drop (deviates {z} sigma)" |
| Conversion rate | z < -1.5 | "Conversion rate abnormally low ({value}%)" |

#### Business Rule Engine

| Rule | Trigger Condition | Description |
|------|---------|------|
| Too short | duration < 30 min | Possibly an abnormal stream start |
| Data contradiction | GMV > 0 and orders == 0 | Data entry may be incorrect |
| Extremely high conversion | conversion > 15% | Requires manual verification |
| Overly long stream | duration > 480 min | Fatigue risk warning |

#### Severity Levels

| Level | Determination Condition |
|------|---------|
| `critical` | Anomalies containing "abnormally low" or "drop" keywords |
| `warning` | All other anomalies |

### Response Example

```json
{
  "status": "ok",
  "anomalies": [
    {
      "session_id": 245,
      "date": "2026-06-03",
      "anchor": "Zhang San",
      "store": "Flagship Store",
      "gmv": 5200.00,
      "viewers": 320,
      "conversion": 0.3,
      "duration": 22,
      "flags": [
        "GMV abnormally low (deviates 2.5 standard deviations)",
        "Traffic drop (deviates 2.1 sigma)",
        "Stream duration too short (< 30 minutes)"
      ],
      "severity": "critical"
    },
    {
      "session_id": 251,
      "date": "2026-06-04",
      "anchor": "Li Si",
      "store": "Specialty Store",
      "gmv": 58000.00,
      "viewers": 2800,
      "conversion": 18.5,
      "duration": 240,
      "flags": [
        "Extremely high conversion rate (18.5%), please verify"
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
      {"name": "Zhang San", "count": 3},
      {"name": "Wang Wu", "count": 1}
    ]
  }
}
```

### Minimum Data Requirement

At least 5 live session records. When insufficient, returns:

```json
{
  "status": "insufficient_data",
  "anomalies": [],
  "summary": {"total_checked": 3}
}
```

---

## 5. InsightEngine -- Operations Insight Engine

### Endpoint

```
GET /api/ai/insights/
```

No parameters. Automatically scans all data to generate recommendations.

### Detection Dimensions

The engine automatically detects the following 7 dimensions and generates actionable operational recommendations:

#### 1. Store Target Achievement (store)

| Condition | Priority |
|------|--------|
| 30-day GMV completion rate < 50% | high |

Recommendation: Increase live session count or adjust anchor allocation.

#### 2. Store Conversion Rate (conversion)

| Condition | Priority |
|------|--------|
| 30-day avg conversion rate < 1% and sessions >= 5 | medium |

Recommendation: Optimize product selection strategy and anchor sales pitch.

#### 3. Anchor Fatigue (fatigue)

| Condition | Priority |
|------|--------|
| Consecutive work days >= 6 | high |

Recommendation: Schedule rest days to prevent quality decline and attrition.

#### 4. Contract Expiration (contract)

| Condition | Priority |
|------|--------|
| Contract expires within 30 days | high |

Recommendation: Initiate renewal discussions as soon as possible.

#### 5. Attendance Anomalies (attendance)

| Condition | Priority |
|------|--------|
| Late arrivals >= 2 times in the past 7 days | medium |

Recommendation: Have a discussion to prevent impact on team discipline.

#### 6. Pending Leave Approvals (leave)

| Condition | Priority |
|------|--------|
| Leave requests in pending status exist | medium |

Recommendation: Approve promptly to avoid scheduling conflicts.

#### 7. GMV Trend Warning (revenue)

| Condition | Priority |
|------|--------|
| Daily avg GMV over the past 7 days declined > 20% compared to prior period | high |

Recommendation: Investigate the cause.

### Response Example

```json
{
  "status": "ok",
  "recommendations": [
    {
      "priority": "high",
      "category": "fatigue",
      "icon": "😴",
      "title": "Li Jiaqi has been working 6 consecutive days",
      "detail": "Overwork leads to declining stream quality and risk of anchor turnover. Recommend scheduling rest.",
      "action": "Adjust Schedule",
      "employee_id": 5
    },
    {
      "priority": "high",
      "category": "contract",
      "icon": "📋",
      "title": "Zhang San's contract expires in 15 days",
      "detail": "Contract expiration date: 2026-06-20. Please initiate renewal discussions as soon as possible.",
      "action": "View Details",
      "employee_id": 8
    },
    {
      "priority": "high",
      "category": "revenue",
      "icon": "📉",
      "title": "Overall GMV declined 28% recently",
      "detail": "Last 7 days daily avg 125K, prior daily avg 174K. Need to investigate the cause.",
      "action": "View Dashboard"
    },
    {
      "priority": "medium",
      "category": "store",
      "icon": "🏪",
      "title": "Kuaishou Specialty Store target achievement rate only 42%",
      "detail": "30-day GMV 210K, monthly target 500K. Recommend increasing live sessions or adjusting anchor allocation.",
      "action": "View Schedule",
      "store_id": 3
    },
    {
      "priority": "medium",
      "category": "attendance",
      "icon": "⏰",
      "title": "Wang Wu late 3 times in the past 7 days",
      "detail": "Frequent lateness affects team discipline and timely stream start. Recommend a discussion.",
      "action": "View Attendance"
    },
    {
      "priority": "medium",
      "category": "leave",
      "icon": "📝",
      "title": "5 leave requests pending approval",
      "detail": "Timely approval avoids scheduling conflicts that affect operations.",
      "action": "Review Requests"
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

Recommendations are sorted by priority: `high` > `medium` > `low`.

---

## 6. AnchorMatcher -- Anchor-Store Matching

### Endpoint

```
GET /api/ai/match/?store_id=1
```

| Parameter | Type | Required | Description |
|------|------|------|------|
| store_id | int | No | Specify store (if omitted, returns all active stores) |

### Algorithm

Based on the last 30 days of data for each anchor-store combination, calculates a multi-dimensional match score:

```
score = min(gmv / 100000, 1) * 40          # GMV contribution (weight 40)
      + min(avg_viewers / 5000, 1) * 20    # Traffic contribution (weight 20)
      + min(avg_conversion / 5, 1) * 20    # Conversion contribution (weight 20)
      + min(sessions / 10, 1) * 20         # Stability (weight 20)
```

| Dimension | Normalization Baseline | Weight |
|------|-----------|------|
| GMV | 100K for full score | 40% |
| Avg viewers | 5000 for full score | 20% |
| Conversion rate | 5% for full score | 20% |
| Session stability | 10 sessions for full score | 20% |

### Matching Process

1. Retrieve all active anchors and active stores
2. Query aggregated performance for all anchors across each store in the past 30 days
3. Calculate match score for each combination
4. Group by store, take Top 5 anchors for each store
5. Globally sort and take Top 20 best combinations

### Response Example

```json
{
  "status": "ok",
  "matches": [
    {
      "store_id": 1,
      "store_name": "Flagship Store",
      "platform": "douyin",
      "top_anchors": [
        {
          "anchor_id": 5,
          "anchor_name": "Li Jiaqi",
          "store_id": 1,
          "store_name": "Flagship Store",
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
      "store_name": "Beauty Specialty Store",
      "platform": "taobao",
      "top_anchors": [],
      "has_data": false
    }
  ],
  "best_combos": [
    {
      "anchor_id": 5,
      "anchor_name": "Li Jiaqi",
      "store_id": 1,
      "store_name": "Flagship Store",
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

## Caching Strategy

All AI engine computation results are cached through the Django caching framework. Cache keys are generated from the engine name and a hash of the parameters:

```
cache_key = "ai:{engine_name}:{md5(sorted_params_json)}"
```

| Engine | Cache Duration | Rationale |
|------|---------|------|
| GMVPredictor | 120 seconds | GMV trends are stable in the short term |
| SmartScheduler | 120 seconds | Scheduling recommendations are valid within the day |
| AnchorProfiler | 180 seconds | Profile changes are relatively slow |
| AnomalyDetector | 120 seconds | Anomaly detection requires timeliness |
| InsightEngine | 120 seconds | Insight scanning is computationally heavy |
| AnchorMatcher | 180 seconds | Match results are relatively stable |

**Cache Invalidation:** When core business data changes (create/update/delete), related caches are automatically cleared:

```python
invalidate_cache('dashboard', 'daily_gmv', 'store_overview')
```

**Production Recommendation:** Switch the cache backend from `LocMemCache` to `Redis` for persistence and cross-process sharing.
