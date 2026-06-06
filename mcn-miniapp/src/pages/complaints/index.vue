<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">客户投诉</text>
      <text class="page-subtitle">共 {{ filteredComplaints.length }} 条记录</text>
    </view>

    <scroll-view scroll-x class="filter-tabs">
      <view
        v-for="tab in statusTabs"
        :key="tab.key"
        class="filter-tab"
        :class="{ active: activeStatus === tab.key }"
        @tap="activeStatus = tab.key"
      >
        <text class="filter-tab-text" :class="{ 'active-text': activeStatus === tab.key }">
          {{ tab.label }} ({{ tab.count }})
        </text>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="complaint-list">
      <view
        v-for="item in filteredComplaints"
        :key="item.id"
        class="complaint-card"
        @tap="toggleExpand(item.id)"
      >
        <view class="complaint-top">
          <view class="customer-info">
            <view class="customer-avatar">
              <text class="avatar-letter">{{ item.customerName.charAt(0) }}</text>
            </view>
            <view class="customer-detail">
              <text class="customer-name">{{ item.customerName }}</text>
              <text class="complaint-type">{{ item.type }}</text>
            </view>
          </view>
          <view class="status-tag" :class="'tag-' + item.status">
            <text class="status-tag-text">{{ getStatusText(item.status) }}</text>
          </view>
        </view>

        <text class="complaint-desc">{{ item.description }}</text>

        <view class="complaint-footer">
          <text class="complaint-date">{{ item.date }}</text>
          <text class="complaint-order">订单: {{ item.orderNo }}</text>
        </view>

        <view v-if="expandedId === item.id" class="complaint-detail">
          <view class="detail-divider"></view>
          <view class="detail-row">
            <text class="detail-label">投诉来源</text>
            <text class="detail-value">{{ item.source }}</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">优先级</text>
            <text class="detail-value" :class="'priority-' + item.priority">{{ item.priorityText }}</text>
          </view>
          <view class="detail-row">
            <text class="detail-label">处理人</text>
            <text class="detail-value">{{ item.handler }}</text>
          </view>
          <view v-if="item.reply" class="detail-row">
            <text class="detail-label">处理结果</text>
            <text class="detail-value">{{ item.reply }}</text>
          </view>
          <view v-if="item.status === 'pending'" class="detail-actions">
            <button class="btn-handle" @tap.stop="handleComplaint(item)">立即处理</button>
          </view>
        </view>

        <view class="expand-hint">
          <text class="expand-text">{{ expandedId === item.id ? '收起' : '点击展开详情' }}</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'
import { getStatusText } from '@/utils/format'

const activeStatus = ref('all')
const expandedId = ref(null)

const complaints = ref([
  {
    id: 1,
    customerName: '刘女士',
    type: '商品质量',
    description: '收到的商品与直播间展示不一致，颜色有色差，尺码偏小，要求退货退款...',
    date: '2025-06-05',
    orderNo: 'ORD20250605001',
    status: 'pending',
    source: '直播间评论',
    priority: 'high',
    priorityText: '高优先',
    handler: '未分配',
    reply: '',
  },
  {
    id: 2,
    customerName: '张先生',
    type: '物流问题',
    description: '下单5天仍未发货，多次联系客服未得到有效回复，严重影响购物体验',
    date: '2025-06-04',
    orderNo: 'ORD20250604012',
    status: 'processing',
    source: '售后工单',
    priority: 'medium',
    priorityText: '中优先',
    handler: '李小花',
    reply: '已联系仓库加急发货，预计明天到达',
  },
  {
    id: 3,
    customerName: '王小姐',
    type: '售后服务',
    description: '申请退款已过3个工作日，退款金额未到账，请尽快处理',
    date: '2025-06-03',
    orderNo: 'ORD20250603008',
    status: 'resolved',
    source: '400电话',
    priority: 'low',
    priorityText: '低优先',
    handler: '赵服务',
    reply: '退款已于6月4日到账，已电话回访确认',
  },
  {
    id: 4,
    customerName: '陈先生',
    type: '虚假宣传',
    description: '直播间承诺买一送一，实际收货只有一件，要求补发赠品',
    date: '2025-06-03',
    orderNo: 'ORD20250602015',
    status: 'processing',
    source: '直播间评论',
    priority: 'high',
    priorityText: '高优先',
    handler: '周运营',
    reply: '已核实活动规则，补发赠品中',
  },
  {
    id: 5,
    customerName: '赵女士',
    type: '商品质量',
    description: '商品收到有破损，外包装完好，应是出厂问题，需要换货',
    date: '2025-06-02',
    orderNo: 'ORD20250601022',
    status: 'resolved',
    source: '在线客服',
    priority: 'medium',
    priorityText: '中优先',
    handler: '钱客服',
    reply: '已换货处理，新件已于6月3日寄出',
  },
  {
    id: 6,
    customerName: '孙先生',
    type: '价格问题',
    description: '直播间标价99元，下单显示129元，涉嫌价格欺诈',
    date: '2025-06-01',
    orderNo: 'ORD20250601005',
    status: 'pending',
    source: '12315投诉',
    priority: 'high',
    priorityText: '高优先',
    handler: '未分配',
    reply: '',
  },
])

