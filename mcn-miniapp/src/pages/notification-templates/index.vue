<template>
  <view class="page">
    <view class="header">
      <text class="title">通知模板</text>
    </view>
    <view class="filter-bar">
      <view
        class="filter-item"
        v-for="(f, i) in channelFilters"
        :key="i"
        :class="{ active: activeChannel === f.value }"
        @tap="activeChannel = f.value"
      >
        <text class="filter-text">{{ f.label }}</text>
      </view>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in filteredTemplates" :key="idx">
        <view class="card-top">
          <view class="channel-icon" :class="'ch-' + item.channel">
            <text class="ch-icon-text">{{ item.channelIcon }}</text>
          </view>
          <view class="card-info">
            <text class="card-name">{{ item.name }}</text>
            <text class="card-subject">{{ item.subject }}</text>
          </view>
        </view>
        <view class="card-bottom">
          <view class="channel-tag" :class="'tag-' + item.channel">
            <text class="channel-tag-text">{{ item.channelLabel }}</text>
          </view>
          <text class="card-update">{{ item.updatedAt }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

const activeChannel = ref('all')

const channelFilters = [
  { label: '全部', value: 'all' },
  { label: '\u{1F4E7} 邮件', value: 'email' },
  { label: '\u{1F4F1} 短信', value: 'sms' },
  { label: '\u{1F4AC} 微信', value: 'wechat' },
]

const templates = ref([
  { name: '订单确认通知', channel: 'email', channelLabel: '邮件', channelIcon: '\u{1F4E7}', subject: '您的订单已确认 - {{order_no}}', updatedAt: '06-05 更新' },
  { name: '发货提醒', channel: 'sms', channelLabel: '短信', channelIcon: '\u{1F4F1}', subject: '您的包裹已发货，快递单号：{{tracking_no}}', updatedAt: '06-04 更新' },
  { name: '账户安全告警', channel: 'wechat', channelLabel: '微信', channelIcon: '\u{1F4AC}', subject: '检测到异地登录，请确认是否本人操作', updatedAt: '06-03 更新' },
  { name: '密码重置', channel: 'email', channelLabel: '邮件', channelIcon: '\u{1F4E7}', subject: '密码重置验证码：{{code}}', updatedAt: '06-02 更新' },
  { name: '活动邀请', channel: 'wechat', channelLabel: '微信', channelIcon: '\u{1F4AC}', subject: '邀请您参加 {{event_name}} 活动', updatedAt: '06-01 更新' },
  { name: '验证码', channel: 'sms', channelLabel: '短信', channelIcon: '\u{1F4F1}', subject: '您的验证码为 {{code}}，5分钟内有效', updatedAt: '05-30 更新' },
  { name: '月度报表', channel: 'email', channelLabel: '邮件', channelIcon: '\u{1F4E7}', subject: '{{month}} 月度数据报表已生成', updatedAt: '05-28 更新' },
  { name: '直播开播提醒', channel: 'wechat', channelLabel: '微信', channelIcon: '\u{1F4AC}', subject: '您关注的直播间即将开播', updatedAt: '05-27 更新' },
])

const filteredTemplates = computed(() => {
  if (activeChannel.value === 'all') return templates.value
  return templates.value.filter(t => t.channel === activeChannel.value)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 24rpx 32rpx 16rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.filter-bar {
  display: flex;
  padding: 0 24rpx 16rpx;
  gap: 12rpx;
}

.filter-item {
  padding: 8rpx 20rpx;
  border-radius: 32rpx;
  background: rgba(124, 92, 255, 0.08);
  border: 1rpx solid rgba(124, 92, 255, 0.12);

  &.active {
    background: rgba(124, 92, 255, 0.2);
    border-color: $neon-purple;
  }
}

.filter-text {
  font-size: 22rpx;
  color: $text-secondary;
  .active & { color: $neon-purple; font-weight: 600; }
}

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.card-top {
  display: flex;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.channel-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: $radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.ch-email { background: rgba(0, 229, 255, 0.12); }
  &.ch-sms { background: rgba(0, 255, 157, 0.12); }
  &.ch-wechat { background: rgba(124, 92, 255, 0.12); }
}

.ch-icon-text {
  font-size: 32rpx;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 6rpx;
}

.card-subject {
  font-size: 22rpx;
  color: $text-muted;
  lines: 1;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.tag-email { background: rgba(0, 229, 255, 0.12); }
  &.tag-sms { background: rgba(0, 255, 157, 0.12); }
  &.tag-wechat { background: rgba(124, 92, 255, 0.12); }
}

.channel-tag-text {
  font-size: 20rpx;
  font-weight: 500;
  .tag-email & { color: $neon-cyan; }
  .tag-sms & { color: $neon-green; }
  .tag-wechat & { color: $neon-purple; }
}

.card-update {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
