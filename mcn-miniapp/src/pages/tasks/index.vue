<template>
  <view class="page">
    <!-- Tab Filter -->
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

    <!-- Task List -->
    <scroll-view scroll-y class="task-list">
      <view
        v-for="task in filteredTasks"
        :key="task.id"
        class="glass-card task-card"
      >
        <view class="card-top">
          <text class="task-title">{{ task.title }}</text>
          <text :class="['priority-tag', `priority-${task.priority}`]">
            {{ priorityMap[task.priority] }}
          </text>
        </view>
        <text class="task-desc">{{ task.description }}</text>
        <view class="card-footer">
          <view class="footer-left">
            <view class="avatar-circle">
              <text class="avatar-text">{{ task.assignee.charAt(0) }}</text>
            </view>
            <text class="assignee-name">{{ task.assignee }}</text>
          </view>
          <text class="due-date">{{ formatDate(task.dueDate) }}</text>
        </view>
        <view class="status-row">
          <view
            v-for="s in statusList"
            :key="s.value"
            :class="['status-step', { active: task.status === s.value, done: getStepIndex(task.status) > getStepIndex(s.value) }]"
          >
            <view class="step-dot"></view>
            <text class="step-label">{{ s.label }}</text>
          </view>
        </view>
      </view>

      <view v-if="filteredTasks.length === 0" class="empty-tip">
        <text class="tip-text">暂无任务</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { TaskAPI } from '@/api'
import { formatDate } from '@/utils/format'

const tabs = [
  { label: '待办', value: 'pending' },
  { label: '进行中', value: 'ongoing' },
  { label: '已完成', value: 'completed' }
]
const statusList = [
  { label: '待办', value: 'pending' },
  { label: '进行中', value: 'ongoing' },
  { label: '已完成', value: 'completed' }
]
const priorityMap = { high: '高', medium: '中', low: '低' }
const activeTab = ref('pending')
const tasks = ref([])

const mockTasks = [
  { id: 1, title: '准备618直播脚本', description: '编写旗舰店618大促直播脚本，包含产品介绍、互动环节、优惠说明', priority: 'high', dueDate: '2026-06-10', assignee: '张小明', status: 'pending' },
  { id: 2, title: '选品上架审核', description: '审核本周新品上架清单，确认价格、库存、详情页信息', priority: 'high', dueDate: '2026-06-08', assignee: '李思思', status: 'pending' },
  { id: 3, title: '直播间背景布置', description: '618主题背景板制作与安装，灯光调试', priority: 'medium', dueDate: '2026-06-12', assignee: '王大伟', status: 'ongoing' },
  { id: 4, title: '粉丝群预热通知', description: '编辑618活动预告，在粉丝群和朋友圈提前预热', priority: 'medium', dueDate: '2026-06-09', assignee: '赵丽丽', status: 'ongoing' },
  { id: 5, title: '上周直播数据复盘', description: '整理上周三场直播的GMV、转化率、观众数据并提交报告', priority: 'low', dueDate: '2026-06-07', assignee: '张小明', status: 'completed' },
  { id: 6, title: '样品清点与归还', description: '清点上月直播用样品，联系供应商归还或购买', priority: 'low', dueDate: '2026-06-06', assignee: '李思思', status: 'completed' }
]

const filteredTasks = computed(() => {
  return tasks.value.filter(t => t.status === activeTab.value)
})

function getStepIndex(status) {
  const order = ['pending', 'ongoing', 'completed']
  return order.indexOf(status)
}

async function loadData() {
  try {
    const res = await TaskAPI.list({ status: activeTab.value })
    tasks.value = res.data?.results || res.data || mockTasks
  } catch {
    tasks.value = mockTasks
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
  gap: 20rpx;
}

.tab-item {
  padding: 16rpx 40rpx;
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

.task-list {
  padding: 0 32rpx;
  height: calc(100vh - 120rpx);
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.task-card {
  margin-bottom: 24rpx;
  padding: 28rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12rpx;
}

.task-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
  margin-right: 16rpx;
}

.priority-tag {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.priority-high {
    background: rgba($neon-pink, 0.15);
    color: $neon-pink;
  }
  &.priority-medium {
    background: rgba($neon-yellow, 0.15);
    color: $neon-yellow;
  }
  &.priority-low {
    background: rgba($neon-cyan, 0.15);
    color: $neon-cyan;
  }
}

.task-desc {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.5;
  margin-bottom: 20rpx;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.avatar-circle {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba($neon-purple, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 22rpx;
  color: $neon-purple;
  font-weight: 600;
}

.assignee-name {
  font-size: 26rpx;
  color: $text-secondary;
}

.due-date {
  font-size: 24rpx;
  color: $text-muted;
}

.status-row {
  display: flex;
  justify-content: space-between;
  padding-top: 20rpx;
  border-top: 2rpx solid rgba(255, 255, 255, 0.05);
}

.status-step {
  display: flex;
  align-items: center;
  gap: 8rpx;

  &.active .step-dot {
    background: $neon-cyan;
    box-shadow: 0 0 12rpx $neon-cyan;
  }
  &.active .step-label {
    color: $neon-cyan;
  }
  &.done .step-dot {
    background: $neon-green;
  }
  &.done .step-label {
    color: $neon-green;
  }
}

.step-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: $text-muted;
}

.step-label {
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
