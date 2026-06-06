<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">费用报销</text>
    </view>

    <!-- New Expense Form -->
    <view class="glass-card form-card">
      <view class="card-header">
        <text class="card-title">新建报销</text>
        <view class="card-underline"></view>
      </view>

      <view class="form-body">
        <view class="form-item">
          <text class="form-label">费用类型</text>
          <picker :range="expenseTypes" @change="onTypeChange">
            <view class="form-picker">
              <text class="picker-text" :class="{ placeholder: !form.type }">
                {{ form.type || '请选择费用类型' }}
              </text>
              <text class="picker-arrow">&#xe6e1;</text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">报销金额</text>
          <view class="input-wrapper">
            <text class="input-prefix">¥</text>
            <input
              v-model="form.amount"
              type="digit"
              placeholder="请输入金额"
              placeholder-class="placeholder"
              class="form-input amount-input"
            />
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">费用日期</text>
          <picker mode="date" @change="onDateChange">
            <view class="form-picker">
              <text class="picker-text" :class="{ placeholder: !form.date }">
                {{ form.date || '请选择日期' }}
              </text>
              <text class="picker-arrow">&#xe6e1;</text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">费用说明</text>
          <textarea
            v-model="form.description"
            placeholder="请简要描述费用用途"
            placeholder-class="placeholder"
            class="form-textarea"
            :maxlength="200"
          />
        </view>

        <button class="btn-submit" @tap="submitExpense">提交报销</button>
      </view>
    </view>

    <!-- Expense Records -->
    <view class="section-header">
      <text class="section-title">报销记录</text>
      <text class="section-count">{{ records.length }} 条</text>
    </view>

    <scroll-view scroll-y class="record-list">
      <view
        v-for="item in records"
        :key="item.id"
        class="record-card"
      >
        <view class="record-left">
          <view class="record-type-icon" :class="'icon-' + item.typeKey">
            <text class="type-icon-text">{{ item.typeIcon }}</text>
          </view>
          <view class="record-info">
            <text class="record-type">{{ item.type }}</text>
            <text class="record-desc">{{ item.description }}</text>
            <text class="record-date">{{ item.date }}</text>
          </view>
        </view>
        <view class="record-right">
          <text class="record-amount">¥{{ item.amount }}</text>
          <view class="record-status" :class="'rs-' + item.status">
            <text class="rs-text">{{ getStatusText(item.status) }}</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { getStatusText } from '@/utils/format'

const expenseTypes = ['交通', '餐饮', '办公', '其他']

const form = ref({
  type: '',
  amount: '',
  date: '',
  description: '',
})

const records = ref([
  {
    id: 1,
    type: '交通',
    typeKey: 'transport',
    typeIcon: 'T',
    amount: '356.00',
    date: '2025-06-04',
    description: '出差杭州-上海往返高铁',
    status: 'approved',
  },
  {
    id: 2,
    type: '餐饮',
    typeKey: 'food',
    typeIcon: 'F',
    amount: '268.00',
    date: '2025-06-03',
    description: '客户接待用餐',
    status: 'pending',
  },
  {
    id: 3,
    type: '办公',
    typeKey: 'office',
    typeIcon: 'O',
    amount: '89.50',
    date: '2025-06-02',
    description: '打印直播脚本及培训材料',
    status: 'approved',
  },
  {
    id: 4,
    type: '交通',
    typeKey: 'transport',
    typeIcon: 'T',
    amount: '120.00',
    date: '2025-06-01',
    description: '去仓库选品打车费用',
    status: 'rejected',
  },
  {
    id: 5,
    type: '餐饮',
    typeKey: 'food',
    typeIcon: 'F',
    amount: '456.00',
    date: '2025-05-30',
    description: '团队聚餐费用（AA制报销部分）',
    status: 'approved',
  },
  {
    id: 6,
    type: '其他',
    typeKey: 'other',
    typeIcon: 'E',
    amount: '200.00',
    date: '2025-05-28',
    description: '直播间道具采购',
    status: 'approved',
  },
])

function onTypeChange(e) {
  form.value.type = expenseTypes[e.detail.value]
}

function onDateChange(e) {
  form.value.date = e.detail.value
}

function submitExpense() {
  const f = form.value
  if (!f.type) return uni.showToast({ title: '请选择费用类型', icon: 'none' })
  if (!f.amount || Number(f.amount) <= 0) return uni.showToast({ title: '请输入金额', icon: 'none' })
  if (!f.date) return uni.showToast({ title: '请选择日期', icon: 'none' })
  if (!f.description) return uni.showToast({ title: '请填写说明', icon: 'none' })

  const typeKeyMap = { '交通': 'transport', '餐饮': 'food', '办公': 'office', '其他': 'other' }
  const typeIconMap = { '交通': 'T', '餐饮': 'F', '办公': 'O', '其他': 'E' }

  records.value.unshift({
    id: Date.now(),
    type: f.type,
    typeKey: typeKeyMap[f.type],
    typeIcon: typeIconMap[f.type],
    amount: Number(f.amount).toFixed(2),
    date: f.date,
    description: f.description,
    status: 'pending',
  })

  form.value = { type: '', amount: '', date: '', description: '' }
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

.input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1rpx solid $border-glow;
  border-radius: $radius-sm;
  padding: 0 24rpx;
}

.input-prefix {
  font-size: 32rpx;
  font-weight: 700;
  color: $neon-purple;
  margin-right: 12rpx;
}

.form-input {
  flex: 1;
  height: 72rpx;
  font-size: 28rpx;
  color: $text-primary;
}

.amount-input {
  font-size: 32rpx;
  font-weight: 600;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 24rpx;
  margin-bottom: 16rpx;
  backdrop-filter: blur(20px);
}

.record-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.record-type-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.icon-transport {
  background: rgba($neon-cyan, 0.2);
  border: 1rpx solid rgba($neon-cyan, 0.3);
}

.icon-food {
  background: rgba($neon-yellow, 0.2);
  border: 1rpx solid rgba($neon-yellow, 0.3);
}

.icon-office {
  background: rgba($neon-purple, 0.2);
  border: 1rpx solid rgba($neon-purple, 0.3);
}

.icon-other {
  background: rgba($neon-green, 0.2);
  border: 1rpx solid rgba($neon-green, 0.3);
}

.type-icon-text {
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.record-info {
  flex: 1;
  min-width: 0;
}

.record-type {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.record-desc {
  font-size: 22rpx;
  color: $text-secondary;
  display: block;
  margin-top: 4rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-date {
  font-size: 20rpx;
  color: $text-muted;
  display: block;
  margin-top: 4rpx;
}

.record-right {
  text-align: right;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.record-amount {
  font-size: 30rpx;
  font-weight: 700;
  color: $neon-pink;
  display: block;
  margin-bottom: 8rpx;
}

.record-status {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1rpx solid;
  display: inline-block;
}

.rs-approved {
  background: rgba($neon-green, 0.12);
  border-color: rgba($neon-green, 0.3);
}

.rs-pending {
  background: rgba($neon-yellow, 0.12);
  border-color: rgba($neon-yellow, 0.3);
}

.rs-rejected {
  background: rgba($neon-pink, 0.12);
  border-color: rgba($neon-pink, 0.3);
}

.rs-text {
  font-size: 20rpx;
}

.rs-approved .rs-text {
  color: $neon-green;
}

.rs-pending .rs-text {
  color: $neon-yellow;
}

.rs-rejected .rs-text {
  color: $neon-pink;
}
</style>
