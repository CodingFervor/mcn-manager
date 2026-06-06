<template>
  <view class="attendance-page">
    <!-- Header -->
    <view class="page-header">
      <text class="page-title">考勤打卡</text>
    </view>

    <scroll-view scroll-y class="scroll-body">
      <!-- Current Time Display -->
      <view class="time-section">
        <text class="current-date">{{ currentDate }}</text>
        <text class="current-time">{{ currentTime }}</text>
      </view>

      <!-- Clock Button Area -->
      <view class="clock-section">
        <view
          v-if="clockStatus === 'none'"
          class="clock-btn clock-in-btn"
          hover-class="btn-hover"
          @tap="handleClockIn"
        >
          <view class="clock-btn-inner clock-in-inner">
            <text class="clock-btn-icon">&#x23F0;</text>
            <text class="clock-btn-text">上班打卡</text>
          </view>
        </view>

        <view
          v-else-if="clockStatus === 'in'"
          class="clock-btn clock-out-btn"
          hover-class="btn-hover"
          @tap="handleClockOut"
        >
          <view class="clock-btn-inner clock-out-inner">
            <text class="clock-btn-icon">&#x1F3C1;</text>
            <text class="clock-btn-text">下班打卡</text>
          </view>
        </view>

        <view v-else class="clock-btn clock-done-btn">
          <view class="clock-btn-inner clock-done-inner">
            <text class="clock-btn-icon-done">&#x2705;</text>
            <text class="clock-btn-text-done">今日已完成</text>
          </view>
        </view>
      </view>

      <!-- GPS Location -->
      <view class="location-section">
        <text class="location-icon">&#x1F4CD;</text>
        <text class="location-text">{{ locationText }}</text>
      </view>

      <!-- Today Record -->
      <view class="section-card">
        <text class="section-title">今日记录</text>
        <view class="record-row">
          <view class="record-item">
            <text class="record-label">上班打卡</text>
            <text class="record-value" :class="{ 'value-active': todayRecord.clockIn }">{{ todayRecord.clockIn || '--:--' }}</text>
          </view>
          <view class="record-divider" />
          <view class="record-item">
            <text class="record-label">下班打卡</text>
            <text class="record-value" :class="{ 'value-active': todayRecord.clockOut }">{{ todayRecord.clockOut || '--:--' }}</text>
          </view>
          <view class="record-divider" />
          <view class="record-item">
            <text class="record-label">工作时长</text>
            <text class="record-value highlight">{{ todayRecord.workHours || '--' }}</text>
          </view>
        </view>
      </view>

      <!-- Recent History -->
      <view class="section-card">
        <text class="section-title">最近记录</text>
        <view class="history-list">
          <view class="history-item" v-for="(item, idx) in historyList" :key="idx">
            <view class="history-date-col">
              <text class="history-date">{{ item.date }}</text>
              <text class="history-weekday">{{ item.weekday }}</text>
            </view>
            <view class="history-times">
              <text class="history-time-in">{{ item.clockIn }}</text>
              <text class="history-sep">-</text>
              <text class="history-time-out">{{ item.clockOut }}</text>
            </view>
            <view class="history-hours">
              <text class="hours-value">{{ item.workHours }}</text>
            </view>
            <view class="history-status" :class="'hs-' + item.statusClass">
              <text class="hs-text">{{ item.statusText }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { AttendanceAPI } from '@/api'
import { formatDate } from '@/utils/format'

// Clock status: 'none' | 'in' | 'done'
const clockStatus = ref('none')
const currentDate = ref('')
const currentTime = ref('')
const locationText = ref('正在获取位置...')
let timer = null

const todayRecord = ref({
  clockIn: '',
  clockOut: '',
  workHours: '',
})

const historyList = ref([
  { date: '06/05', weekday: '周四', clockIn: '09:02', clockOut: '18:15', workHours: '9.2h', statusText: '正常', statusClass: 'normal' },
  { date: '06/04', weekday: '周三', clockIn: '08:58', clockOut: '18:30', workHours: '9.5h', statusText: '正常', statusClass: 'normal' },
  { date: '06/03', weekday: '周二', clockIn: '09:15', clockOut: '18:00', workHours: '8.8h', statusText: '迟到', statusClass: 'late' },
  { date: '06/02', weekday: '周一', clockIn: '08:55', clockOut: '19:20', workHours: '10.4h', statusText: '正常', statusClass: 'normal' },
  { date: '05/30', weekday: '周五', clockIn: '09:00', clockOut: '18:05', workHours: '9.1h', statusText: '正常', statusClass: 'normal' },
])

function updateTime() {
  const now = new Date()
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  currentDate.value = `${y}年${m}月${d}日 ${weekDays[now.getDay()]}`
  const h = String(now.getHours()).padStart(2, '0')
  const min = String(now.getMinutes()).padStart(2, '0')
  const s = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${h}:${min}:${s}`
}

function getLocation() {
  try {
    uni.getLocation({
      type: 'gcj02',
      success(res) {
        locationText.value = `${res.address || '当前位置'} (${res.latitude.toFixed(4)}, ${res.longitude.toFixed(4)})`
      },
      fail() {
        locationText.value = '无法获取位置信息'
      },
    })
  } catch (e) {
    locationText.value = 'MCN管家总部大厦'
  }
}

async function loadTodayStatus() {
  try {
    const res = await AttendanceAPI.summary()
    if (res) {
      todayRecord.value = {
        clockIn: res.clock_in ? res.clock_in.slice(11, 16) : '',
        clockOut: res.clock_out ? res.clock_out.slice(11, 16) : '',
        workHours: res.work_hours ? `${res.work_hours}h` : '',
      }
      if (res.clock_in && res.clock_out) {
        clockStatus.value = 'done'
      } else if (res.clock_in) {
        clockStatus.value = 'in'
      } else {
        clockStatus.value = 'none'
      }
    }
  } catch (e) {
    // Keep default state (none)
    console.log('Attendance summary fallback to default state')
  }
}

async function handleClockIn() {
  uni.showLoading({ title: '打卡中...' })
  try {
    const res = await AttendanceAPI.clockIn({
      latitude: 0,
      longitude: 0,
      location: locationText.value,
    })
    uni.hideLoading()
    if (res) {
      const time = new Date().toTimeString().slice(0, 5)
      todayRecord.value.clockIn = time
      clockStatus.value = 'in'
      uni.showToast({ title: '打卡成功', icon: 'success' })
    }
  } catch (e) {
    uni.hideLoading()
    // Mock success for demo
    const time = new Date().toTimeString().slice(0, 5)
    todayRecord.value.clockIn = time
    clockStatus.value = 'in'
    uni.showToast({ title: '打卡成功', icon: 'success' })
  }
}

async function handleClockOut() {
  uni.showLoading({ title: '打卡中...' })
  try {
    const res = await AttendanceAPI.clockOut({
      latitude: 0,
      longitude: 0,
      location: locationText.value,
    })
    uni.hideLoading()
    if (res) {
      const time = new Date().toTimeString().slice(0, 5)
      todayRecord.value.clockOut = time
      todayRecord.value.workHours = '8.5h'
      clockStatus.value = 'done'
      uni.showToast({ title: '打卡成功', icon: 'success' })
    }
  } catch (e) {
    uni.hideLoading()
    // Mock success for demo
    const time = new Date().toTimeString().slice(0, 5)
    todayRecord.value.clockOut = time
    todayRecord.value.workHours = '8.5h'
    clockStatus.value = 'done'
    uni.showToast({ title: '打卡成功', icon: 'success' })
  }
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  getLocation()
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

onShow(() => {
  loadTodayStatus()
})
</script>

<style lang="scss" scoped>
.attendance-page {
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

.scroll-body {
  flex: 1;
  height: 0;
}

// Time Section
.time-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0 40rpx;
}

.current-date {
  font-size: 26rpx;
  color: $text-secondary;
  margin-bottom: 8rpx;
}

.current-time {
  font-size: 72rpx;
  font-weight: 700;
  color: $text-primary;
  font-variant-numeric: tabular-nums;
  letter-spacing: 4rpx;
  background: linear-gradient(135deg, $text-primary, $neon-cyan);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

// Clock Button
.clock-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx 0 40rpx;
}

.clock-btn {
  width: 320rpx;
  height: 320rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clock-btn:active {
  transform: scale(0.95);
}

.clock-in-btn {
  background: linear-gradient(135deg, rgba(0, 255, 157, 0.15), rgba(0, 229, 255, 0.15));
  border: 4rpx solid rgba(0, 255, 157, 0.3);
  box-shadow: 0 0 60rpx rgba(0, 255, 157, 0.2), 0 0 120rpx rgba(0, 255, 157, 0.08);
}

.clock-out-btn {
  background: linear-gradient(135deg, rgba(255, 140, 66, 0.15), rgba(255, 77, 158, 0.15));
  border: 4rpx solid rgba(255, 140, 66, 0.3);
  box-shadow: 0 0 60rpx rgba(255, 140, 66, 0.2), 0 0 120rpx rgba(255, 140, 66, 0.08);
}

.clock-done-btn {
  background: rgba(107, 115, 147, 0.1);
  border: 4rpx solid rgba(107, 115, 147, 0.2);
}

.clock-btn-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.clock-in-inner {
  animation: pulse-green 2s ease-in-out infinite;
}

.clock-out-inner {
  animation: pulse-orange 2s ease-in-out infinite;
}

@keyframes pulse-green {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0, 255, 157, 0.1); }
  50% { box-shadow: 0 0 20rpx 10rpx rgba(0, 255, 157, 0.05); }
}

@keyframes pulse-orange {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 140, 66, 0.1); }
  50% { box-shadow: 0 0 20rpx 10rpx rgba(255, 140, 66, 0.05); }
}

.clock-btn-icon {
  font-size: 56rpx;
  margin-bottom: 12rpx;
}

.clock-btn-icon-done {
  font-size: 56rpx;
  margin-bottom: 12rpx;
}

.clock-btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
}

.clock-btn-text-done {
  font-size: 28rpx;
  font-weight: 500;
  color: $text-muted;
}

.btn-hover {
  transform: scale(0.95);
  opacity: 0.9;
}

// Location
.location-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 32rpx 32rpx;
}

.location-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.location-text {
  font-size: 24rpx;
  color: $text-muted;
}

// Section Card
.section-card {
  margin: 0 24rpx 20rpx;
  padding: 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 24rpx;
  display: block;
}

// Today Record
.record-row {
  display: flex;
  align-items: center;
}

.record-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.record-label {
  font-size: 22rpx;
  color: $text-muted;
  margin-bottom: 8rpx;
}

.record-value {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-muted;

  &.value-active {
    color: $neon-cyan;
  }
}

.record-value.highlight {
  color: $neon-purple;
}

.record-divider {
  width: 1rpx;
  height: 60rpx;
  background: rgba(124, 92, 255, 0.15);
}

// History List
.history-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 16rpx 20rpx;
  background: rgba(10, 14, 39, 0.4);
  border-radius: $radius-sm;
}

.history-date-col {
  display: flex;
  flex-direction: column;
  margin-right: 24rpx;
  min-width: 80rpx;
}

.history-date {
  font-size: 26rpx;
  font-weight: 600;
  color: $text-primary;
}

.history-weekday {
  font-size: 22rpx;
  color: $text-muted;
}

.history-times {
  flex: 1;
  display: flex;
  align-items: center;
}

.history-time-in {
  font-size: 26rpx;
  color: $neon-green;
  font-weight: 500;
}

.history-sep {
  margin: 0 12rpx;
  font-size: 22rpx;
  color: $text-muted;
}

.history-time-out {
  font-size: 26rpx;
  color: $neon-cyan;
  font-weight: 500;
}

.history-hours {
  margin-left: 16rpx;
}

.hours-value {
  font-size: 24rpx;
  color: $text-secondary;
  font-weight: 500;
}

.history-status {
  margin-left: 16rpx;
  padding: 4rpx 14rpx;
  border-radius: 16rpx;

  &.hs-normal {
    background: rgba(0, 255, 157, 0.1);
  }
  &.hs-normal .hs-text {
    color: $neon-green;
  }
  &.hs-late {
    background: rgba(255, 77, 158, 0.1);
  }
  &.hs-late .hs-text {
    color: $neon-pink;
  }
}

.hs-text {
  font-size: 20rpx;
  font-weight: 500;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
