<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">请假申请</text>
    </view>

    <!-- New Leave Form -->
    <view class="glass-card form-card">
      <view class="card-header">
        <text class="card-title">新建请假</text>
        <view class="card-underline"></view>
      </view>

      <view class="form-body">
        <view class="form-item">
          <text class="form-label">请假类型</text>
          <picker :range="leaveTypes" @change="onTypeChange">
            <view class="form-picker">
              <text class="picker-text" :class="{ placeholder: !form.type }">
                {{ form.type || '请选择请假类型' }}
              </text>
              <text class="picker-arrow">></text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">开始日期</text>
          <picker mode="date" @change="onStartDateChange">
            <view class="form-picker">
              <text class="picker-text" :class="{ placeholder: !form.startDate }">
                {{ form.startDate || '请选择开始日期' }}
              </text>
              <text class="picker-arrow">></text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">结束日期</text>
          <picker mode="date" @change="onEndDateChange">
            <view class="form-picker">
              <text class="picker-text" :class="{ placeholder: !form.endDate }">
                {{ form.endDate || '请选择结束日期' }}
              </text>
              <text class="picker-arrow">></text>
            </view>
          </picker>
        </view>

        <view v-if="form.startDate && form.endDate" class="form-item">
          <text class="days-hint">共 {{ calcDays }} 天</text>
        </view>

        <view class="form-item">
          <text class="form-label">请假事由</text>
          <textarea
            v-model="form.reason"
            placeholder="请简要说明请假原因"
            placeholder-class="placeholder"
            class="form-textarea"
            :maxlength="200"
          />
        </view>

        <button class="btn-submit" @tap="submitLeave">提交申请</button>
      </view>
    </view>

    <!-- Leave Records -->
    <view class="section-header">
      <text class="section-title">请假记录</text>
      <text class="section-count">{{ records.length }} 条</text>
    </view>

    <scroll-view scroll-y class="record-list">
      <view
        v-for="item in records"
        :key="item.id"
        class="record-card"
      >
        <view class="record-top">
          <view class="record-type-badge" :class="'badge-' + item.typeKey">
            <text class="badge-text">{{ item.type }}</text>
          </view>
          <view class="record-status" :class="'ls-' + item.status">
            <text class="ls-text">{{ getStatusText(item.status) }}</text>
          </view>
        </view>
        <view class="record-dates">
          <text class="date-range">{{ item.startDate }} ~ {{ item.endDate }}</text>
          <text class="date-days">{{ item.days }}天</text>
        </view>
        <text class="record-reason">{{ item.reason }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { getStatusText } from '@/utils/format'

const leaveTypes = ['年假', '病假', '事假', '调休']

const form = ref({
  type: '',
  startDate: '',
  endDate: '',
  reason: '',
})

const calcDays = computed(() => {
  if (!form.value.startDate || !form.value.endDate) return 0
  const start = new Date(form.value.startDate)
  const end = new Date(form.value.endDate)
  const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
  return diff > 0 ? diff : 0
})

const records = ref([
  {
    id: 1,
    type: '年假',
    typeKey: 'annual',
    startDate: '2025-06-10',
    endDate: '2025-06-11',
    days: 2,
    reason: '家庭聚会，需要回老家一趟',
    status: 'approved',
  },
  {
    id: 2,
    type: '病假',
    typeKey: 'sick',
    startDate: '2025-06-03',
    endDate: '2025-06-03',
    days: 1,
    reason: '感冒发烧，需要休息一天',
    status: 'approved',
  },
  {
    id: 3,
    type: '事假',
    typeKey: 'personal',
    startDate: '2025-06-15',
    endDate: '2025-06-15',
    days: 1,
    reason: '需要去银行办理个人业务',
    status: 'pending',
  },
  {
    id: 4,
    type: '调休',
    typeKey: 'compensatory',
    startDate: '2025-05-28',
    endDate: '2025-05-28',
    days: 1,
    reason: '上周六加班调休',
    status: 'approved',
  },
  {
    id: 5,
    type: '年假',
    typeKey: 'annual',
    startDate: '2025-05-01',
    endDate: '2025-05-03',
    days: 3,
    reason: '五一假期延长休假',
    status: 'approved',
  },
  {
    id: 6,
    type: '事假',
    typeKey: 'personal',
    startDate: '2025-04-20',
    endDate: '2025-04-20',
    days: 1,
    reason: '家中有急事需要处理',
    status: 'rejected',
  },
])

function onTypeChange(e) {
  form.value.type = leaveTypes[e.detail.value]
}

function onStartDateChange(e) {
  form.value.startDate = e.detail.value
}

function onEndDateChange(e) {
  form.value.endDate = e.detail.value
}

function submitLeave() {
  const f = form.value
  if (!f.type) return uni.showToast({ title: '请选择请假类型', icon: 'none' })
  if (!f.startDate) return uni.showToast({ title: '请选择开始日期', icon: 'none' })
  if (!f.endDate) return uni.showToast({ title: '请选择结束日期', icon: 'none' })
  if (!f.reason) return uni.showToast({ title: '请填写事由', icon: 'none' })

  const typeKeyMap = { '年假': 'annual', '病假': 'sick', '事假': 'personal', '调休': 'compensatory' }

  records.value.unshift({
    id: Date.now(),
    type: f.type,
    typeKey: typeKeyMap[f.type],
    startDate: f.startDate,
    endDate: f.endDate,
    days: calcDays.value,
    reason: f.reason,
    status: 'pending',
  })

  form.value = { type: '', startDate: '', endDate: '', reason: '' }
  uni.showToast({ title: '提交成功', icon: 'success' })
}

onPullDownRefresh(() => {
  setTimeout(() => {
    uni.stopPullDownRefresh()
  }, 1000)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 20rpx 24rpx;
}

.page-header {
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
}

.glass-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 28rpx;
  backdrop-filter: blur(20px);
}

.card-header {
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 12rpx;
}

.card-underline {
  width: 60rpx;
  height: 4rpx;
  border-radius: 2rpx;
  background: linear-gradient(90deg, $neon-purple, $neon-pink);
  box-shadow: 0 0 10rpx rgba($neon-purple, 0.4);
}

.form-item {
  margin-bottom: 24rpx;
}

.form-label {
  font-size: 26rpx;
  color: $text-secondary;
  display: block;
  margin-bottom: 12rpx;
}

.form-picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1rpx solid $border-glow;
  border-radius: $radius-sm;
  padding: 20rpx 24rpx;
}

