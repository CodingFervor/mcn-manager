<template>
  <view class="schedule-page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">排班日历</text>
    </view>

    <!-- Week Selector -->
    <view class="week-selector">
      <view
        class="week-day"
        v-for="(day, idx) in weekDays"
        :key="idx"
        :class="{ active: day.isToday, selected: day.date === selectedDate }"
        @tap="selectDay(day)"
      >
        <text class="week-label">{{ day.label }}</text>
        <text class="week-date" :class="{ 'date-active': day.date === selectedDate }">{{ day.dayNum }}</text>
        <view v-if="day.isToday" class="today-dot" />
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" refresher-enabled :refresher-triggered="refreshing" @refresherrefresh="onRefresh">
      <!-- Schedule List -->
      <view v-if="scheduleList.length > 0" class="schedule-list">
        <view class="schedule-card" v-for="(item, idx) in scheduleList" :key="idx">
          <view class="card-left-accent" :style="{ background: item.accentColor }" />
          <view class="card-body">
            <view class="card-top">
              <text class="card-shift">{{ item.shiftName }}</text>
              <view class="card-status" :class="'tag-' + item.statusClass">
                <text class="tag-text">{{ item.statusText }}</text>
              </view>
            </view>
            <view class="card-row">
              <text class="card-icon">&#x1F3EA;</text>
              <text class="card-store">{{ item.storeName }}</text>
            </view>
            <view class="card-row">
              <text class="card-icon">&#x1F552;</text>
              <text class="card-time">{{ item.startTime }} - {{ item.endTime }}</text>
              <text class="card-duration">{{ item.duration }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Empty State -->
      <view v-else class="empty-state">
        <text class="empty-icon">&#x1F4C5;</text>
        <text class="empty-title">暂无排班</text>
        <text class="empty-desc">{{ selectedDate === todayStr ? '今天没有排班安排，好好休息吧' : '该日期暂无排班安排' }}</text>
      </view>

      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { ScheduleAPI } from '@/api'

const refreshing = ref(false)
const selectedDate = ref('')
const todayStr = ref('')

const weekDays = ref([])

// Mock schedule data mapped by date
const mockSchedules = {
  default: [
    { shiftName: '早班直播', storeName: '旗舰店直播间', startTime: '08:00', endTime: '12:00', duration: '4小时', statusText: '已完成', statusClass: 'completed', accentColor: '#00ff9d' },
    { shiftName: '午间补播', storeName: '万象城店', startTime: '13:00', endTime: '15:00', duration: '2小时', statusText: '待开始', statusClass: 'pending', accentColor: '#7c5cff' },
    { shiftName: '晚间大场', storeName: '线上直播间', startTime: '20:00', endTime: '23:30', duration: '3.5小时', statusText: '待开始', statusClass: 'pending', accentColor: '#00e5ff' },
  ],
  empty: [],
}

const scheduleList = ref([])

function initWeekDays() {
  const now = new Date()
  const dayLabels = ['一', '二', '三', '四', '五', '六', '日']
  const current = new Date(now)
  // Find Monday of current week
  const dayOfWeek = now.getDay() || 7 // Sunday = 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - dayOfWeek + 1)

  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    const dateStr = formatDateStr(d)
    const isToday = dateStr === formatDateStr(now)
    days.push({
      label: dayLabels[i],
      dayNum: d.getDate(),
      date: dateStr,
      isToday,
    })
  }
  weekDays.value = days
  todayStr.value = formatDateStr(now)
  selectedDate.value = todayStr.value
}

function formatDateStr(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function selectDay(day) {
  selectedDate.value = day.date
  loadScheduleForDate(day.date)
}

async function loadScheduleForDate(date) {
  try {
    const res = await ScheduleAPI.list({ date })
    if (res && res.results && res.results.length > 0) {
      scheduleList.value = res.results.map(s => ({
        shiftName: s.shift_name || s.name || '默认班次',
        storeName: s.store_name || '直播间',
        startTime: s.start_time?.slice(11, 16) || '09:00',
        endTime: s.end_time?.slice(11, 16) || '18:00',
        duration: s.duration || '8小时',
        statusText: s.status === 'completed' ? '已完成' : s.status === 'ongoing' ? '进行中' : '待开始',
        statusClass: s.status === 'completed' ? 'completed' : s.status === 'ongoing' ? 'active' : 'pending',
        accentColor: s.status === 'completed' ? '#6b7393' : s.status === 'ongoing' ? '#00ff9d' : '#7c5cff',
      }))
    } else {
      scheduleList.value = []
    }
  } catch (e) {
    // Fallback: use mock data for today, empty for other days
    if (date === todayStr.value) {
      scheduleList.value = [...mockSchedules.default]
    } else {
      scheduleList.value = []
    }
  }
}

onMounted(() => {
  initWeekDays()
})

onShow(() => {
  loadScheduleForDate(selectedDate.value)
})

onPullDownRefresh(async () => {
  refreshing.value = true
  await loadScheduleForDate(selectedDate.value)
  refreshing.value = false
  uni.stopPullDownRefresh()
})

function onRefresh() {
  // handled by refresher
}
</script>

<style lang="scss" scoped>
.schedule-page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: 24rpx 32rpx 16rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

// Week Selector
.week-selector {
  display: flex;
  padding: 16rpx 20rpx;
  background: $bg-secondary;
  margin: 0 24rpx;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
}

.week-day {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 0;
  border-radius: $radius-sm;
  position: relative;
  transition: all 0.2s;

  &.selected {
    background: rgba(124, 92, 255, 0.15);
  }
}

.week-label {
  font-size: 22rpx;
  color: $text-muted;
  margin-bottom: 8rpx;
}

.week-date {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;

  &.date-active {
    color: $neon-purple;
  }
}

.today-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: $neon-purple;
  position: absolute;
  bottom: 8rpx;
}

.scroll-body {
  flex: 1;
  height: 0;
  margin-top: 20rpx;
}

// Schedule Cards
.schedule-list {
  padding: 0 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.schedule-card {
  display: flex;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  overflow: hidden;
}

.card-left-accent {
  width: 8rpx;
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  padding: 24rpx 28rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-shift {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.card-status {
  padding: 4rpx 16rpx;
  border-radius: 20rpx;

  &.tag-active {
    background: rgba(0, 255, 157, 0.12);
  }
  &.tag-active .tag-text {
    color: $neon-green;
  }
  &.tag-pending {
    background: rgba(124, 92, 255, 0.12);
  }
  &.tag-pending .tag-text {
    color: $neon-purple;
  }
  &.tag-completed {
    background: rgba(107, 115, 147, 0.12);
  }
  &.tag-completed .tag-text {
    color: $text-muted;
  }
}

.tag-text {
  font-size: 22rpx;
  font-weight: 500;
}

.card-row {
  display: flex;
  align-items: center;
  margin-bottom: 10rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.card-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.card-store {
  font-size: 26rpx;
  color: $text-secondary;
}

.card-time {
  font-size: 26rpx;
  color: $text-secondary;
}

.card-duration {
  font-size: 22rpx;
  color: $text-muted;
  margin-left: 16rpx;
}

// Empty State
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