const statusTabs = computed(() => [
  { key: 'all', label: '全部', count: complaints.value.length },
  {
    key: 'pending',
    label: '待处理',
    count: complaints.value.filter((c) => c.status === 'pending').length,
  },
  {
    key: 'processing',
    label: '处理中',
    count: complaints.value.filter((c) => c.status === 'processing').length,
  },
  {
    key: 'resolved',
    label: '已解决',
    count: complaints.value.filter((c) => c.status === 'resolved').length,
  },
])

const filteredComplaints = computed(() => {
  if (activeStatus.value === 'all') return complaints.value
  return complaints.value.filter((c) => c.status === activeStatus.value)
})

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function handleComplaint(item) {
  uni.showToast({ title: `正在处理 #${item.id}`, icon: 'none' })
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
  margin-bottom: 20rpx;
  padding: 0 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
  display: block;
  margin-bottom: 8rpx;
}

.page-subtitle {
  font-size: 24rpx;
  color: $text-muted;
}

.filter-tabs {
  white-space: nowrap;
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.filter-tab {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 28rpx;
  border-radius: 40rpx;
  background: $bg-card;
  border: 1rpx solid $border-glow;
  margin-right: 16rpx;

  &.active {
    background: rgba($neon-purple, 0.25);
    border-color: $neon-purple;
    box-shadow: 0 0 20rpx rgba($neon-purple, 0.3);
  }
}

.filter-tab-text {
  font-size: 24rpx;
  color: $text-secondary;

  &.active-text {
    color: $text-primary;
    font-weight: 600;
  }
}

.complaint-list {
  height: calc(100vh - 240rpx);
}

.complaint-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 28rpx;
  margin-bottom: 20rpx;
  backdrop-filter: blur(20px);
}

.complaint-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.customer-info {
  display: flex;
  align-items: center;
}

.customer-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba($neon-purple, 0.3), rgba($neon-pink, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.avatar-letter {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.customer-detail {
  display: flex;
  flex-direction: column;
}

.customer-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.complaint-type {
  font-size: 22rpx;
  color: $neon-purple;
  margin-top: 4rpx;
}

.status-tag {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  border: 1rpx solid;
}

.tag-pending {
  background: rgba($neon-yellow, 0.12);
  border-color: rgba($neon-yellow, 0.3);
}

.tag-processing {
  background: rgba($neon-cyan, 0.12);
  border-color: rgba($neon-cyan, 0.3);
}

.tag-resolved {
  background: rgba($neon-green, 0.12);
  border-color: rgba($neon-green, 0.3);
}

.status-tag-text {
  font-size: 22rpx;
  font-weight: 500;
}

.tag-pending .status-tag-text {
  color: $neon-yellow;
}

.tag-processing .status-tag-text {
  color: $neon-cyan;
}

.tag-resolved .status-tag-text {
  color: $neon-green;
}

.complaint-desc {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.complaint-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.complaint-date,
.complaint-order {
  font-size: 22rpx;
  color: $text-muted;
}

.complaint-detail {
  margin-top: 20rpx;
}

.detail-divider {
  height: 1rpx;
  background: $border-glow;
  margin-bottom: 20rpx;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14rpx;
}

.detail-label {
  font-size: 24rpx;
  color: $text-muted;
}

.detail-value {
  font-size: 24rpx;
  color: $text-secondary;
  text-align: right;
  flex: 1;
  margin-left: 20rpx;
}

.priority-high {
  color: $neon-pink;
}

.priority-medium {
  color: $neon-yellow;
}

.priority-low {
  color: $neon-green;
}

.detail-actions {
  margin-top: 20rpx;
}

.btn-handle {
  background: linear-gradient(135deg, $neon-purple, $neon-pink);
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
  border-radius: 12rpx;
  padding: 16rpx;
  text-align: center;
  border: none;
  box-shadow: 0 0 20rpx rgba($neon-purple, 0.3);
}

.expand-hint {
  margin-top: 12rpx;
  text-align: center;
}

.expand-text {
  font-size: 22rpx;
  color: $text-muted;
}
</style>
