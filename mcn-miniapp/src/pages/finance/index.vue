<template>
  <view class="page">
    <!-- Summary Cards -->
    <view class="summary-row">
      <view class="glass-card summary-card income">
        <text class="summary-label">本月收入</text>
        <text class="summary-value">{{ formatMoney(summary.income) }}</text>
      </view>
      <view class="glass-card summary-card expense">
        <text class="summary-label">本月支出</text>
        <text class="summary-value">{{ formatMoney(summary.expense) }}</text>
      </view>
    </view>
    <view class="glass-card summary-card profit">
      <view class="profit-row">
        <text class="summary-label">净利润</text>
        <text :class="['summary-value', summary.profit >= 0 ? 'positive' : 'negative']">
          {{ formatMoney(summary.profit) }}
        </text>
      </view>
    </view>

    <!-- Income Chart Placeholder -->
    <view class="glass-card chart-section">
      <text class="section-title">近6个月收入趋势</text>
      <view class="chart-placeholder">
        <view
          v-for="(bar, idx) in monthlyChart"
          :key="idx"
          class="chart-col"
        >
          <text class="chart-value">{{ formatMoney(bar.value).replace('¥', '') }}</text>
          <view class="chart-bar-track">
            <view
              class="chart-bar"
              :style="{ height: bar.height + '%', background: bar.color }"
            ></view>
          </view>
          <text class="chart-label">{{ bar.month }}</text>
        </view>
      </view>
    </view>

    <!-- Recent Transactions -->
    <view class="glass-card tx-section">
      <text class="section-title">最近交易</text>
      <view
        v-for="tx in transactions"
        :key="tx.id"
        class="tx-row"
      >
        <view class="tx-left">
          <view :class="['tx-icon', tx.type]">
            <text class="tx-icon-text">{{ tx.type === 'income' ? '+' : '-' }}</text>
          </view>
          <view class="tx-info">
            <text class="tx-desc">{{ tx.description }}</text>
            <text class="tx-date">{{ formatDateTime(tx.date) }}</text>
          </view>
        </view>
        <text :class="['tx-amount', tx.type]">
          {{ tx.type === 'income' ? '+' : '-' }}{{ formatMoney(tx.amount) }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { FinanceAPI } from '@/api'
import { formatMoney, formatDateTime } from '@/utils/format'

const summary = ref({ income: 0, expense: 0, profit: 0 })
const monthlyChart = ref([])
const transactions = ref([])

const mockSummary = {
  income: 386500,
  expense: 212800,
  profit: 173700
}

const mockChartData = [
  { month: '1月', value: 245000, height: 42, color: 'rgba(124,92,255,0.6)' },
  { month: '2月', value: 312000, height: 54, color: 'rgba(124,92,255,0.65)' },
  { month: '3月', value: 289000, height: 50, color: 'rgba(124,92,255,0.7)' },
  { month: '4月', value: 356000, height: 61, color: 'rgba(0,229,255,0.7)' },
  { month: '5月', value: 425000, height: 73, color: 'rgba(0,229,255,0.8)' },
  { month: '6月', value: 386500, height: 67, color: 'rgba(0,255,157,0.8)' }
]

const mockTransactions = [
  { id: 1, type: 'income', description: '旗舰店A直播收入', amount: 125800, date: '2026-06-05T22:30:00' },
  { id: 2, type: 'income', description: '品牌店B直播收入', amount: 89600, date: '2026-06-04T22:00:00' },
  { id: 3, type: 'expense', description: '618推广广告费', amount: 35000, date: '2026-06-04T10:00:00' },
  { id: 4, type: 'expense', description: '主播提成结算', amount: 23400, date: '2026-06-03T16:00:00' },
  { id: 5, type: 'income', description: '专卖店C直播收入', amount: 67800, date: '2026-06-03T23:00:00' },
  { id: 6, type: 'expense', description: '直播设备采购', amount: 12800, date: '2026-06-02T14:00:00' },
  { id: 7, type: 'income', description: '概念店D直播收入', amount: 45200, date: '2026-06-02T21:30:00' },
  { id: 8, type: 'expense', description: '物流仓储费用', amount: 18600, date: '2026-06-01T09:00:00' },
  { id: 9, type: 'income', description: '旗舰店A直播收入', amount: 156200, date: '2026-06-01T22:00:00' },
  { id: 10, type: 'expense', description: '样品采购', amount: 8200, date: '2026-05-31T11:00:00' }
]

async function loadData() {
  try {
    const res = await FinanceAPI.summary()
    summary.value = res.data || mockSummary
  } catch {
    summary.value = mockSummary
  }
  monthlyChart.value = mockChartData
  try {
    const txRes = await FinanceAPI.list()
    transactions.value = txRes.data?.results || txRes.data || mockTransactions
  } catch {
    transactions.value = mockTransactions
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
  padding: 24rpx 32rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
  padding: 28rpx;
  margin-bottom: 24rpx;
}

.summary-row {
  display: flex;
  gap: 16rpx;
}

.summary-card {
  flex: 1;
  margin-bottom: 16rpx;

  &.income .summary-value {
    color: $neon-green;
  }
  &.expense .summary-value {
    color: $neon-pink;
  }
}

.summary-label {
  font-size: 24rpx;
  color: $text-muted;
  margin-bottom: 8rpx;
  display: block;
}

.summary-value {
  font-size: 34rpx;
  font-weight: 700;

  &.positive { color: $neon-green; }
  &.negative { color: $neon-pink; }
}

.profit-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 24rpx;
  display: block;
}

.chart-section {
  margin-bottom: 24rpx;
}

.chart-placeholder {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 320rpx;
  padding: 0 8rpx;
}

.chart-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
  justify-content: flex-end;
}

.chart-value {
  font-size: 18rpx;
  color: $text-muted;
  margin-bottom: 8rpx;
}

.chart-bar-track {
  width: 70%;
  flex: 1;
  display: flex;
  align-items: flex-end;
}

.chart-bar {
  width: 100%;
  border-radius: 8rpx 8rpx 0 0;
  min-height: 8rpx;
}

.chart-label {
  font-size: 22rpx;
  color: $text-secondary;
  margin-top: 8rpx;
}

.tx-section {
  margin-bottom: 0;
}

.tx-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18rpx 0;
  border-bottom: 2rpx solid rgba(255, 255, 255, 0.04);

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
}

.tx-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.tx-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.income {
    background: rgba($neon-green, 0.15);
  }
  &.expense {
    background: rgba($neon-pink, 0.15);
  }
}

.tx-icon-text {
  font-size: 28rpx;
  font-weight: 700;

  .income & { color: $neon-green; }
  .expense & { color: $neon-pink; }
}

.tx-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
  min-width: 0;
}

.tx-desc {
  font-size: 26rpx;
  color: $text-primary;
}

.tx-date {
  font-size: 22rpx;
  color: $text-muted;
}

.tx-amount {
  font-size: 28rpx;
  font-weight: 600;
  flex-shrink: 0;
  margin-left: 16rpx;

  &.income { color: $neon-green; }
  &.expense { color: $neon-pink; }
}
</style>
