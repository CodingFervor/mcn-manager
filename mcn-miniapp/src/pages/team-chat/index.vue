<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">团队沟通</text>
      <text class="page-subtitle">共 {{ channels.length }} 个频道</text>
    </view>

    <scroll-view scroll-y class="channel-list">
      <view
        v-for="item in channels"
        :key="item.id"
        class="channel-card"
        @tap="openChannel(item)"
      >
        <view class="channel-avatar" :class="item.isGroup ? 'avatar-group' : 'avatar-direct'">
          <text class="avatar-icon">{{ item.isGroup ? '#' : '@' }}</text>
        </view>
        <view class="channel-info">
          <view class="channel-top">
            <text class="channel-name">{{ item.name }}</text>
            <text class="channel-time">{{ item.lastTime }}</text>
          </view>
          <view class="channel-bottom">
            <text class="channel-preview">{{ item.lastMessage }}</text>
            <view v-if="item.unread > 0" class="unread-badge">
              <text class="unread-text">{{ item.unread > 99 ? '99+' : item.unread }}</text>
            </view>
          </view>
        </view>
        <view v-if="item.isGroup" class="channel-tag">
          <text class="tag-text">群组</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'

const channels = ref([
  {
    id: 1,
    name: '全员公告',
    lastMessage: '[主管] 明天下午3点全员会议，请准时参加',
    lastTime: '14:30',
    unread: 3,
    isGroup: true,
  },
  {
    id: 2,
    name: '直播间运营组',
    lastMessage: '小美: 今晚8点直播，大家准备好了吗？',
    lastTime: '13:15',
    unread: 12,
    isGroup: true,
  },
  {
    id: 3,
    name: '选品讨论',
    lastMessage: '[文件] 新品清单-6月.xlsx',
    lastTime: '12:08',
    unread: 0,
    isGroup: true,
  },
  {
    id: 4,
    name: '张经理',
    lastMessage: '绩效报告已经发到你邮箱了，注意查收',
    lastTime: '11:42',
    unread: 1,
    isGroup: false,
  },
  {
    id: 5,
    name: '客服售后组',
    lastMessage: '客户投诉处理进度更新，已解决23件',
    lastTime: '10:30',
    unread: 5,
    isGroup: true,
  },
  {
    id: 6,
    name: '李小龙',
    lastMessage: '好的，下午我把脚本发给你',
    lastTime: '09:55',
    unread: 0,
    isGroup: false,
  },
  {
    id: 7,
    name: '技术支持',
    lastMessage: '系统维护通知：今晚22:00-23:00',
    lastTime: '昨天',
    unread: 0,
    isGroup: true,
  },
  {
    id: 8,
    name: '王小花',
    lastMessage: '场地已经预定好了，明天上午10点',
    lastTime: '昨天',
    unread: 2,
    isGroup: false,
  },
  {
    id: 9,
    name: '新人培训群',
    lastMessage: '培训视频已上传，请本周内完成学习',
    lastTime: '周一',
    unread: 0,
    isGroup: true,
  },
  {
    id: 10,
    name: '赵运营',
    lastMessage: '数据报表你看一下，GMV环比增长15%',
    lastTime: '周一',
    unread: 0,
    isGroup: false,
  },
])

function openChannel(item) {
  uni.showToast({ title: `打开 ${item.name}`, icon: 'none' })
}

onPullDownRefresh(() => {
  setTimeout(() => {
    uni.stopPullDownRefresh()
    uni.showToast({ title: '已刷新', icon: 'none' })
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
  display: block;
  margin-bottom: 8rpx;
}

.page-subtitle {
  font-size: 24rpx;
  color: $text-muted;
}

.channel-list {
  height: calc(100vh - 140rpx);
}

.channel-card {
  display: flex;
  align-items: center;
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 24rpx;
  margin-bottom: 16rpx;
  backdrop-filter: blur(20px);
  transition: border-color 0.3s;

  &:active {
    border-color: rgba($neon-purple, 0.6);
  }
}

.channel-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  flex-shrink: 0;
}

.avatar-group {
  background: linear-gradient(135deg, rgba($neon-purple, 0.3), rgba($neon-pink, 0.3));
  border: 1rpx solid rgba($neon-purple, 0.4);
}

.avatar-direct {
  background: linear-gradient(135deg, rgba($neon-cyan, 0.3), rgba($neon-green, 0.3));
  border: 1rpx solid rgba($neon-cyan, 0.4);
}

.avatar-icon {
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

.channel-info {
  flex: 1;
  min-width: 0;
}

.channel-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.channel-name {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  flex-shrink: 0;
}

.channel-time {
  font-size: 22rpx;
  color: $text-muted;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.channel-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.channel-preview {
  font-size: 24rpx;
  color: $text-secondary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 16rpx;
}

.unread-badge {
  background: $neon-pink;
  border-radius: 20rpx;
  min-width: 36rpx;
  height: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10rpx;
  flex-shrink: 0;
  box-shadow: 0 0 12rpx rgba($neon-pink, 0.5);
}

.unread-text {
  font-size: 20rpx;
  font-weight: 700;
  color: #fff;
}

.channel-tag {
  margin-left: 12rpx;
  flex-shrink: 0;
}

.tag-text {
  font-size: 20rpx;
  color: $neon-purple;
  background: rgba($neon-purple, 0.15);
  border: 1rpx solid rgba($neon-purple, 0.3);
  border-radius: 8rpx;
  padding: 4rpx 12rpx;
}
</style>