.picker-text {
  font-size: 28rpx;
  color: $text-primary;

  &.placeholder {
    color: $text-muted;
  }
}

.picker-arrow {
  font-size: 24rpx;
  color: $text-muted;
}

.days-hint {
  font-size: 26rpx;
  color: $neon-cyan;
  background: rgba($neon-cyan, 0.1);
  padding: 8rpx 20rpx;
  border-radius: 8rpx;
  border: 1rpx solid rgba($neon-cyan, 0.2);
}

.form-textarea {
  width: 100%;
  height: 160rpx;
  background: rgba(255, 255, 255, 0.04);
  border: 1rpx solid $border-glow;
  border-radius: $radius-sm;
  padding: 20rpx 24rpx;
  font-size: 26rpx;
  color: $text-primary;
  box-sizing: border-box;
}

.placeholder {
  color: $text-muted;
}

.btn-submit {
  background: linear-gradient(135deg, $neon-purple, $neon-pink);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: $radius-sm;
  margin-top: 12rpx;
  border: none;
  box-shadow: 0 0 24rpx rgba($neon-purple, 0.3);

  &::after {
    border: none;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 32rpx 8rpx 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.section-count {
  font-size: 24rpx;
  color: $text-muted;
}

.record-list {
  height: 600rpx;
}

.record-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 24rpx;
  margin-bottom: 16rpx;
  backdrop-filter: blur(20px);
}

.record-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.record-type-badge {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  border: 1rpx solid;
}

.badge-annual {
  background: rgba($neon-purple, 0.15);
  border-color: rgba($neon-purple, 0.4);
}

.badge-sick {
  background: rgba($neon-pink, 0.15);
  border-color: rgba($neon-pink, 0.4);
}

.badge-personal {
  background: rgba($neon-yellow, 0.15);
  border-color: rgba($neon-yellow, 0.4);
}

.badge-compensatory {
  background: rgba($neon-cyan, 0.15);
  border-color: rgba($neon-cyan, 0.4);
}

.badge-text {
  font-size: 24rpx;
  font-weight: 600;
  color: $text-primary;
}

.record-status {
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  border: 1rpx solid;
}

.ls-approved {
  background: rgba($neon-green, 0.12);
  border-color: rgba($neon-green, 0.3);
}

.ls-pending {
  background: rgba($neon-yellow, 0.12);
  border-color: rgba($neon-yellow, 0.3);
}

.ls-rejected {
  background: rgba($neon-pink, 0.12);
  border-color: rgba($neon-pink, 0.3);
}

.ls-text {
  font-size: 22rpx;
}

.ls-approved .ls-text {
  color: $neon-green;
}

.ls-pending .ls-text {
  color: $neon-yellow;
}

.ls-rejected .ls-text {
  color: $neon-pink;
}

.record-dates {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.date-range {
  font-size: 26rpx;
  color: $text-secondary;
}

.date-days {
  font-size: 24rpx;
  color: $neon-purple;
  font-weight: 600;
  background: rgba($neon-purple, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.record-reason {
  font-size: 24rpx;
  color: $text-muted;
  line-height: 1.5;
}
</style>
