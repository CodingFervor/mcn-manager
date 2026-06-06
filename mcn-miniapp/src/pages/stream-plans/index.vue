<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">直播预告</text>
    </view>

    <scroll-view scroll-y class="plan-list">
      <template v-for="(group, idx) in groupedPlans" :key="idx">
        <!-- Calendar-style date header -->
        <view class="date-header">
          <view class="date-badge">
            <text class="date-day">{{ group.day }}</text>
            <text class="date-weekday">{{ group.weekday }}</text>
          </view>
          <text class="date-full">{{ group.fullDate }}</text>
        </view>

        <!-- Plan cards under this date -->
        <view
          v-for="plan in group.plans"
          :key="plan.id"
          class="glass-card plan-card"
        >
          <view class="plan-time">
            <text class="time-text">{{ plan.startTime }}</text>
            <text class="time-sep">-</text>
            <text class="time-text">{{ plan.endTime }}</text>
          </view>
          <view class="plan-info">
            <view class="info-top">
              <text class="store-name">{{ plan.storeName }}</text>
              <text :class="['status-tag', `status-${plan.status}`]">
                {{ statusMap[plan.status] }}
              </text>
            </view>
            <view class="info-meta">
              <text class="meta-item">主播: {{ plan.anchor }}</text>
              <text class="meta-item">运营: {{ plan.operator }}</text>
            </view>
            <text v-if="plan.note" class="plan-note">{{ plan.note }}</text>
          </view>
        </view>
      </template>

      <view v-if="groupedPlans.length === 0" class="empty-tip">
        <text class="tip-text">暂无直播预告</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { StreamPlanAPI } from '@/api'
import { formatDate } from '@/utils/format'

const statusMap = {
  upcoming: '即将开始',
  confirmed: '已确认',
  cancelled: '已取消'
}

const plans = ref([])

const mockPlans = [
  { id: 1, date: '2026-06-06', startTime: '19:00', endTime: '22:00', storeName: '旗舰店A', anchor: '小明', operator: '思思', status: 'confirmed', note: '618专场，主推护肤套盒' },
  { id: 2, date: '2026-06-06', startTime: '14:00', endTime: '16:00', storeName: '品牌店B', anchor: '小红', operator: '大伟', status: 'confirmed', note: '新品首发专场' },
  { id: 3, date: '2026-06-07', startTime: '20:00', endTime: '23:00', storeName: '专卖店C', anchor: '小丽', operator: '思思', status: 'upcoming', note: '美妆教程+带货' },
  { id: 4, date: '2026-06-07', startTime: '10:00', endTime: '12:00', storeName: '旗舰店A', anchor: '小明', operator: '大伟', status: 'upcoming', note: '' },
  { id: 5, date: '2026-06-08', startTime: '19:30', endTime: '22:30', storeName: '旗舰店A', anchor: '小明', operator: '思思', status: 'upcoming', note: '618预热第一波' },
  { id: 6, date: '2026-06-08', startTime: '15:00', endTime: '17:00', storeName: '概念店D', anchor: '小红', operator: '大伟', status: 'upcoming', note: '' },
  { id: 7, date: '2026-06-09', startTime: '20:00', endTime: '23:30', storeName: '旗舰店A', anchor: '小丽', operator: '思思', status: 'upcoming', note: '618预热第二波，主打满减' },
  { id: 8, date: '2026-06-10', startTime: '19:00', endTime: '24:00', storeName: '旗舰店A', anchor: '小明', operator: '思思', note: '618正式大促', status: 'upcoming' }
]

const weekdayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const groupedPlans = computed(() => {
  const groups = {}
  plans.value.forEach(plan => {
    if (!groups[plan.date]) {
      const d = new Date(plan.date)
      groups[plan.date] = {
        day: d.getDate(),
        weekday: weekdayNames[d.getDay()],
        fullDate: plan.date,
        plans: []
      }
    }
    groups[plan.date].plans.push(plan)
  })
  return Object.values(groups).sort((a, b) => a.fullDate.localeCompare(b.fullDate))
})

async function loadData() {
  try {
    const res = await StreamPlanAPI.list()
    plans.value = res.data?.results || res.data || mockPlans
  } catch {
    plans.value = mockPlans
  }
}

onShow(() => {
  loadData()
})

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
}

.page-header {
  padding: 24rpx 32rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.plan-list {
  padding: 0 32rpx;
  height: calc(100vh - 100rpx);
}

.date-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 0 16rpx;
}

.date-badge {
  width: 80rpx;
  height: 80rpx;
  border-radius: $radius-sm;
  background: rgba($neon-purple, 0.2);
  border: 2rpx solid rgba($neon-purple, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.date-day {
  font-size: 32rpx;
  font-weight: 700;
  color: $neon-purple;
  line-height: 1;
}

.date-weekday {
  font-size: 20rpx;
  color: $neon-purple;
}

.date-full {
  font-size: 28rpx;
  color: $text-secondary;
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.plan-card {
  display: flex;
  padding: 24rpx;
  margin-bottom: 16rpx;
}

.plan-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-right: 24rpx;
  margin-right: 24rpx;
  border-right: 2rpx solid rgba(255, 255, 255, 0.06);
  min-width: 80rpx;
}

.time-text {
  font-size: 26rpx;
  font-weight: 600;
  color: $neon-cyan;
}

.time-sep {
  font-size: 22rpx;
  color: $text-muted;
  margin: 4rpx 0;
}

.plan-info {
  flex: 1;
  min-width: 0;
}

.info-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.store-name {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.status-tag {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.status-upcoming {
    background: rgba($neon-yellow, 0.15);
    color: $neon-yellow;
  }
  &.status-confirmed {
    background: rgba($neon-green, 0.15);
    color: $neon-green;
  }
  &.status-cancelled {
    background: rgba($neon-pink, 0.15);
    color: $neon-pink;
  }
}

.info-meta {
  display: flex;
  gap: 24rpx;
  margin-bottom: 8rpx;
}

.meta-item {
  font-size: 24rpx;
  color: $text-secondary;
}

.plan-note {
  font-size: 24rpx;
  color: $text-muted;
}

.empty-tip {
  padding: 80rpx 0;
  text-align: center;
}

.tip-text {
  font-size: 28rpx;
  color: $text-muted;
}
</style>
