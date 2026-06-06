<template>
  <view class="page">
    <!-- Status Filter Tabs -->
    <view class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-item', { active: activeTab === tab.value }]"
        @tap="activeTab = tab.value"
      >
        <text class="tab-text">{{ tab.label }}</text>
      </view>
    </view>

    <!-- Order List -->
    <scroll-view scroll-y class="order-list">
      <view
        v-for="order in filteredOrders"
        :key="order.id"
        class="glass-card order-card"
      >
        <view class="order-header">
          <text class="order-no">订单号: {{ order.orderNo }}</text>
          <text :class="['status-tag', `status-${order.status}`]">
            {{ statusMap[order.status] }}
          </text>
        </view>
        <view class="order-body">
          <view class="product-row">
            <view class="product-dot"></view>
            <text class="product-name">{{ order.productName }}</text>
          </view>
          <text class="product-qty">x{{ order.quantity }}</text>
        </view>
        <view class="order-footer">
          <text class="order-date">{{ formatDate(order.createdAt) }}</text>
          <text class="order-amount">{{ formatMoney(order.amount) }}</text>
        </view>
      </view>

      <view v-if="filteredOrders.length === 0" class="empty-tip">
        <text class="tip-text">暂无订单</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { OrderAPI } from '@/api'
import { formatMoney, formatDate } from '@/utils/format'

const tabs = [
  { label: '全部', value: 'all' },
  { label: '待发货', value: 'pending' },
  { label: '已完成', value: 'completed' },
  { label: '退款', value: 'refunded' }
]

const statusMap = {
  pending: '待发货',
  shipped: '已发货',
  completed: '已完成',
  refunded: '已退款',
  cancelled: '已取消'
}

const activeTab = ref('all')
const orders = ref([])

const mockOrders = [
  { id: 1, orderNo: '202606060001', productName: '玻尿酸精华液30ml', quantity: 2, amount: 598, status: 'pending', createdAt: '2026-06-06T14:30:00' },
  { id: 2, orderNo: '202606060002', productName: '护肤四件套礼盒', quantity: 1, amount: 699, status: 'pending', createdAt: '2026-06-06T13:20:00' },
  { id: 3, orderNo: '202606060003', productName: '丝绒雾面唇釉 x3', quantity: 3, amount: 384, status: 'pending', createdAt: '2026-06-06T11:45:00' },
  { id: 4, orderNo: '202606050010', productName: '烟酰胺美白面霜50g', quantity: 1, amount: 300, status: 'shipped', createdAt: '2026-06-05T16:00:00' },
  { id: 5, orderNo: '202606050008', productName: '化妆刷套装12支', quantity: 1, amount: 168, status: 'completed', createdAt: '2026-06-05T10:30:00' },
  { id: 6, orderNo: '202606050005', productName: '氨基酸洁面乳120ml', quantity: 2, amount: 200, status: 'completed', createdAt: '2026-06-05T09:15:00' },
  { id: 7, orderNo: '202606040012', productName: '电动洁面仪', quantity: 1, amount: 399, status: 'completed', createdAt: '2026-06-04T14:20:00' },
  { id: 8, orderNo: '202606040009', productName: '12色眼影盘大地色', quantity: 1, amount: 198, status: 'completed', createdAt: '2026-06-04T11:00:00' },
  { id: 9, orderNo: '202606030007', productName: '防晒喷雾SPF50+', quantity: 2, amount: 490, status: 'refunded', createdAt: '2026-06-03T16:45:00' },
  { id: 10, orderNo: '202606020003', productName: '美妆蛋3枚装', quantity: 5, amount: 195, status: 'refunded', createdAt: '2026-06-02T10:30:00' }
]

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders.value
  return orders.value.filter(o => o.status === activeTab.value)
})

async function loadData() {
  try {
    const res = await OrderAPI.list()
    orders.value = res.data?.results || res.data || mockOrders
  } catch {
    orders.value = mockOrders
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

.filter-tabs {
  display: flex;
  padding: 24rpx 32rpx;
  gap: 16rpx;
}

.tab-item {
  padding: 16rpx 32rpx;
  border-radius: $radius-sm;
  background: $bg-secondary;
  border: 2rpx solid transparent;

  &.active {
    background: rgba($neon-purple, 0.15);
    border-color: $neon-purple;
  }
}

.tab-text {
  font-size: 28rpx;
  color: $text-secondary;

  .active & {
    color: $neon-purple;
    font-weight: 600;
  }
}

.order-list {
  padding: 0 32rpx;
  height: calc(100vh - 120rpx);
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.order-card {
  padding: 24rpx 28rpx;
  margin-bottom: 20rpx;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.order-no {
  font-size: 24rpx;
  color: $text-muted;
}

.status-tag {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.status-pending {
    background: rgba($neon-yellow, 0.15);
    color: $neon-yellow;
  }
  &.status-shipped {
    background: rgba($neon-cyan, 0.15);
    color: $neon-cyan;
  }
  &.status-completed {
    background: rgba($neon-green, 0.15);
    color: $neon-green;
  }
  &.status-refunded {
    background: rgba($neon-pink, 0.15);
    color: $neon-pink;
  }
  &.status-cancelled {
    background: rgba($text-muted, 0.15);
    color: $text-muted;
  }
}

.order-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.product-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.product-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: $neon-purple;
}

.product-name {
  font-size: 28rpx;
  color: $text-primary;
}

.product-qty {
  font-size: 26rpx;
  color: $text-muted;
  margin-left: 16rpx;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16rpx;
  border-top: 2rpx solid rgba(255, 255, 255, 0.04);
}

.order-date {
  font-size: 24rpx;
  color: $text-muted;
}

.order-amount {
  font-size: 32rpx;
  font-weight: 700;
  color: $neon-pink;
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
