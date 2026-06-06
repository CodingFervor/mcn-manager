<template>
  <view class="page">
    <!-- Top Bar -->
    <view class="top-bar">
      <text class="page-title">消息中心</text>
      <view class="read-all-btn" @tap="markAllRead">
        <text class="read-all-text">全部已读</text>
      </view>
    </view>

    <!-- Notification List -->
    <scroll-view scroll-y class="notification-list">
      <view
        v-for="item in notifications"
        :key="item.id"
        :class="['glass-card', 'notification-card', { unread: !item.isRead }]"
        @tap="markRead(item)"
      >
        <view class="card-left">
          <view :class="['icon-circle', `icon-${item.type}`]">
            <text class="icon-text">{{ typeIcon[item.type] }}</text>
          </view>
        </view>
        <view class="card-center">
          <view class="title-row">
            <text class="notif-title">{{ item.title }}</text>
            <view v-if="!item.isRead" class="unread-dot"></view>
          </view>
          <text class="notif-content">{{ item.content }}</text>
          <text class="notif-time">{{ formatDateTime(item.createdAt) }}</text>
        </view>
      </view>

      <view v-if="notifications.length === 0" class="empty-tip">
        <text class="tip-text">暂无消息</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { NotificationAPI } from '@/api'
import { formatDateTime } from '@/utils/format'

const typeIcon = {
  system: '系',
  task: '任',
  stream: '播',
  order: '订',
  finance: '财'
}

const notifications = ref([])

const mockNotifications = [
  { id: 1, type: 'stream', title: '直播即将开始', content: '旗舰店A的直播将在30分钟后开始，请主播和运营团队做好准备', createdAt: '2026-06-06T18:30:00', isRead: false },
  { id: 2, type: 'task', title: '新任务分配', content: '张小明被分配了新任务「准备618直播脚本」，截止日期6月10日', createdAt: '2026-06-06T16:45:00', isRead: false },
  { id: 3, type: 'order', title: '退款申请', content: '订单#202606050023提交了退款申请，商品：玻尿酸精华液，金额¥299', createdAt: '2026-06-06T14:20:00', isRead: false },
  { id: 4, type: 'finance', title: '月度财务报告', content: '5月份财务报告已生成，本月净利润¥86,500，环比增长12.3%', createdAt: '2026-06-06T10:00:00', isRead: false },
  { id: 5, type: 'system', title: '系统维护通知', content: '系统将于今晚22:00-23:00进行例行维护，届时部分功能可能暂时不可用', createdAt: '2026-06-05T09:00:00', isRead: true },
  { id: 6, type: 'stream', title: '直播数据报告', content: '昨日旗舰店A直播已结束，GMV ¥125,800，观看人数3520，峰值1280', createdAt: '2026-06-05T22:30:00', isRead: true },
  { id: 7, type: 'task', title: '任务已完成', content: '「上周直播数据复盘」已由张小明标记为完成', createdAt: '2026-06-05T17:00:00', isRead: true },
  { id: 8, type: 'order', title: '大额订单提醒', content: '旗舰店A收到一笔¥15,800的批量订单，请及时安排发货', createdAt: '2026-06-04T15:30:00', isRead: true },
  { id: 9, type: 'system', title: '新功能上线', content: '销售目标管理功能已上线，可以为每个直播间设定月度GMV目标', createdAt: '2026-06-04T10:00:00', isRead: true },
  { id: 10, type: 'finance', title: '提成结算完成', content: '5月份主播提成已结算完成，总额¥23,400，请相关人员确认', createdAt: '2026-06-03T16:00:00', isRead: true }
]

async function loadData() {
  try {
    const res = await NotificationAPI.list()
    notifications.value = res.data?.results || res.data || mockNotifications
  } catch {
    notifications.value = mockNotifications
  }
}

async function markAllRead() {
  try {
    await NotificationAPI.readAll()
  } catch {
    // ignore
  }
  notifications.value.forEach(n => { n.isRead = true })
  uni.showToast({ title: '已全部标记为已读', icon: 'success' })
}

function markRead(item) {
  if (!item.isRead) {
    item.isRead = true
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

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.read-all-btn {
  padding: 12rpx 28rpx;
  border-radius: $radius-sm;
  background: rgba($neon-purple, 0.15);
  border: 2rpx solid rgba($neon-purple, 0.3);
}

.read-all-text {
  font-size: 24rpx;
  color: $neon-purple;
}

.notification-list {
  padding: 0 32rpx;
  height: calc(100vh - 100rpx);
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.notification-card {
  display: flex;
  padding: 24rpx;
  margin-bottom: 20rpx;

  &.unread {
    background: rgba($neon-purple, 0.08);
    border-color: rgba($neon-purple, 0.35);
  }
}

.card-left {
  margin-right: 20rpx;
  flex-shrink: 0;
}

.icon-circle {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  &.icon-system { background: rgba($neon-cyan, 0.15); }
  &.icon-task { background: rgba($neon-yellow, 0.15); }
  &.icon-stream { background: rgba($neon-purple, 0.15); }
  &.icon-order { background: rgba($neon-green, 0.15); }
  &.icon-finance { background: rgba($neon-pink, 0.15); }
}

.icon-text {
  font-size: 28rpx;
  font-weight: 700;

  .icon-system & { color: $neon-cyan; }
  .icon-task & { color: $neon-yellow; }
  .icon-stream & { color: $neon-purple; }
  .icon-order & { color: $neon-green; }
  .icon-finance & { color: $neon-pink; }
}

.card-center {
  flex: 1;
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 8rpx;
}

.notif-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.unread-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: $neon-pink;
  flex-shrink: 0;
}

.notif-content {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 10rpx;
}

.notif-time {
  font-size: 22rpx;
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
