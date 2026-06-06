<template>
  <view class="dashboard-page">
    <!-- Top Greeting -->
    <view class="greeting-section">
      <view class="greeting-left">
        <text class="greeting-hi">Hi, {{ employeeName }}</text>
        <text class="greeting-date">{{ todayDate }}</text>
      </view>
      <view class="greeting-right" @tap="goNotifications">
        <text class="bell-icon">&#x1F514;</text>
        <view v-if="unreadCount > 0" class="badge">
          <text class="badge-text">{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-body" refresher-enabled :refresher-triggered="refreshing" @refresherrefresh="onRefresh">
      <!-- Stat Cards 2x2 -->
      <view class="stat-grid">
        <view class="stat-card" v-for="(stat, idx) in stats" :key="idx">
          <view class="stat-icon-wrap" :style="{ background: stat.bgColor }">
            <text class="stat-icon">{{ stat.icon }}</text>
          </view>
          <text class="stat-value">{{ stat.value }}</text>
          <text class="stat-label">{{ stat.label }}</text>
        </view>
      </view>

      <!-- 7-Day Trend -->
      <view class="section-card">
        <view class="section-header">
          <text class="section-title">7天趋势</text>
          <text class="section-more">GMV (万)</text>
        </view>
        <view class="trend-chart">
          <view class="trend-bar-group" v-for="(item, idx) in trendData" :key="idx">
            <view class="trend-bar-track">
              <view class="trend-bar-fill" :style="{ height: item.percent + '%', background: item.color }" />
            </view>
            <text class="trend-label">{{ item.day }}</text>
            <text class="trend-value">{{ item.value }}</text>
          </view>
        </view>
      </view>

      <!-- Today Schedule -->
      <view class="section-card">
        <view class="section-header">
          <text class="section-title">今日排班</text>
          <text class="section-more" @tap="goSchedule">查看全部 ></text>
        </view>
        <view v-if="todaySchedules.length === 0" class="empty-hint">
          <text class="empty-text">今日暂无排班</text>
        </view>
        <view v-else class="schedule-list">
          <view class="schedule-item" v-for="(item, idx) in todaySchedules" :key="idx">
            <view class="schedule-time-block">
              <text class="schedule-time">{{ item.startTime }}</text>
              <text class="schedule-sep">-</text>
              <text class="schedule-time">{{ item.endTime }}</text>
            </view>
            <view class="schedule-info">
              <text class="schedule-store">{{ item.storeName }}</text>
              <text class="schedule-shift">{{ item.shiftName }}</text>
            </view>
            <view class="schedule-status" :class="'status-' + item.statusClass">
              <text class="status-text">{{ item.statusText }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Latest Notifications -->
      <view class="section-card">
        <view class="section-header">
          <text class="section-title">最新通知</text>
          <text class="section-more" @tap="goNotifications">更多 ></text>
        </view>
        <view v-if="notifications.length === 0" class="empty-hint">
          <text class="empty-text">暂无通知</text>
        </view>
        <view v-else class="notification-list">
          <view class="notification-item" v-for="(item, idx) in notifications" :key="idx">
            <view class="notif-dot" :class="{ unread: !item.isRead }" />
            <view class="notif-content">
              <text class="notif-title">{{ item.title }}</text>
              <text class="notif-desc">{{ item.content }}</text>
              <text class="notif-time">{{ item.time }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Bottom Spacer -->
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { DashboardAPI, ScheduleAPI, NotificationAPI } from '@/api'
import { formatMoney, formatDate } from '@/utils/format'

const authStore = useAuthStore()
const appStore = useAppStore()

const employeeName = ref('同学')
const todayDate = ref('')
const unreadCount = ref(0)
const refreshing = ref(false)

// Mock stat data
const stats = ref([
  { icon: '\u{1F4B0}', label: '今日GMV', value: '¥3.2万', bgColor: 'rgba(124,92,255,0.15)' },
  { icon: '\u{1F4E6}', label: '今日订单', value: '128', bgColor: 'rgba(0,229,255,0.15)' },
  { icon: '\u{2705}', label: '出勤率', value: '95.2%', bgColor: 'rgba(0,255,157,0.15)' },
  { icon: '\u{1F4CB}', label: '待办任务', value: '6', bgColor: 'rgba(255,77,158,0.15)' },
])

// Mock trend data
const trendData = ref([
  { day: '周一', value: '2.1', percent: 42, color: '#7c5cff' },
  { day: '周二', value: '3.5', percent: 70, color: '#9b7cff' },
  { day: '周三', value: '2.8', percent: 56, color: '#7c5cff' },
  { day: '周四', value: '4.2', percent: 84, color: '#00e5ff' },
  { day: '周五', value: '3.1', percent: 62, color: '#9b7cff' },
  { day: '周六', value: '4.8', percent: 96, color: '#00ff9d' },
  { day: '周日', value: '3.2', percent: 64, color: '#7c5cff' },
])

// Mock schedules
const todaySchedules = ref([
  { startTime: '09:00', endTime: '12:00', storeName: '旗舰店直播间', shiftName: '上午场', statusText: '进行中', statusClass: 'active' },
  { startTime: '14:00', endTime: '18:00', storeName: '万象城店', shiftName: '下午场', statusText: '待开始', statusClass: 'pending' },
  { startTime: '20:00', endTime: '23:00', storeName: '线上直播间', shiftName: '晚场', statusText: '待开始', statusClass: 'pending' },
])

// Mock notifications
const notifications = ref([
  { title: '排班通知', content: '明天(周五)您有排班，请准时到场', time: '10分钟前', isRead: false },
  { title: '系统更新', content: 'MCN管家 v2.1 已发布，新增绩效考核模块', time: '2小时前', isRead: false },
  { title: '销售达标', content: '恭喜！本周GMV已达成目标的85%', time: '昨天', isRead: true },
])

function loadDate() {
  const now = new Date()
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const m = now.getMonth() + 1
  const d = now.getDate()
  todayDate.value = `${m}月${d}日 周${weekDays[now.getDay()]}`
}

async function loadDashboard() {
  try {
    const res = await DashboardAPI.overview()
    if (res) {
      stats.value = [
        { icon: '\u{1F4B0}', label: '今日GMV', value: formatMoney(res.today_gmv), bgColor: 'rgba(124,92,255,0.15)' },
        { icon: '\u{1F4E6}', label: '今日订单', value: String(res.today_orders ?? 0), bgColor: 'rgba(0,229,255,0.15)' },
        { icon: '\u{2705}', label: '出勤率', value: `${res.attendance_rate ?? 0}%`, bgColor: 'rgba(0,255,157,0.15)' },
        { icon: '\u{1F4CB}', label: '待办任务', value: String(res.pending_tasks ?? 0), bgColor: 'rgba(255,77,158,0.15)' },
      ]
    }
  } catch (e) {
    // Keep mock data as fallback
    console.log('Dashboard API fallback to mock data')
  }
}

async function loadSchedules() {
  try {
    const res = await ScheduleAPI.today()
    if (res && res.results && res.results.length > 0) {
      todaySchedules.value = res.results.map(s => ({
        startTime: s.start_time?.slice(11, 16) || '09:00',
        endTime: s.end_time?.slice(11, 16) || '18:00',
        storeName: s.store_name || '直播间',
        shiftName: s.shift_name || '默认班次',
        statusText: s.status === 'ongoing' ? '进行中' : s.status === 'completed' ? '已完成' : '待开始',
        statusClass: s.status === 'ongoing' ? 'active' : s.status === 'completed' ? 'completed' : 'pending',
      }))
    }
  } catch (e) {
    console.log('Schedule API fallback to mock data')
  }
}

async function loadNotifications() {
  try {
    const countRes = await NotificationAPI.unreadCount()
    if (countRes) {
      unreadCount.value = countRes.count ?? 0
    }
  } catch (e) {
    unreadCount.value = 2
  }
}

async function loadAll() {
  await Promise.allSettled([
    loadDashboard(),
    loadSchedules(),
    loadNotifications(),
  ])
}

onMounted(() => {
  loadDate()
})

onShow(() => {
  employeeName.value = authStore.employeeName || '同学'
  loadAll()
})

onPullDownRefresh(async () => {
  refreshing.value = true
  await loadAll()
  refreshing.value = false
  uni.stopPullDownRefresh()
})

function onRefresh() {
  // handled by onPullDownRefresh
}

function goSchedule() {
  uni.switchTab({ url: '/pages/schedule/index' })
}

function goNotifications() {
  uni.navigateTo({ url: '/pages/notifications/index' })
}
</script>

<style lang="scss" scoped>
.dashboard-page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.greeting-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx 20rpx;
  background: linear-gradient(180deg, rgba(124, 92, 255, 0.08) 0%, transparent 100%);
}

.greeting-left {
  display: flex;
  flex-direction: column;
}

.greeting-hi {
  font-size: 38rpx;
  font-weight: 700;
  color: $text-primary;
}

.greeting-date {
  font-size: 26rpx;
  color: $text-secondary;
  margin-top: 4rpx;
}

.greeting-right {
  position: relative;
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bell-icon {
  font-size: 44rpx;
}

.badge {
  position: absolute;
  top: 4rpx;
  right: 0;
  min-width: 32rpx;
  height: 32rpx;
  border-radius: 16rpx;
  background: $neon-pink;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.badge-text {
  font-size: 20rpx;
  color: #fff;
  font-weight: 600;
}

.scroll-body {
  flex: 1;
  height: 0;
}

// Stat Grid
.stat-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 16rpx 24rpx;
  gap: 20rpx;
}

.stat-card {
  width: calc(50% - 10rpx);
  padding: 28rpx 24rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80rpx;
  height: 80rpx;
  background: radial-gradient(circle, rgba(124, 92, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

.stat-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  border-radius: $radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.stat-icon {
  font-size: 30rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4rpx;
}

.stat-label {
  font-size: 24rpx;
  color: $text-muted;
}

// Section Card
.section-card {
  margin: 12rpx 24rpx 0;
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.section-more {
  font-size: 24rpx;
  color: $text-muted;
}

// Trend Chart
.trend-chart {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 240rpx;
  padding: 0 8rpx;
}

.trend-bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.trend-bar-track {
  width: 32rpx;
  height: 180rpx;
  background: rgba(124, 92, 255, 0.08);
  border-radius: 16rpx;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.trend-bar-fill {
  width: 100%;
  border-radius: 16rpx;
  transition: height 0.5s ease;
  min-height: 16rpx;
}

.trend-label {
  font-size: 22rpx;
  color: $text-muted;
  margin-top: 10rpx;
}

.trend-value {
  font-size: 20rpx;
  color: $text-secondary;
  margin-top: 2rpx;
}

// Schedule List
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.schedule-item {
  display: flex;
  align-items: center;
  padding: 20rpx 24rpx;
  background: rgba(10, 14, 39, 0.5);
  border-radius: $radius-sm;
  border: 1rpx solid rgba(124, 92, 255, 0.1);
}

.schedule-time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-right: 24rpx;
  border-right: 1rpx solid rgba(124, 92, 255, 0.15);
  min-width: 90rpx;
}

.schedule-time {
  font-size: 24rpx;
  font-weight: 600;
  color: $neon-cyan;
}

.schedule-sep {
  font-size: 20rpx;
  color: $text-muted;
  line-height: 1;
}

.schedule-info {
  flex: 1;
  padding-left: 24rpx;
  display: flex;
  flex-direction: column;
}

.schedule-store {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
}

.schedule-shift {
  font-size: 24rpx;
  color: $text-secondary;
  margin-top: 4rpx;
}

.schedule-status {
  padding: 6rpx 16rpx;
  border-radius: 20rpx;

  &.status-active {
    background: rgba(0, 255, 157, 0.12);
  }
  &.status-active .status-text {
    color: $neon-green;
  }
  &.status-pending {
    background: rgba(124, 92, 255, 0.12);
  }
  &.status-pending .status-text {
    color: $neon-purple;
  }
  &.status-completed {
    background: rgba(107, 115, 147, 0.12);
  }
  &.status-completed .status-text {
    color: $text-muted;
  }
}

.status-text {
  font-size: 22rpx;
  font-weight: 500;
}

// Notification List
.notification-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.notification-item {
  display: flex;
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(124, 92, 255, 0.08);

  &:last-child {
    border-bottom: none;
  }
}

.notif-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: $text-muted;
  margin-top: 12rpx;
  margin-right: 20rpx;
  flex-shrink: 0;

  &.unread {
    background: $neon-purple;
    box-shadow: 0 0 12rpx rgba(124, 92, 255, 0.4);
  }
}

.notif-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.notif-title {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-primary;
  margin-bottom: 6rpx;
}

.notif-desc {
  font-size: 24rpx;
  color: $text-secondary;
  line-height: 1.5;
  margin-bottom: 8rpx;
}

.notif-time {
  font-size: 22rpx;
  color: $text-muted;
}

.empty-hint {
  padding: 40rpx 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  font-size: 26rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
